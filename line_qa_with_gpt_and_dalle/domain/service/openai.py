import secrets
from abc import ABC, abstractmethod
from io import BytesIO
from pathlib import Path

import requests.exceptions
from PIL import Image
from openai import OpenAI
from openai.types.chat import (
    ChatCompletion,
)

from config.settings import STATIC_ROOT
from line_qa_with_gpt_and_dalle.domain.repository.chatlogs import (
    ChatLogsRepository,
)
from line_qa_with_gpt_and_dalle.domain.valueobject.chat import MyChatCompletionMessage
from line_qa_with_gpt_and_dalle.domain.valueobject.gender import Gender


class ModelService(ABC):
    def __init__(self, client: OpenAI):
        self.chatlogs_repository = ChatLogsRepository()
        self.client = client

    @abstractmethod
    def generate(self, **kwargs):
        pass

    @abstractmethod
    def post_to_gpt(self, **kwargs):
        pass

    @abstractmethod
    def save(self, **kwargs):
        pass


class ModelGptService(ModelService):
    def generate(
        self, my_chat_completion_message: MyChatCompletionMessage, gender: str
    ) -> list[MyChatCompletionMessage]:
        if my_chat_completion_message.content is None:
            raise Exception("content is None")

        chat_history = self.get_chat_history(
            my_chat_completion_message.user_id, Gender(gender)
        )

        # 初回はユーザのボタン押下などのトリガーで「プロンプト」と「なぞなぞスタート」の2行がinsertされる
        # 会話が始まっているならユーザの入力したチャットをinsertしてからChatGPTに全投げする
        # つまり、3以上あれば会話が始まっているだろうとみなせる
        if len(chat_history) > 2:
            chat_history.append(
                self.save(
                    MyChatCompletionMessage(
                        user_id=my_chat_completion_message.user_id,
                        role=my_chat_completion_message.role,
                        content=my_chat_completion_message.content,
                        invisible=False,
                    )
                )
            )
        response = self.post_to_gpt(chat_history)

        latest_assistant = MyChatCompletionMessage(
            user_id=my_chat_completion_message.user_id,
            role=response.choices[0].message.role,
            content=response.choices[0].message.content,
            invisible=False,
        )
        chat_history.append(self.save(latest_assistant))

        if "本日はなぞなぞにご参加いただき" in latest_assistant.content:
            chat_history.append(
                self.save(
                    MyChatCompletionMessage(
                        user_id=latest_assistant.user_id,
                        role="user",
                        content="評価結果をjsonで出力してください",
                        invisible=True,
                    )
                )
            )
            response = self.post_to_gpt(chat_history)

            latest_assistant = MyChatCompletionMessage(
                user_id=my_chat_completion_message.user_id,
                role=response.choices[0].message.role,
                content=response.choices[0].message.content,
                invisible=True,
            )
            chat_history.append(self.save(latest_assistant))

        return chat_history

    def post_to_gpt(
        self, chat_history: list[MyChatCompletionMessage]
    ) -> ChatCompletion:
        return self.client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[x.to_origin() for x in chat_history],
            temperature=0.5,
        )

    def save(
        self, messages: MyChatCompletionMessage | list[MyChatCompletionMessage]
    ) -> MyChatCompletionMessage | list[MyChatCompletionMessage]:
        if isinstance(messages, list):
            self.chatlogs_repository.bulk_insert(messages)
        elif isinstance(messages, MyChatCompletionMessage):
            self.chatlogs_repository.insert(messages)
        else:
            raise ValueError(
                f"Unexpected type {type(messages)}. Expected MyChatCompletionMessage or list[MyChatCompletionMessage]."
            )

        return messages

    def get_chat_history(
        self, user_id: int, gender: Gender
    ) -> list[MyChatCompletionMessage]:
        chatlogs_list = self.chatlogs_repository.find_chatlogs_by_user_id(user_id)

        if chatlogs_list:
            history = [
                MyChatCompletionMessage(
                    pk=chatlogs.pk,
                    user_id=int(chatlogs.user_id),
                    role=chatlogs.role,
                    content=chatlogs.content,
                    invisible=False,
                    file_path=chatlogs.file_path,
                )
                for chatlogs in chatlogs_list
            ]
        else:
            history = [
                MyChatCompletionMessage(
                    user_id=user_id,
                    role="system",
                    content=self.get_prompt(gender),
                    invisible=True,
                ),
                MyChatCompletionMessage(
                    user_id=user_id,
                    role="user",
                    content="なぞなぞスタート",
                    invisible=False,
                ),
            ]
            self.save(history)

        return history

    @staticmethod
    def get_prompt(gender: Gender) -> str:
        return f"""
            あなたはなぞなぞコーナーの担当者です。
            
            #制約条件
            - 「なぞなぞスタート」と言われたら質問に移る前に、あいさつをします
            - 質問1のあとに質問2を行う。質問2が終わったら、感想を述べるとともに「本日はなぞなぞにご参加いただき、ありがとうございました。」と言って終わりましょう。判定結果は出力してはいけません
            - 質問1は「論理的思考力」評価します
            - 質問2は「洞察力」を評価します
            - scoreが70を超えたら、judgeが「合格」になる
            - {gender.name} の口調で会話を行う
            - 「評価結果をjsonで出力してください」と入力されたら、判定結果例のように判定結果を出力する
            
            #質問1
            - はじめは4本足、途中から2本足、最後は3本足。それは何でしょう？
            
            #質問2
            - 私は黒い服を着て、赤い手袋を持っている。夜には立っているが、朝になると寝る。何でしょう？
            
            #判定結果例
            [{{"skill": "論理的思考力", "score": 50, "judge": "不合格"}},{{"skill": "洞察力", "score": 96, "judge": "合格"}}]
        """


