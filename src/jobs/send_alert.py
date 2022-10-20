import datetime

from src import current_bot
from src.air_raid import get_api
from src.models import Notification, NotificationTime, Response, User

RESPONSES = {True: "text_alert_1", False: "text_no_alert"}


@current_bot.schedule("run_repeating", **current_bot.config.JOB_SEND_ALERT)
@current_bot.log_job
def send_alert(*_) -> None:
    now = datetime.datetime.now(tz=current_bot.config.DEFAULTS["tzinfo"])
    weekday = now.weekday()

    if weekday >= 5:
        return

    api = get_api()
    air_raid, _ = api.get_status(tag=current_bot.config.LOCATION)
    current_bot.logger.debug("air_raid_alert = %s", air_raid)

    if not air_raid:
        return

    last_notification = (
        Notification.select().order_by(Notification.datetime.desc()).first()
    )

    if last_notification and last_notification.air_raid_alert:
        return

    Notification.create(air_raid_alert=air_raid)

    time = NotificationTime.get_by_id(1).time
    notification_time = (
        datetime.datetime.combine(now.date(), time) + datetime.timedelta(minutes=1)
    ).time()

    if datetime.time(9, 1) <= now.time() <= datetime.time(17, 0):
        message_everyone(Response.get_by_id("text_alert_3").value)

    elif notification_time < now.time() < datetime.time(9, 1):
        message_everyone(Response.get_by_id("text_alert_2").value)


def send_morning_alert(*_) -> None:
    api = get_api()
    air_raid, _ = api.get_status(tag=current_bot.config.LOCATION)
    current_bot.logger.debug("air_raid_alert = %s", air_raid)

    Notification.create(air_raid_alert=air_raid)
    message_everyone(Response.get_by_id(RESPONSES[air_raid]).value)


def set_morning_alert() -> None:
    if job := current_bot.jobs.get("send_morning_alert"):
        job.schedule_removal()

    time = NotificationTime.get_by_id(1).time
    current_bot.schedule("run_daily", time=time, days=(0, 1, 2, 3, 4))(
        send_morning_alert
    )


def message_everyone(message) -> None:
    for db_user in User.select(User.user_id).where(User.subscribed == True).dicts():
        current_bot.logged_send_message(db_user["user_id"], message)

    for channel_id in current_bot.config.BOT["CHANNEL_IDS"]:
        current_bot.logged_send_message(channel_id, message)
