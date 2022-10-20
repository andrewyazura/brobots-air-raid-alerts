import logging
from functools import wraps
from typing import Any, Callable

from peewee import PostgresqlDatabase
from telegram import Update
from telegram.error import BadRequest, Unauthorized
from telegram.ext import CallbackContext, Defaults, Handler, Updater


class TelegramBot:
    def __init__(self, config=None) -> None:
        if config:
            self.init_bot(config)
            self.init_db()

    def init_bot(self, config) -> None:
        self.config = config
        self.logger = logging.getLogger("telegram_bot")

        defaults = Defaults(**config.DEFAULTS)

        self.updater = Updater(config.BOT["TOKEN"], defaults=defaults)
        self.bot = self.updater.bot
        self.dispatcher = self.updater.dispatcher
        self.job_queue = self.updater.job_queue
        self.jobs = {}

    def init_db(self) -> None:
        self.database = PostgresqlDatabase(**self.config.DB_CONFIG)

    def register_handler(
        self, handler_class: Handler, *args, **kwargs
    ) -> Callable[[Callable], Callable]:
        def decorator(function: Callable) -> Callable:
            handler = handler_class(*args, **kwargs, callback=function)
            self.dispatcher.add_handler(handler)
            return function

        return decorator

    def log_handler(self, function: Callable) -> Callable:
        @wraps(function)
        def decorated_function(
            update: Update, context: CallbackContext, *args, **kwargs
        ) -> Any:
            self.logger.debug("Update: %s", str(update))
            self.logger.debug("bot_data: %s", str(context.bot_data))
            self.logger.debug("user_data: %s", str(context.user_data))
            self.logger.debug("chat_data: %s", str(context.chat_data))

            return function(update, context, *args, **kwargs)

        return decorated_function

    def protected(self, function) -> Callable:
        @wraps(function)
        def decorated_function(
            update: Update, context: CallbackContext, *args, **kwargs
        ) -> Any | None:
            username = update.effective_user.username

            if username not in self.config.BOT["OWNER_NICKNAMES"]:
                self.logger.warning(
                    "user %s attempted to access a protected handler", username
                )
                return

            self.logger.debug("user %s authenticated as owner", username)
            return function(update, context, *args, **kwargs)

        return decorated_function

    def schedule(self, method: str, *args, **kwargs) -> Callable[[Callable], Callable]:
        def decorator(function: Callable) -> Callable:
            job = getattr(self.job_queue, method)(callback=function, *args, **kwargs)
            self.jobs[job.name] = job
            return function

        return decorator

    def log_job(self, function: Callable) -> Callable:
        @wraps(function)
        def decorated_function(context: CallbackContext, *args, **kwargs) -> Any:
            self.logger.debug("Job: %s", function.__name__)
            self.logger.debug("bot_data: %s", str(context.bot_data))
            self.logger.debug("user_data: %s", str(context.user_data))
            self.logger.debug("chat_data: %s", str(context.chat_data))

            return function(context, *args, **kwargs)

        return decorated_function

    def logged_send_message(self, chat_id, text, *args, **kwargs) -> None:
        try:
            self.bot.send_message(chat_id=chat_id, text=text, *args, **kwargs)
            self.logger.debug("message sent to chat %s", chat_id)

        except (BadRequest, Unauthorized) as _:
            self.logger.warning(
                "chat %s is unavailable or has blocked the bot", chat_id
            )
