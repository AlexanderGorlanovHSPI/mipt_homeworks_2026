import os
from dataclasses import dataclass
from pathlib import Path

import yaml
from dotenv import load_dotenv


@dataclass
class Config:
    api_key: str
    api_host: str
    limit_message: int | None
    limit_chars: int | None
    temperature: float
    system_prompt: str | None
    model: str


class ConfigError(Exception):
    pass


def load_yaml_config(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}

    try:
        with path.open(encoding='utf-8') as file:
            data = yaml.safe_load(file)
    except OSError as error:
        raise ConfigError('не удалось прочитать config.yaml') from error
    except yaml.YAMLError as error:
        raise ConfigError('config.yaml содержит некорректный YAML') from error

    if data is None:
        return {}

    if not isinstance(data, dict):
        raise ConfigError('config.yaml должен содержать словарь настроек')

    return data


def parse_optional_int(value: object, name: str) -> int | None:
    if value is None:
        return None

    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise ConfigError(f'{name} должен быть целым числом или null')

    try:
        parsed_value = int(value)
    except (TypeError, ValueError) as error:
        raise ConfigError(f'{name} должен быть целым числом или null') from error

    if parsed_value <= 0:
        raise ConfigError(f'{name} должен быть положительным целым числом')

    return parsed_value


def parse_temperature(value: object) -> float:
    if value is None:
        return 0.5

    if isinstance(value, bool) or not isinstance(value, (float, int, str)):
        raise ConfigError('temperature должен быть числом')

    try:
        temperature = float(value)
    except (TypeError, ValueError) as error:
        raise ConfigError('temperature должен быть числом') from error

    if not (0.0 <= temperature <= 1.0):
        raise ConfigError('temperature должен быть в диапазоне от 0.0 до 1.0')

    return temperature


def require_str(value: object, name: str) -> str:
    if not isinstance(value, str):
        raise ConfigError(f'{name} должен быть строкой')

    if not value.strip():
        raise ConfigError(f'{name} не может быть пустой строкой')

    return value.strip()


def load_config(path: Path | None = None) -> Config:
    if path is None:
        path = Path('config.yaml')

    load_dotenv(path.with_name('.env'))

    yaml_config = load_yaml_config(path)

    api_key = os.environ.get('API_KEY', yaml_config.get('api_key'))
    api_host = os.environ.get('API_HOST', yaml_config.get('api_host'))
    limit_message = os.environ.get(
        'LIMIT_MESSAGE',
        yaml_config.get('limit_message'),
    )
    limit_chars = os.environ.get(
        'LIMIT_CHARS',
        yaml_config.get('limit_chars'),
    )
    temperature = os.environ.get(
        'TEMPERATURE',
        yaml_config.get('temperature'),
    )
    system_prompt = yaml_config.get('system_prompt')

    model = os.environ.get('MODEL', yaml_config.get('model'))

    return Config(
        api_key=require_str(api_key, 'api_key'),
        api_host=require_str(api_host, 'api_host'),
        limit_message=parse_optional_int(limit_message, 'limit_message'),
        limit_chars=parse_optional_int(limit_chars, 'limit_chars'),
        temperature=parse_temperature(temperature),
        system_prompt=system_prompt if isinstance(system_prompt, str) else None,
        model=require_str(model, 'model'),
    )
