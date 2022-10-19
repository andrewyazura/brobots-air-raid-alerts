from logging.config import dictConfig

from config import Config
from src.telegram_bot import TelegramBot

current_bot = TelegramBot()


def create_bot(config=Config) -> TelegramBot:
    dictConfig(config.LOG_CONFIG)

    current_bot.init_bot(config)
    current_bot.init_db()

    import src.handlers
    import src.jobs
    import src.models

    create_tables()

    return current_bot


def create_tables() -> None:
    from src.models import Notification, Response, User, populate_responses

    with current_bot.database:
        current_bot.database.create_tables(models=[Notification, Response, User])

    populate_responses()
