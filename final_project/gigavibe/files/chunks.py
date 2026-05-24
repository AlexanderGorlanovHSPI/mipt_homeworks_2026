from dataclasses import dataclass
from pathlib import Path

from gigavibe.llm.client import LLMClient


@dataclass
class ChunkModeOptions:
    paragraphs_per_chunk: int = 1
    chunk_len: int | None = None
    auto_confirm: bool = False


class FileChunkError(Exception):
    pass


def read_chunk_file(path_text: str) -> str:
    path = Path(path_text)

    if not path.exists():
        raise FileChunkError(f'файл не найден: {path}')

    if not path.is_file():
        raise FileChunkError(f'это не файл: {path}')

    try:
        return path.read_text(encoding='utf-8')
    except OSError as error:
        raise FileChunkError(f'не удалось прочитать файл: {path}') from error
    except UnicodeDecodeError as error:
        raise FileChunkError(f'файл не является UTF-8 текстом: {path}') from error


def split_by_paragraphs(
    text: str,
    paragraphs_per_chunk: int = 1,
) -> list[str]:
    if paragraphs_per_chunk <= 0:
        raise FileChunkError('число абзацев в чанке должно быть больше 0')

    paragraphs = [paragraph for paragraph in text.splitlines() if paragraph.strip()]
    chunks: list[str] = []

    for start in range(0, len(paragraphs), paragraphs_per_chunk):
        chunk = '\n'.join(paragraphs[start:start + paragraphs_per_chunk])
        chunks.append(chunk)

    return chunks


def split_by_length(text: str, chunk_len: int) -> list[str]:
    if chunk_len <= 0:
        raise FileChunkError('длина чанка должна быть больше 0')

    chunks: list[str] = []

    for start in range(0, len(text), chunk_len):
        chunks.append(text[start:start + chunk_len])

    return chunks


def parse_chunk_mode_options(command: str) -> ChunkModeOptions:
    options = ChunkModeOptions()
    parts = command.split()

    for part in parts[1:]:
        if part == '-y':
            options.auto_confirm = True
        elif part.startswith('paragraph='):
            value = part.removeprefix('paragraph=')

            try:
                options.paragraphs_per_chunk = int(value)
            except ValueError as error:
                raise FileChunkError('paragraph должен быть целым числом') from error

            if options.paragraphs_per_chunk <= 0:
                raise FileChunkError('paragraph должен быть больше 0')
        elif part.startswith('len='):
            value = part.removeprefix('len=')

            try:
                options.chunk_len = int(value)
            except ValueError as error:
                raise FileChunkError('len должен быть целым числом') from error

            if options.chunk_len <= 0:
                raise FileChunkError('len должен быть больше 0')
        else:
            raise FileChunkError(f'неизвестный параметр filechunk: {part}')

    return options

def split_into_chunks(text: str, options: ChunkModeOptions) -> list[str]:
    if options.chunk_len is not None:
        return split_by_length(text, options.chunk_len)

    return split_by_paragraphs(text, options.paragraphs_per_chunk)


def build_chunk_prompt(user_prompt: str, chunk: str) -> str:
    return f'{user_prompt}\n\n{chunk}'


def run_file_chunk_mode(llm_client: LLMClient, command: str) -> None:
    options = parse_chunk_mode_options(command)

    path_text = input('Введите путь до файла:\n>>> ')
    if path_text == r'\q':
        print('Обработка файла прервана.')
        return

    text = read_chunk_file(path_text)

    user_prompt = input(
        'Что нужно сделать для каждого фрагмента?\n>>> ',
    )
    if user_prompt == r'\q':
        print('Обработка файла прервана.')
        return

    chunks = split_into_chunks(text, options)
    print('Принято. Начинаю обработку:')

    for chunk_index, chunk in enumerate(chunks, start=1):
        prompt = build_chunk_prompt(user_prompt, chunk)
        try:
            answer = llm_client.ask_once(prompt)
        except KeyboardInterrupt:
            print('\nЗапрос прерван.')
            return

        print(answer)

        is_last_chunk = chunk_index == len(chunks)
        if not options.auto_confirm and not is_last_chunk:
            next_input = input('Нажмите Enter для следующего фрагмента:\n>>> ')

            if next_input == r'\q':
                print('Обработка файла прервана.')
                return

            if next_input:
                print('Для продолжения нужен пустой ввод.')
                return

    print('Обработка файла завершена.')
