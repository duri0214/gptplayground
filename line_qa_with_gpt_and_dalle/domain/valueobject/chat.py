from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionAssistantMessageParam,
    ChatCompletionUserMessageParam,
)

from line_qa_with_gpt_and_dalle.models import ChatLogsWithLine


class MyChatCompletionMessage:
    def __init__(
        self,
        user_id: int,
        role: str,
        content: str,
        invisible: bool,
        file_path: str = None,
    ):
        self.user_id = user_id
        self.role = role
        self.content = content
        self.invisible = invisible
        self.file_path = file_path

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

    def to_entity(self):
        return ChatLogsWithLine(
            user_id=self.user_id,
            role=self.role,
            content=self.content,
            invisible=self.invisible,
            file_path=self.file_path,
        )

    def __str__(self):
        return (
            f"user_id: {self.user_id}, "
            f"role: {self.role}, "
            f"content: {self.content}, "
            f"is_invisible: {self.invisible}, "
            f"file_path: {self.file_path}"
        )
