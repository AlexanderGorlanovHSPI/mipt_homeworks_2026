from openai import APIError, OpenAI
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)

from gigavibe.core.history import Message
from gigavibe.settings.config import Config


class LLMError(Exception):
    pass


class LLMClient:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.api_host,
        )

    def build_api_messages(self, messages: list[Message]) -> list[ChatCompletionMessageParam]:
        api_messages: list[ChatCompletionMessageParam] = []

        if self.config.system_prompt is not None:
            api_messages.append(
                ChatCompletionSystemMessageParam(
                    role='system',
                    content=self.config.system_prompt,
                ),
            )

        for message in messages:
            if message.role == 'user':
                api_messages.append(
                    ChatCompletionUserMessageParam(
                        role='user',
                        content=message.content,
                    ),
                )
            else:
                api_messages.append(
                    ChatCompletionAssistantMessageParam(
                        role='assistant',
                        content=message.content,
                    ),
                )

        return api_messages

    def ask(self, messages: list[Message]) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=self.build_api_messages(messages),
                temperature=self.config.temperature,
            )
        except APIError as error:
            raise LLMError('не удалось получить ответ от модели') from error

        answer = response.choices[0].message.content

        if answer is None:
            return ''

        return answer

    def ask_once(self, prompt: str) -> str:
        message = Message(role='user', content=prompt)
        return self.ask([message])
