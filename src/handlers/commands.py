import datetime
from enum import Enum, auto
from typing import Literal

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram import User as TelegramUser
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
)

from src import current_bot
from src.air_raid import get_api
from src.constants import ExceptionDayType, ExceptionRangeType
from src.jobs.send_alert import set_morning_alert
from src.models import ExceptionDay, ExceptionRange, NotificationTime, Response, User


class ChangeTimeStatus(Enum):
    CHOOSE_TIME = auto()


class ChangeTextStatus(Enum):
    CHOOSE_RESPONSE = auto()
    SEND_NEW_TEXT = auto()


class AddExceptionRangeStatus(Enum):
    ENTER_TEXT = auto()
    ENTER_START_DATE = auto()
    ENTER_END_DATE = auto()


class AddExceptionDayStatus(Enum):
    ENTER_TEXT = auto()
    ENTER_DATE = auto()


@current_bot.register_handler(CommandHandler, "start")
@current_bot.log_handler
def start(update: Update, *_) -> None:
    user = update.effective_user
    db_user, created = User.get_or_create(user_id=str(user.id), username=user.username)

    if not created and db_user.subscribed:
        user.send_message("Ви вже підписані")
        return

    if not db_user.subscribed:
        db_user.subscribed = True
        db_user.save(only=(User.subscribed,))

    user.send_message("Вітаю! Ви підписалися на шкільні сповіщення 😊")


@current_bot.register_handler(CommandHandler, "help")
@current_bot.log_handler
@current_bot.protected
def commands(update: Update, *_) -> None:
    user = update.effective_user
    user.send_message(
        "/check_text - перевірити задані повідомлення для сповіщень\n"
        "/change_text - змінити повідомлення сповіщень\n\n"
        "/check_time - переглянути час сповіщень\n"
        "/change_time - змінити час сповіщень\n\n"
        "/check_vacation - переглянути канікули\n"
        "/change_text_vacation - додати канікули\n\n"
        "/check_mon - переглянути повідомлення МОН\n"
        "/change_text_mon - додати повідомлення МОН\n\n"
        "/check_holiday - переглянути свята\n"
        "/change_text_holiday - переглянути свята\n\n"
        "/check_exception - переглянути дні, коли бот не працює\n"
        "/enter_exceptions - додати дні, коли бот не працюватиме\n\n"
        "/debug_request - зробити запит на API і показати повну відповідь\n"
        "/logs - переглянути логи"
    )


@current_bot.register_handler(CommandHandler, "rules")
@current_bot.log_handler
def rules(update: Update, *_) -> None:
    user = update.effective_user
    user.send_message(
        "<b>Алгоритм роботи школи, враховуючі часті атаки на Київ:</b>\n"
        "▶️ Якщо є повідомлення від КМДА, МОН про те що школи у Києві мають працювати "
        "дистанційно - ми будемо у цей час працювати дистанційно.\n"
        "▶️ Якщо активних рекомендацій КМДА, МОН немає, або школи мають право приймати "
        "рішення щодо формату роботи самостійно, ми будемо керуватись наступним:\n"
        "    ▶️ якщо триває повітряна тривога зранку до 8:10 включно - школа буде в цей"
        " день працювати дистанційно.\n"
        "    ▶️ якщо тривога розпочалась після 8:10 - учні та вчителі, що вже приїхали "
        "в школу мають бути в укритті. В укритті буде присутній черговий куратор школи "
        "вже з 8 ранку. Вчителі, що застали повітряну тривогу в дорозі можуть "
        "залишатись в укритті <i>(наприклад метро Кловська/Арсенальна)</i>, "
        "чи дійти до укриття в школі <i>(на власний розсуд)</i>. "
        "Після відбою ми розпочинаємо очне навчання.\n"
        "    ▶️ якщо тривога розпочалась після 9:00, то діємо за вже відпрацьованим "
        "планом - уроки призупиняються та всі спускаються в укриття. Після відбою ми "
        "продовжуємо очне навчання."
    )


