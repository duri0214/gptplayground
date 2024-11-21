from abc import ABC, abstractmethod
from pathlib import Path

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from config import settings
from line_qa_with_gpt_and_dalle.domain.service.llm import (
    GeminiService,
    OpenAIGptService,
    OpenAIDalleService,
    OpenAITextToSpeechService,
    OpenAISpeechToTextService,
)
from line_qa_with_gpt_and_dalle.domain.valueobject.chat import MyChatCompletionMessage
from line_qa_with_gpt_and_dalle.models import ChatLogsWithLine


class UseCase(ABC):
    @abstractmethod
    def execute(self, user: User, content: str | None):
        pass


class GeminiUseCase(UseCase):
    def execute(self, user: User, content: str | None):
        llm_service = GeminiService()
        my_chat_completion_message = MyChatCompletionMessage(
            user=user,
            role="user",
            content=content,
            invisible=False,
        )
        return llm_service.generate(my_chat_completion_message, gender="man")


class OpenAIGptUseCase(UseCase):
    # Gptに投げるのは role: user のセリフです。Questionは何を入れてもいい
    def execute(self, user: User, content: str | None):
        llm_service = OpenAIGptService()
        my_chat_completion_message = MyChatCompletionMessage(
            user=user,
            role="user",
            content=content,
            invisible=False,
        )
        return llm_service.generate(my_chat_completion_message, gender="man")


class OpenAIDalleUseCase(UseCase):
    # Dalleに投げるのは role: user のセリフです
    def execute(self, user: User, content: str | None):
        llm_service = OpenAIDalleService()
        my_chat_completion_message = MyChatCompletionMessage(
            user=user,
            role="user",
            content=content,
            invisible=False,
        )
        return llm_service.generate(my_chat_completion_message)


class OpenAITextToSpeechUseCase(UseCase):
    # ttsに投げるのは role: user のセリフです
    def execute(self, user: User, content: str | None):
        llm_service = OpenAITextToSpeechService()
        my_chat_completion_message = MyChatCompletionMessage(
            user=user,
            role="user",
            content=content,
            invisible=False,
        )
        return llm_service.generate(my_chat_completion_message)


class OpenAISpeechToTextUseCase(UseCase):
    # ttsに投げるのは直近の role: user のセリフです。Questionは何を入れてもいい
    # TODO: ちょっとファイルが見つけられないバグがある issue7
    def execute(self, user: User, content: str | None):
        record = ChatLogsWithLine.objects.filter(
            Q(user=user)
            & Q(role="user")
            & Q(file_path__endswith=".mp3")
            & Q(invisible=False)
        ).last()

        if record is None:
            raise ObjectDoesNotExist("No audio file registered for the user")

        llm_service = OpenAISpeechToTextService()
        my_chat_completion_message = MyChatCompletionMessage(
            pk=record.pk,
            user=record.user,
            role=record.role,
            content=record.content,
            file_path=str(Path(settings.MEDIA_ROOT) / record.file_path),
            invisible=record.invisible,
        )

        return llm_service.generate(my_chat_completion_message)
