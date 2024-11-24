from django.contrib.auth.models import User
from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionAssistantMessageParam,
    ChatCompletionUserMessageParam,
)

from line_qa_with_gpt_and_dalle.models import ChatLogsWithLine


class MyChatCompletionMessage:
    def __init__(
        self,
        user: User,
        role: str,
        invisible: bool,
        pk: int = None,
        content: str = None,
        file_path: str = None,
    ):
        self.id = pk
        self.user = user
        self.role = role
        self.content = content
        self.file_path = file_path
        self.invisible = invisible

    def to_origin(self):
        if self.role == "system":
            temp = ChatCompletionSystemMessageParam(role="system", content=self.content)
        elif self.role == "assistant":
            temp = ChatCompletionAssistantMessageParam(
                role="assistant", content=self.content
            )
        else:
            temp = ChatCompletionUserMessageParam(role="user", content=self.content)

        return temp

    def to_entity(self) -> ChatLogsWithLine:
        return ChatLogsWithLine(
            user=self.user,
            role=self.role,
            content=self.content,
            invisible=self.invisible,
            file_path=self.file_path,
        )

    def __str__(self):
        return (
            f"user_id: {self.user.pk}, "
            f"role: {self.role}, "
            f"content: {self.content}, "
            f"invisible: {self.invisible}, "
            f"file_path: {self.file_path}"
        )