@current_bot.register_handler(CommandHandler, "unsubscribe")
@current_bot.log_handler
def unsubscribe(update: Update, *_) -> None:
    user = update.effective_user

    db_user = User.get_or_none(user_id=user.id)
    if db_user and db_user.subscribed:
        db_user.subscribed = False
        db_user.save(only=(User.subscribed,))

        user.send_message("Підписку скасовано 😢")
        return

    user.send_message("Ви не були підписані")


@current_bot.register_handler(CommandHandler, "debug_request")
@current_bot.log_handler
@current_bot.protected
def debug_request(update: Update, *_) -> None:
    user = update.effective_user
    location = current_bot.config.LOCATION

    status = get_api().get_status(location)
    user.send_message(f"Current status for {location} is {status}")


@current_bot.register_handler(CommandHandler, "logs")
@current_bot.log_handler
@current_bot.protected
def get_logs(update: Update, *_) -> None:
    user = update.effective_user
    log_file = open(current_bot.config.LOG_FILENAME, "rb")
    user.send_document(document=log_file)


@current_bot.register_handler(CommandHandler, "check_text")
@current_bot.log_handler
@current_bot.protected
def check_text(update: Update, *_) -> None:
    user = update.effective_user

    message = "\n\n".join(
        [
            f"<i>{response.id}:</i> {response.value}"
            for response in Response.select()
            .order_by(Response.keyboard_order)
            .iterator()
        ]
    )

    user.send_message(message)


@current_bot.register_handler(CommandHandler, "check_time")
@current_bot.log_handler
@current_bot.protected
def check_time(update: Update, *_) -> None:
    user = update.effective_user

    notification_time = NotificationTime.get_by_id(1)
    time = notification_time.time.strftime("%H:%M")

    user.send_message(f"Заданий час: {time}")


@current_bot.log_handler
@current_bot.protected
def change_time(update: Update, *_) -> int:
    user = update.effective_user

    notification_time = NotificationTime.get_by_id(1)
    time = notification_time.time.strftime("%H:%M")

    user.send_message(f"Заданий час: {time}")
    user.send_message("Надішліть час у форматі ГГ:ХХ")

    return ChangeTimeStatus.CHOOSE_TIME


@current_bot.log_handler
@current_bot.protected
def get_time(update: Update, *_) -> int:
    user = update.effective_user

    text = update.message.text
    parsed_time = datetime.datetime.strptime(text, "%H:%M")
    time = parsed_time.time()

    notification_time = NotificationTime.get_by_id(1)
    notification_time.time = time
    notification_time.save()

    set_morning_alert()

    user.send_message(f"Новий час збережено: {time}")

    return ConversationHandler.END


@current_bot.log_handler
@current_bot.protected
def change_text(update: Update, *_) -> int:
    user = update.effective_user

    notification_time = NotificationTime.get_by_id(1)
    time = notification_time.time.strftime("%H:%M")

    reply_markup = ReplyKeyboardMarkup(
        [
            [response.description.format(time)]
            for response in Response.select(Response.description)
            .order_by(Response.keyboard_order)
            .iterator()
        ],
        one_time_keyboard=True,
        resize_keyboard=True,
    )
    user.send_message("Оберіть відповідь", reply_markup=reply_markup)

    return ChangeTextStatus.CHOOSE_RESPONSE


@current_bot.log_handler
@current_bot.protected
def get_response(update: Update, context: CallbackContext) -> int:
    user = update.effective_user

    notification_time = NotificationTime.get_by_id(1)
    time = notification_time.time.strftime("%H:%M")
    description = update.message.text.replace(time, "{}", 1)

    response = Response.select().where(Response.description == description).first()
    context.user_data["response_id"] = response.id

    user.send_message(
        f"Поточний текст:\n{response.value}", reply_markup=ReplyKeyboardRemove()
    )
    user.send_message(
        "Напишіть новий текст. Ви можете використовувати HTML-форматування"
    )

    return ChangeTextStatus.SEND_NEW_TEXT


