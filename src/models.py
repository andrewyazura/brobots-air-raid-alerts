import datetime

from peewee import (
    BooleanField,
    CharField,
    DateField,
    DateTimeField,
    DoesNotExist,
    Model,
    SmallIntegerField,
    TextField,
    TimeField,
)

from src import current_bot


class BaseModel(Model):
    class Meta:
        database = current_bot.database


class User(BaseModel):
    user_id = CharField()
    username = CharField(null=True)
    subscribed = BooleanField(default=True)

    joined = DateTimeField(default=datetime.datetime.now)


class Notification(BaseModel):
    air_raid_alert = BooleanField()
    datetime = DateTimeField(default=datetime.datetime.now)


class Response(BaseModel):
    id = CharField(unique=True)
    value = TextField()
    previous_value = TextField(null=True)
    description = TextField()
    keyboard_order = SmallIntegerField()

    updated = DateTimeField(default=datetime.datetime.now)

    def change_value(self, new_value: str) -> None:
        self.previous_value = self.value
        self.value = new_value
        self.updated = datetime.datetime.now()

        self.save()


class NotificationTime(BaseModel):
    time = TimeField()


class ExceptionRange(BaseModel):
    message = TextField()
    type = CharField()

    start_date = DateField()
    end_date = DateField()


class ExceptionDay(BaseModel):
    message = TextField(null=True)
    type = CharField()

    date = DateField()


def populate_responses() -> None:
    try:
        NotificationTime.get_by_id(1)
    except DoesNotExist:
        NotificationTime.create(time=datetime.time(8, 0, 0))

    try:
        Response.get_by_id("text_no_alert")
    except DoesNotExist:
        Response.get_or_create(
            id="text_no_alert",
            value="🟢 <b>Тривоги немає.</b> Школа #brobots сьогодні "
            "буде працювати очно, чекаємо вас у школі.",
            description="Тривоги немає",
            keyboard_order=0,
        )

    try:
        Response.get_by_id("text_alert_1")
    except DoesNotExist:
        Response.get_or_create(
            id="text_alert_1",
            value="🔴 <b>Увага! В Києві зараз тривога.</b> Школа #brobots "
            "сьогодні буде працювати онлайн.",
            description="Тривога є о {}",
            keyboard_order=1,
        )

    try:
        Response.get_by_id("text_alert_2")
    except DoesNotExist:
        Response.get_or_create(
            id="text_alert_2",
            value="🟠 <b>Увага! В Києві зараз тривога.</b> Подумайте про власну "
            "безпеку: якщо ви в дорозі до школи - пройдіть до укриття, "
            "якщо біля школи - спускайтесь у шкільне укриття в кафе. "
            "Керуйтесь рекомендаціями від батьків. Після відбою ми "
            "розпочинаємо очне навчання.",
            description="Тривога почалася між {} та 9:00",
            keyboard_order=2,
        )

    try:
        Response.get_by_id("text_alert_3")
    except DoesNotExist:
        Response.get_or_create(
            id="text_alert_3",
            value="🟡 <b>Увага! В Києві зараз тривога.</b> Навчання призупинено, "
            "спускайтесь у шкільне укриття в кафе. Після відбою ми "
            "розпочинаємо очне навчання.",
            description="Тривога почалася між 9:00 та 17:00",
            keyboard_order=3,
        )

    try:
        Response.get_by_id("text_alert_4")
    except DoesNotExist:
        Response.get_or_create(
            id="text_alert_4",
            value="✅ <b>Відбій тривоги.</b> Школа #brobots повертається до навчання.",
            description="Тривога почалася між 9:00 та 17:00",
            keyboard_order=4,
        )
