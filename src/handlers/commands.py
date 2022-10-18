from telegram import Update
from telegram.ext import CommandHandler

from src import current_bot
from src.models import User


@current_bot.register_handler(CommandHandler, ("start",))
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


@current_bot.register_handler(CommandHandler, ("rules"))
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
        "продовжуємо очне навчання.\n"
    )


@current_bot.register_handler(CommandHandler, ("unsubscribe",))
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
