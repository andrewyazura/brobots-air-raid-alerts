from telegram.error import Unauthorized

from src import current_bot
from src.air_raid import get_api
from src.models import SchoolDay, User

MESSAGES = {True: "Школа сьогодні працює онлайн", False: "Школа сьогодні працює очно"}


@current_bot.schedule("run_daily", **current_bot.config.JOB_SEND_ALERT)
@current_bot.log_job
def send_school_state(*_) -> None:
    api = get_api()
    status, _ = api.get_status(tag=current_bot.config.LOCATION)
    current_bot.logger.debug("air_raid_alert=%s", status)

    SchoolDay.create(air_raid_alert=status)

    for db_user in User.select(User.user_id).where(User.subscribed == True).dicts():
        try:
            current_bot.bot.send_message(
                chat_id=db_user["user_id"], text=MESSAGES[status]
            )
            current_bot.logger.debug("notification sent to user %s", db_user["user_id"])

        except Unauthorized:
            current_bot.logger.warning("user %s blocked the bot", db_user["user_id"])

    for channel_id in current_bot.config.BOT["CHANNEL_IDS"]:
        try:
            current_bot.bot.send_message(chat_id=channel_id, text=MESSAGES[status])
            current_bot.logger.debug("notification sent to channel %s", channel_id)

        except Unauthorized:
            current_bot.logger.warning("channel_id %s blocked the bot", channel_id)
