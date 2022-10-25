import datetime

from src import current_bot
from src.air_raid import get_api
from src.models import (
    ExceptionDay,
    ExceptionRange,
    Notification,
    NotificationTime,
    Response,
    User,
)

RESPONSES = {True: "text_alert_1", False: "text_no_alert"}


def get_now() -> datetime:
    return datetime.datetime.now(tz=current_bot.config.DEFAULTS["tzinfo"])


def check_date() -> tuple[bool, str]:
    now = get_now()
    weekday = now.weekday()

    if weekday >= 5:
        current_bot.logger.debug("job cancelled - not a weekday")
        return False, ""

    today = now.date()
    current_exception = (
        ExceptionRange.select()
        .where(
            (ExceptionRange.start_date <= today) & (ExceptionRange.end_date >= today)
        )
        .first()
    )

    if current_exception:
        current_bot.logger.debug(
            "job cancelled - ExceptionRange(%i)", current_exception.id
        )
        if current_exception.start_date == today:
            return False, current_exception.message
        return False, ""

    current_exception = ExceptionDay.select().where(ExceptionDay.date == today).first()

    if current_exception:
        current_bot.logger.debug(
            "job cancelled - ExceptionDay(%i)", current_exception.id
        )
        return False, current_exception.message

    return True, ""


@current_bot.schedule("run_repeating", **current_bot.config.JOB_SEND_ALERT)
@current_bot.log_job
def send_alert(*_) -> None:
    check, _ = check_date()

    if not check:
        return

    api = get_api()
    air_raid, _ = api.get_status(tag=current_bot.config.LOCATION)
    current_bot.logger.debug("air_raid_alert = %s", air_raid)

    last_notification = (
        Notification.select().order_by(Notification.datetime.desc()).first()
    )

    Notification.create(air_raid_alert=air_raid)

    if not air_raid:
        return

    if not last_notification:
        return

    if last_notification.air_raid_alert:
        return

    now = get_now()
    time = NotificationTime.get_by_id(1).time
    notification_time = (
        datetime.datetime.combine(now.date(), time) + datetime.timedelta(minutes=1)
    ).time()

    if datetime.time(9, 0) <= now.time() <= datetime.time(17, 0):
        message_everyone(Response.get_by_id("text_alert_3").value)

    elif notification_time < now.time() < datetime.time(9, 0):
        message_everyone(Response.get_by_id("text_alert_2").value)


def send_morning_alert(*_) -> None:
    check, message = check_date()

    if message:
        message_everyone(message)

    if not check:
        return

    api = get_api()
    air_raid, _ = api.get_status(tag=current_bot.config.LOCATION)
    current_bot.logger.debug("air_raid_alert = %s", air_raid)

    Notification.create(air_raid_alert=air_raid)
    message_everyone(Response.get_by_id(RESPONSES[air_raid]).value)


def set_morning_alert() -> None:
    if job := current_bot.jobs.get("send_morning_alert"):
        job.schedule_removal()
        current_bot.logger.debug("morning_alert job cancelled")

    time = NotificationTime.get_by_id(1).time
    current_bot.schedule("run_daily", time=time)(send_morning_alert)
    current_bot.logger.debug("morning_alert job scheduled for %s", time)


def message_everyone(message) -> None:
    for db_user in User.select(User.user_id).where(User.subscribed == True).dicts():
        current_bot.logged_send_message(db_user["user_id"], message)

    for channel_id in current_bot.config.BOT["CHANNEL_IDS"]:
        current_bot.logged_send_message(channel_id, message)
