from dataclasses import dataclass
from typing import Literal


@dataclass
class Message:
    role: Literal['user', 'assistant']
    content: str


class ChatHistory:
    def __init__(
        self,
        limit_message: int | None = None,
        limit_chars: int | None = None,
    ) -> None:
        self.messages: list[Message] = []
        self.limit_message = limit_message
        self.limit_chars = limit_chars

    def add_user_message(self, content: str) -> None:
        self.messages.append(Message(role='user', content=content))
        self.trim()

    def add_assistant_message(self, content: str) -> None:
        self.messages.append(Message(role='assistant', content=content))
        self.trim()

    def reset(self) -> None:
        self.messages.clear()

    def get_messages(self) -> list[Message]:
        return self.messages.copy()

    def trim_by_message_limit(self) -> None:
        if self.limit_message is None:
            return

        while len(self.messages) > self.limit_message:
            self.messages.pop(0)

    def total_chars(self) -> int:
        return sum(len(message.content) for message in self.messages)

    def trim_by_chars_limit(self) -> None:
        if self.limit_chars is None:
            return

        while self.messages and self.total_chars() > self.limit_chars:
            self.messages.pop(0)

    def trim_last_message_if_too_long(self) -> None:
        if self.limit_chars is None or not self.messages:
            return

        last_message = self.messages[-1]

        if len(last_message.content) > self.limit_chars:
            last_message.content = last_message.content[-self.limit_chars:]

    def trim(self) -> None:
        self.trim_last_message_if_too_long()
        self.trim_by_message_limit()
        self.trim_by_chars_limit()
