import os
import secrets
from abc import ABC, abstractmethod

from PIL import Image
from openai import OpenAI
from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam,
    ChatCompletion,
)

from line_qa_with_gpt_and_dalle.domain.repository.chatlogs import (
    ChatLogsRepository,
)
from line_qa_with_gpt_and_dalle.models import ChatLogsWithLine


class MyChatCompletionMessage:
    def __init__(self, user_id: int, role: str, content: str, invisible: bool):
        # TODO: domainに移動できるはず
        self.user_id = user_id
        self.role = role
        self.content = content
        self.invisible = invisible

    def to_origin_param(self):
        if self.role == "system":
            temp = ChatCompletionSystemMessageParam(role="system", content=self.content)
        elif self.role == "assistant":
            temp = ChatCompletionAssistantMessageParam(
                role="assistant", content=self.content
            )
        else:
            temp = ChatCompletionUserMessageParam(role="user", content=self.content)

        return temp

    def to_entity(self):
        return ChatLogsWithLine(
            user_id=self.user_id,
            role=self.role,
            content=self.content,
            invisible=self.invisible,
        )

    def __str__(self):
        return f"user_id: {self.user_id}, role: {self.role}, content: {self.content}, is_invisible: {self.invisible}"


class Gender:
    def __init__(self, gender):
        if gender not in {"man", "woman"}:
            raise ValueError("Invalid gender")
        self.gender = gender

    @property
    def name(self) -> str:
        return "男性" if self.gender == "man" else "女性"


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
        self, user_id: int, new_chat: str, gender: str
    ) -> list[MyChatCompletionMessage]:

        chat_history = self.get_chat_history(user_id, Gender(gender))

        # 会話が始まっているならユーザの入力したチャットをinsertしてからChatGPTに全投げする
        # ユーザのボタン押下で「プロンプト」と「さぁはじめましょう」の2行がinsertされるので
        # 3以上あれば会話が始まっていると判定することができる
        if len(chat_history) > 2:
            chat_history.append(
                self.save(
                    MyChatCompletionMessage(
                        user_id=user_id, role="user", content=new_chat, invisible=False
                    )
                )
            )
        response = self.post_to_gpt(chat_history)

        latest_assistant = MyChatCompletionMessage(
            user_id=user_id,
            role=response[0].message.role,
            content=response[0].message.content,
            invisible=False,
        )
        chat_history.append(self.save(latest_assistant))

        if "アセスメントは終了" in latest_assistant.content:
            chat_history.append(
                self.save(
                    MyChatCompletionMessage(
                        user_id=latest_assistant.user_id,
                        role="user",
                        content="判定結果をjsonで出してください",
                        invisible=True,
                    )
                )
            )
            response = self.post_to_gpt(chat_history)

            latest_assistant = MyChatCompletionMessage(
                user_id=user_id,
                role=response[0].message.role,
                content=response[0].message.content,
                invisible=False,
            )
            chat_history.append(self.save(latest_assistant))

        return chat_history

    def get_chat_history(
        self, user_id: int, gender: Gender
    ) -> list[MyChatCompletionMessage]:
        chatlogs_list = self.chatlogs_repository.find_chatlogs_by_user_id(user_id)

        if chatlogs_list:
            history = [
                MyChatCompletionMessage(
                    user_id=int(chatlogs.user_id),
                    role=chatlogs.role,
                    content=chatlogs.message,
                    invisible=False,
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
                    content="アセスメントスタート",
                    invisible=False,
                ),
            ]
            self.save(history)

        return history

    @staticmethod
    def get_prompt(gender: Gender) -> str:
        return f"""
            あなたは人材派遣会社の面接官です。
            
            #制約条件
            - 会話の前にあいさつをします
            - 質問1のあとに質問2を行う。質問2が終わったら判定結果例のように、判定結果を出力する
            - 質問1は「目標設定力」評価します
            - 質問2は「コミュニケーション力」を評価します
            - scoreが70を超えたら、judgeが「合格」になる
            - {gender.name} の口調で会話を行う
            
            #質問1
            - 新しいことを学ぶ際、どのような方法を探しますか？
            
            #質問2
            - ストレスが溜まったとき、どのように解消しますか？
            
            #判定結果例
            {{"skill": "目標設定力", "score": 50, "judge": "不合格"}}
            {{"skill": "コミュニケーション力", "score": 96, "judge": "合格"}}
        """

    def post_to_gpt(
        self, chat_history: list[MyChatCompletionMessage]
    ) -> ChatCompletion:
        return self.client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[x.to_origin_param() for x in chat_history],
            temperature=0.5,
        )

    def save(
        self, messages: MyChatCompletionMessage | list[MyChatCompletionMessage]
    ) -> MyChatCompletionMessage | list[MyChatCompletionMessage]:
        if isinstance(messages, list):
            self._bulk_insert_latest_chat_into_the_table(messages)
        elif isinstance(messages, MyChatCompletionMessage):
            self._insert_latest_chat_into_the_table(
                messages.user_id, messages.role, messages.content, messages.invisible
            )
        else:
            raise ValueError(
                f"Unexpected type {type(messages)}. Expected MyChatCompletionMessage or list[MyChatCompletionMessage]."
            )

        return messages

    def _insert_latest_chat_into_the_table(
        self, user_id: int, role: str, content: str, invisible: bool = False
    ) -> MyChatCompletionMessage:
        my_chat_completion_message = MyChatCompletionMessage(
            user_id=user_id, role=role, content=content, invisible=invisible
        )
        self.chatlogs_repository.insert(my_chat_completion_message)

        return my_chat_completion_message

    def _bulk_insert_latest_chat_into_the_table(
        self, my_chat_completion_message_list: list[MyChatCompletionMessage]
    ) -> list[MyChatCompletionMessage]:
        self.chatlogs_repository.bulk_insert(my_chat_completion_message_list)

        return my_chat_completion_message_list


class ModelDalleService(ModelService):
    def generate(self, user_id: str, prompt: str):
        """
        画像urlの有効期限は1時間。それ以上使いたいときは保存する。
        dall-e-3: 1024x1024, 1792x1024, 1024x1792 のいずれかしか生成できない
        """
        pass

    @staticmethod
    def resize(picture: Image) -> Image:
        return picture.resize((512, 512))

    def post_to_gpt(self, xxx: str):
        pass

    @staticmethod
    def save(picture: Image):
        # TODO: chatlogs modelにランダム名でパスを保存するのがいいかもしれない
        folder_path = "app/images"
        # This generates a random string of 10 characters
        random_string = secrets.token_hex(5)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        picture.save(f"{folder_path}/{random_string}.jpg")