@current_bot.log_handler
@current_bot.protected
def get_new_text(update: Update, context: CallbackContext) -> int:
    user = update.effective_user

    response = Response.get_by_id(context.user_data["response_id"])
    response.change_value(update.message.text)

    user.send_message("Текст збережено")

    return ConversationHandler.END


@current_bot.register_handler(CommandHandler, ("check_mon", "check_vacation"))
@current_bot.log_handler
@current_bot.protected
def check_exception_range(update: Update, *_) -> None:
    today = datetime.date.today()
    user = update.effective_user
    text = update.message.text
    range_type = None

    if "mon" in text:
        range_type = ExceptionRangeType.MON
    elif "vacation" in text:
        range_type = ExceptionRangeType.VACATION

    ranges = (
        ExceptionRange.select()
        .where((ExceptionRange.type == range_type) & (ExceptionRange.end_date >= today))
        .iterator()
    )

    message = "\n\n".join(
        f"З {r.start_date} до {r.end_date} - {r.message}" for r in ranges
    )

    if not message:
        user.send_message("Немає")
        return

    user.send_message(message)


@current_bot.log_handler
@current_bot.protected
def add_exception_range(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    user.send_message("Надішліть повідомлення, що буде надсилатися")

    text = update.message.text
    range_type = None

    if "mon" in text:
        range_type = ExceptionRangeType.MON
    elif "vacation" in text:
        range_type = ExceptionRangeType.VACATION

    context.user_data["type"] = range_type

    return AddExceptionRangeStatus.ENTER_TEXT


@current_bot.log_handler
@current_bot.protected
def get_range_message(update: Update, context: CallbackContext) -> int:
    context.user_data["message"] = update.message.text

    user = update.effective_user
    user.send_message("Надішліть початок дії у форматі РРРР-ММ-ДД")
    return AddExceptionRangeStatus.ENTER_START_DATE


@current_bot.log_handler
@current_bot.protected
def get_range_start(update: Update, context: CallbackContext) -> int:
    user = update.effective_user

    try:
        date = update.message.text
        date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        user.send_message("Неправильна дата, спробуйте ще раз")
        return AddExceptionRangeStatus.ENTER_START_DATE

    context.user_data["start_date"] = date

    user.send_message("Надішліть кінець дії у форматі РРРР-ММ-ДД")
    return AddExceptionRangeStatus.ENTER_END_DATE


@current_bot.log_handler
@current_bot.protected
def get_range_end(update: Update, context: CallbackContext) -> int:
    user = update.effective_user

    try:
        end_date = update.message.text
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        user.send_message("Неправильна дата, спробуйте ще раз")
        return AddExceptionRangeStatus.ENTER_END_DATE

    message = context.user_data["message"]
    start_date = context.user_data["start_date"]

    if end_date < start_date:
        user.send_message(
            "Кінцева дата менша за початкову, можливо"
            " Ви переплутали порядок. Уведіть початок дії знову"
        )
        return AddExceptionRangeStatus.ENTER_START_DATE

    ExceptionRange.create(
        message=message,
        start_date=start_date,
        end_date=end_date,
        type=context.user_data["type"],
    )

    user.send_message(
        f"Готово! З {start_date} до {end_date} приходитиме повідомлення: {message}"
    )

    return ConversationHandler.END


@current_bot.register_handler(CommandHandler, ("check_exception", "check_holiday"))
@current_bot.log_handler
@current_bot.protected
def check_exception_days(update: Update, *_) -> None:
    today = datetime.datetime.today()
    user = update.effective_user
    text = update.message.text
    day_type = None

    if "exception" in text:
        day_type = ExceptionDayType.EXCEPTION
    elif "holiday" in text:
        day_type = ExceptionDayType.HOLIDAY

    days = (
        ExceptionDay.select()
        .where(ExceptionDay.type == day_type, ExceptionDay.date >= today)
        .iterator()
    )

    message = "\n\n".join(
        f"{d.date}" + (f" - {d.message}" if d.message else "") for d in days
    )

    if not message:
        user.send_message("Немає")
        return

    user.send_message(message)


def send_date_rules(user: TelegramUser) -> Literal[AddExceptionDayStatus.ENTER_DATE]:
    user.send_message("Надішліть дату у форматі ММ-ДД або РРРР-ММ-ДД")
    user.send_message("За відсутності року, буде використано поточний рік")
    user.send_message("Щоб закінчити, напишіть /cancel")
    return AddExceptionDayStatus.ENTER_DATE


@current_bot.log_handler
@current_bot.protected
def add_exception_day(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    day_type = None

    if "exceptions" in text:
        day_type = ExceptionDayType.EXCEPTION
    elif "holiday" in text:
        day_type = ExceptionDayType.HOLIDAY

    context.user_data["type"] = day_type
    user = update.effective_user

    if day_type == ExceptionDayType.EXCEPTION:
        return send_date_rules(user)

    user.send_message("Надішліть повідомлення, що буде надсилатися")
    return AddExceptionDayStatus.ENTER_TEXT


@current_bot.log_handler
@current_bot.protected
def get_day_message(update: Update, context: CallbackContext) -> int:
    context.user_data["message"] = update.message.text
    user = update.effective_user
    return send_date_rules(user)


@current_bot.log_handler
@current_bot.protected
def get_day_date(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    message = context.user_data.get("message")
    current_year = datetime.date.today().year

    try:
        date = update.message.text
        if len(date) == 10:
            date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        else:
            date = (
                datetime.datetime.strptime(date, "%m-%d")
                .date()
                .replace(year=current_year)
            )

    except ValueError:
        user.send_message("Неправильна дата, спробуйте ще раз")
        return AddExceptionDayStatus.ENTER_DATE

    ExceptionDay.create(message=message, date=date, type=context.user_data["type"])
    user.send_message(f"Додано день: {date}" + (f" - {message}" if message else ""))
    user.send_message("Надішліть ще одну дату\n/cancel, щоб закінчити")

    return AddExceptionDayStatus.ENTER_DATE


@current_bot.log_handler
def cancel(update: Update, *_) -> int:
    user = update.effective_user
    user.send_message("Готово", reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


current_bot.dispatcher.add_handler(
    ConversationHandler(
        entry_points=[CommandHandler("change_time", change_time)],
        states={
            ChangeTimeStatus.CHOOSE_TIME: [
                MessageHandler(Filters.regex(r"^\d{2}:\d{2}$"), get_time)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )
)


current_bot.dispatcher.add_handler(
    ConversationHandler(
        entry_points=[CommandHandler("change_text", change_text)],
        states={
            ChangeTextStatus.CHOOSE_RESPONSE: [
                MessageHandler(Filters.text & ~Filters.command, get_response)
            ],
            ChangeTextStatus.SEND_NEW_TEXT: [
                MessageHandler(Filters.text & ~Filters.command, get_new_text)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )
)

current_bot.dispatcher.add_handler(
    ConversationHandler(
        entry_points=[
            CommandHandler("change_text_mon", add_exception_range),
            CommandHandler("change_text_vacation", add_exception_range),
        ],
        states={
            AddExceptionRangeStatus.ENTER_TEXT: [
                MessageHandler(Filters.text, get_range_message)
            ],
            AddExceptionRangeStatus.ENTER_START_DATE: [
                MessageHandler(Filters.regex(r"^\d{4}-\d{2}-\d{2}$"), get_range_start)
            ],
            AddExceptionRangeStatus.ENTER_END_DATE: [
                MessageHandler(Filters.regex(r"^\d{4}-\d{2}-\d{2}$"), get_range_end)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
)

current_bot.dispatcher.add_handler(
    ConversationHandler(
        entry_points=[
            CommandHandler("change_text_holiday", add_exception_day),
            CommandHandler("enter_exceptions", add_exception_day),
        ],
        states={
            AddExceptionDayStatus.ENTER_TEXT: [
                MessageHandler(Filters.text, get_day_message)
            ],
            AddExceptionDayStatus.ENTER_DATE: [
                MessageHandler(
                    Filters.regex(r"^((\d{4}-)?\d{2}-\d{2},?)+$"), get_day_date
                )
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
)