class ModelDalleService(ModelService):
    def generate(self, my_chat_completion_message: MyChatCompletionMessage):
        """
        画像urlの有効期限は1時間。それ以上使いたいときは保存する。
        dall-e-3: 1024x1024, 1792x1024, 1024x1792 のいずれかしか生成できない
        """
        if my_chat_completion_message.content is None:
            raise Exception("content is None")
        response = self.post_to_gpt(my_chat_completion_message.content)
        image_url = response.data[0].url
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            resized_picture = self.resize(picture=Image.open(BytesIO(response.content)))
            my_chat_completion_message = self.save(
                resized_picture,
                my_chat_completion_message,
            )
        except requests.exceptions.HTTPError as http_error:
            raise Exception(http_error)
        except requests.exceptions.ConnectionError as connection_error:
            raise Exception(connection_error)
        except Exception as e:
            raise Exception(e)

        return my_chat_completion_message

    def post_to_gpt(self, prompt: str):
        return self.client.images.generate(
            model="dall-e-3", prompt=prompt, size="1024x1024", quality="standard", n=1
        )

    def save(
        self, picture: Image, my_chat_completion_message: MyChatCompletionMessage
    ) -> MyChatCompletionMessage:
        folder_path = Path(STATIC_ROOT) / "images"
        if not folder_path.exists():
            folder_path.mkdir(parents=True, exist_ok=True)
        # This generates a random string of 10 characters
        random_filename = secrets.token_hex(5) + ".jpg"
        relative_path_str = "images/" + random_filename
        full_path = folder_path / random_filename
        my_chat_completion_message.file_path = relative_path_str
        picture.save(full_path)
        self.chatlogs_repository.upsert(my_chat_completion_message)

        return my_chat_completion_message

    @staticmethod
    def resize(picture: Image) -> Image:
        return picture.resize((512, 512))


class ModelTextToSpeechService(ModelService):
    def generate(self, my_chat_completion_message: MyChatCompletionMessage):
        if my_chat_completion_message.content is None:
            raise Exception("content is None")
        response = self.post_to_gpt(my_chat_completion_message.content)
        self.save(response, my_chat_completion_message)

    def post_to_gpt(self, text: str):
        return self.client.audio.speech.create(
            model="tts-1", voice="alloy", input=text, response_format="mp3"
        )

    def save(self, response, my_chat_completion_message: MyChatCompletionMessage):
        folder_path = Path(STATIC_ROOT) / "audios"
        if not folder_path.exists():
            folder_path.mkdir(parents=True, exist_ok=True)
        # This generates a random string of 10 characters
        random_filename = secrets.token_hex(5) + ".mp3"
        relative_path_str = "audios/" + random_filename
        full_path = folder_path / random_filename
        my_chat_completion_message.file_path = relative_path_str
        response.write_to_file(full_path)
        self.chatlogs_repository.upsert(my_chat_completion_message)

        return my_chat_completion_message


class ModelSpeechToTextService(ModelService):
    def generate(self, my_chat_completion_message: MyChatCompletionMessage):
        if my_chat_completion_message.file_path is None:
            raise Exception("file_path is None")
        full_path = Path(STATIC_ROOT) / my_chat_completion_message.file_path
        if full_path.exists():
            response = self.post_to_gpt(str(full_path))
            my_chat_completion_message.content = response.text
            print(f"\n音声ファイルは「{response.text}」とテキスト化されました\n")
            self.save(my_chat_completion_message)
        else:
            print(f"音声ファイル {my_chat_completion_message.file_path} は存在しません")

    def post_to_gpt(self, path_to_audio: str):
        audio = open(path_to_audio, "rb")
        return self.client.audio.transcriptions.create(model="whisper-1", file=audio)

    def save(self, my_chat_completion_message: MyChatCompletionMessage):
        self.chatlogs_repository.upsert(my_chat_completion_message)
