from openai import OpenAI

from line_qa_with_gpt_and_dalle.domain.repository.chatlogsrepository import (
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

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "role": self.role,
            "content": self.content,
            "invisible": self.invisible,
        }

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


class GptService:
    def __init__(self):
        self.chatlogs_repository = ChatLogsRepository()

    def generate_with_gpt(
        self, gpt_client: OpenAI, user_id: int, new_chat: str
    ) -> MyChatCompletionMessage:

        chat_history = self.get_chat_history(user_id)

        # 会話が始まっているならユーザの入力したチャットをinsertしてからChatGPTに全投げする
        # ユーザのボタン押下で「プロンプト」と「さぁはじめましょう」の2行がinsertされるので
        # 3以上あれば会話が始まっていると判定することができる
        if len(chat_history) > 2:
            chat_history.append(
                self.insert_latest_chat_into_the_table(
                    user_id=user_id, role="user", content=new_chat
                ).to_dict()
            )

        response = gpt_client.chat.completions.create(
            model="gpt-4-turbo", messages=chat_history, temperature=0.5
        )

        assistant = self.insert_latest_chat_into_the_table(
            user_id=user_id,
            role=response[0].message.role,
            content=response[0].message.content,
        )
        chat_history.append(assistant.to_dict())

        if "アセスメントは終了" in assistant.content:
            chat_history.append(
                self.insert_latest_chat_into_the_table(
                    user_id=assistant.user_id,
                    role="user",
                    content="判定結果をjsonで出してください",
                    invisible=True,
                ).to_dict()
            )

            response = gpt_client.chat.completions.create(
                model="gpt-4-turbo", messages=chat_history, temperature=0.5
            )

            assistant = self.insert_latest_chat_into_the_table(
                user_id=user_id,
                role=response[0].message.role,
                content=response[0].message.content,
            )
            chat_history.append(assistant.to_dict())

        return MyChatCompletionMessage(
            user_id=assistant.user_id,
            role=assistant.role,
            content=assistant.content,
            invisible=assistant.invisible,
        )

    def get_chat_history(self, user_id: int) -> list[dict]:
        chatlogs_list = self.chatlogs_repository.find_chatlogs_by_user_id(user_id)

        # TODO: historyが .to_dict() で増えていくけどこれはたしかSQLAlchemyのbulc_insertの都合だったはずだ
        if chatlogs_list:
            history = [
                MyChatCompletionMessage(
                    user_id=int(chatlogs.user_id),
                    role=chatlogs.role,
                    content=chatlogs.message,
                    invisible=False,
                ).to_dict()
                for chatlogs in chatlogs_list
            ]
        else:
            temp = [
                MyChatCompletionMessage(
                    user_id=user_id,
                    role="system",
                    content=self.get_prompt(),
                    invisible=True,
                ),
                MyChatCompletionMessage(
                    user_id=user_id,
                    role="user",
                    content="アセスメントスタート",
                    invisible=False,
                ),
            ]
            self.bulk_insert_latest_chat_into_the_table(temp)
            history = [x.to_dict() for x in temp]

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

    def insert_latest_chat_into_the_table(
        self, user_id: int, role: str, content: str, invisible: bool = False
    ) -> MyChatCompletionMessage:
        my_chat_completion_message = MyChatCompletionMessage(
            user_id=user_id, role=role, content=content, invisible=invisible
        )
        self.chatlogs_repository.insert(my_chat_completion_message)

        return my_chat_completion_message

    def bulk_insert_latest_chat_into_the_table(
        self, my_chat_completion_message_list: list[MyChatCompletionMessage]
    ):
        self.chatlogs_repository.bulk_insert(my_chat_completion_message_list)

        return my_chat_completion_message_list[-1]

    def generate_with_dalle(self):
        pass
