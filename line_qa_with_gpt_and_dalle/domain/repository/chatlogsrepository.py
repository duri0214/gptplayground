from line_qa_with_gpt_and_dalle.domain.service.gptservice import MyChatCompletionMessage
from line_qa_with_gpt_and_dalle.models import ChatLogsWithLine


class ChatLogsRepository:
    def __init__(self):
        print("Initializing ChatLogsRepository")

    def find_chatlogs_by_id(self, pk: int) -> list[ChatLogsWithLine]:
        pass

    def find_chatlogs_by_user_id(self, user_id: int) -> list[ChatLogsWithLine]:
        pass

    @staticmethod
    def insert(my_chat_completion_message: MyChatCompletionMessage):
        ChatLogsWithLine.objects.create(my_chat_completion_message.to_entity())

    @staticmethod
    def bulk_insert(my_chat_completion_message_list: list[MyChatCompletionMessage]):
        ChatLogsWithLine.objects.bulk_create(my_chat_completion_message_list)
