from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionAssistantMessageParam,
    ChatCompletionUserMessageParam,
)


class MyChatCompletionMessage:
    def __init__(
        self,
        role: str,
        content: str = None,
    ):
        self.role = role
        self.content = content

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

    def __str__(self):
        return f"role: {self.role}, " f"content: {self.content}, "
