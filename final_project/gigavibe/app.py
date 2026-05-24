from gigavibe.core.history import ChatHistory
from gigavibe.files.chunks import FileChunkError, run_file_chunk_mode
from gigavibe.files.mentions import FileMentionError, expand_file_mentions
from gigavibe.llm.client import LLMClient, LLMError
from gigavibe.settings.config import load_config
from gigavibe.ui.console import clear_screen


def run() -> None:
    config = load_config()
    history = ChatHistory(
        limit_message=config.limit_message,
        limit_chars=config.limit_chars,
    )
    llm_client = LLMClient(config)

    while True:
        user_input = input('>>> ')

        if user_input == r'\q':
            break

        if user_input == '/reset':
            history.reset()
            clear_screen()
            print('История чата очищена.')
            continue

        if user_input.startswith(('/filechunk', '/file_chunk')):
            try:
                run_file_chunk_mode(llm_client, user_input)
            except FileChunkError as error:
                print(f'Ошибка filechunk: {error}')
            except LLMError as error:
                print(f'Ошибка модели: {error}')

            continue

        try:
            expanded_input = expand_file_mentions(user_input)
        except FileMentionError as error:
            print(f'Ошибка файла: {error}')
            continue

        history.add_user_message(expanded_input)
        try:
            answer = llm_client.ask(history.get_messages())
        except KeyboardInterrupt:
            print('\nЗапрос прерван.')
            continue
        except LLMError as error:
            print(f'Ошибка модели: {error}')
            continue

        print(f'Assistant: {answer}')

        history.add_assistant_message(answer)
