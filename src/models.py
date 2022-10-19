from datetime import datetime

from peewee import BooleanField, CharField, DateTimeField, Model, TextField

from src import current_bot


class BaseModel(Model):
    class Meta:
        database = current_bot.database


class User(BaseModel):
    user_id = CharField(unique=True)
    username = CharField(null=True)
    subscribed = BooleanField(default=True)

    joined = DateTimeField(default=datetime.now)


class Notification(BaseModel):
    air_raid_alert = BooleanField()
    datetime = DateTimeField(default=datetime.now)


class Response(BaseModel):
    id = CharField(unique=True)
    value = TextField()
    previous_value = TextField(null=True)
    description = TextField()

    updated = DateTimeField(default=datetime.now)

    def change_value(self, new_value: str) -> None:
        self.previous_value = self.value
        self.value = new_value
        self.updated = datetime.now()

        self.save()


def populate_responses() -> None:
    Response.get_or_create(
        id="text_no_alert",
        value="🟢 <b>Тривоги немає.</b> Школа #brobots сьогодні "
        "буде працювати очно, чекаємо вас у школі.",
        description="Тривоги немає",
    )

    Response.get_or_create(
        id="text_alert_1",
        value="🔴 <b>Увага! В Києві зараз тривога.</b> Школа #brobots "
        "сьогодні буде працювати онлайн.",
        description="Тривога є у заданий час",
    )

    Response.get_or_create(
        id="text_alert_2",
        value="🟠 <b>Увага! В Києві зараз тривога.</b> Подумайте про власну "
        "безпеку: якщо ви в дорозі до школи - пройдіть до укриття, "
        "якщо біля школи - спускайтесь у шкільне укриття в кафе. "
        "Керуйтесь рекомендаціями від батьків. Після відбою ми "
        "розпочинаємо очне навчання.",
        description="Тривога почалася між заданим часом та 9:00",
    )

    Response.get_or_create(
        id="text_alert_3",
        value="🟡 <b>Увага! В Києві зараз тривога.</b> Навчання призупинено, "
        "спускайтесь у шкільне укриття в кафе. Після відбою ми "
        "розпочинаємо очне навчання.",
        description="Тривога почалася між 9:00 та 17:00",
    )
