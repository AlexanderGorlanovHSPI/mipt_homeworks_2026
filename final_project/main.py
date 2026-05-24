from gigavibe.app import run
from gigavibe.settings.config import ConfigError


if __name__ == '__main__':
    try:
        run()
    except ConfigError as error:
        print(f'Ошибка конфигурации: {error}')
