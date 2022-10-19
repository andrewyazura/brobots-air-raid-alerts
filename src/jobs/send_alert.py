import datetime

from src import current_bot
from src.air_raid import get_api
from src.models import Notification, NotificationTime, Response, User


@current_bot.schedule("run_repeating", **current_bot.config.JOB_SEND_ALERT)
@current_bot.log_job
def send_alert(*_) -> None:
    now = datetime.datetime.now(tz=current_bot.config.DEFAULTS["tzinfo"])
    weekday = now.weekday()

    if weekday >= 5:
        return

    api = get_api()
    air_raid, _ = api.get_status(tag=current_bot.config.LOCATION)

    Notification.create(air_raid_alert=air_raid)
    current_bot.logger.debug("air_raid_alert = %s", air_raid)

    time = NotificationTime.get_by_id(1).time
    notification_time = datetime.time(time.hour, time.minute + 1)

    if datetime.time(9, 1) <= now.time() <= datetime.time(17, 0):
        message_everyone(Response.get_by_id("text_alert_3").value)

    elif notification_time < now.time() < datetime.time(9, 1):
        message_everyone(Response.get_by_id("text_alert_2").value)


def message_everyone(message) -> None:
    for db_user in User.select(User.user_id).where(User.subscribed == True).dicts():
        current_bot.logged_send_message(db_user["user_id"], message)

    for channel_id in current_bot.config.BOT["CHANNEL_IDS"]:
        current_bot.logged_send_message(channel_id, message)
