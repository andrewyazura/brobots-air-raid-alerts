import traceback

from telegram import Update
from telegram.ext import CallbackContext

from src import current_bot


def error_handler(update: Update, context: CallbackContext) -> None:
    exc_info = context.error

    current_bot.logger.error(msg="Exception:", exc_info=exc_info)

    error_traceback = traceback.format_exception(
        type(exc_info), exc_info, exc_info.__traceback__
    )

    message = (
        "<i>bot_data</i>\n"
        f"<pre>{context.bot_data}</pre>\n"
        "<i>user_data</i>\n"
        f"<pre>{context.user_data}</pre>\n"
        "<i>chat_data</i>\n"
        f"<pre>{context.chat_data}</pre>\n"
        "<i>exception</i>\n"
        f"<pre>{''.join(error_traceback)}</pre>"
    )

    for user_id in current_bot.config.BOT["REPORT_TO_IDS"]:
        context.bot.send_message(chat_id=user_id, text=message)

    update.effective_user.send_message("Щось пішло не так...\nРозробники вже сповіщені")


current_bot.dispatcher.add_error_handler(error_handler)
