import re
from pathlib import Path

FILE_MENTION_PATTERN = re.compile(r'@::(.+?)::')

MAX_FILE_SIZE = 5 * 1024 * 1024


class FileMentionError(Exception):
    pass


def read_mentioned_file(path_text: str) -> str:
    path = Path(path_text)

    if not path.exists():
        raise FileMentionError(f'файл не найден: {path}')

    if not path.is_file():
        raise FileMentionError(f'это не файл: {path}')

    if path.stat().st_size > MAX_FILE_SIZE:
        raise FileMentionError(f'файл слишком большой: {path}')

    try:
        return path.read_text(encoding='utf-8')
    except OSError as error:
        raise FileMentionError(f'не удалось прочитать файл: {path}') from error
    except UnicodeDecodeError as error:
        raise FileMentionError(f'файл не является UTF-8 текстом: {path}') from error


def expand_file_mentions(text: str) -> str:
    def replace_mention(match: re.Match[str]) -> str:
        path_text = match.group(1)
        return read_mentioned_file(path_text)

    return FILE_MENTION_PATTERN.sub(replace_mention, text)
