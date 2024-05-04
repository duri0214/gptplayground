from line_qa_with_gpt_and_dalle.domain.service.openai import MyChatCompletionMessage
from line_qa_with_gpt_and_dalle.models import ChatLogsWithLine


class ChatLogsRepository:
    def __init__(self):
        print("Initializing ChatLogsRepository")

    @staticmethod
    def find_chatlogs_by_id(pk: int) -> list[ChatLogsWithLine]:
        return ChatLogsWithLine.objects.get(pk=pk)

    @staticmethod
    def find_chatlogs_by_user_id(user_id: int) -> list[ChatLogsWithLine]:
        return ChatLogsWithLine.objects.filter(user_id=user_id)

    @staticmethod
    def insert(my_chat_completion_message: MyChatCompletionMessage):
        ChatLogsWithLine.objects.create(my_chat_completion_message.to_entity())

    @staticmethod
    def bulk_insert(my_chat_completion_message_list: list[MyChatCompletionMessage]):
        ChatLogsWithLine.objects.bulk_create(my_chat_completion_message_list)
