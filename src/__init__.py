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

    src.jobs.send_alert.set_morning_alert()

    return current_bot


def create_tables() -> None:
    from src.models import (
        ExceptionDay,
        ExceptionRange,
        Notification,
        NotificationTime,
        Response,
        User,
        populate_responses,
    )

    with current_bot.database:
        current_bot.database.create_tables(
            models=[
                ExceptionDay,
                ExceptionRange,
                Notification,
                NotificationTime,
                Response,
                User,
            ]
        )

    populate_responses()
