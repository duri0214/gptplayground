from abc import ABC, abstractmethod

from openai import OpenAI
from openai.types.chat import (
    ChatCompletion,
)

from d_id.domain.valueobject.chat import MyChatCompletionMessage


class ModelService(ABC):
    def __init__(self, client: OpenAI):
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
    ) -> MyChatCompletionMessage:
        if my_chat_completion_message.content is None:
            raise Exception("content is None")

        response = self.post_to_gpt([my_chat_completion_message])

        latest_assistant = MyChatCompletionMessage(
            role=response.choices[0].message.role,
            content=response.choices[0].message.content,
        )

        return latest_assistant

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
        pass
