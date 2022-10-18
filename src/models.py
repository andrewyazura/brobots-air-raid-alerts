from datetime import datetime

from peewee import BooleanField, CharField, DateTimeField, Model

from src import current_bot


class BaseModel(Model):
    class Meta:
        database = current_bot.database


class User(BaseModel):
    user_id = CharField()
    username = CharField(null=True)
    subscribed = BooleanField(default=True)

    joined = DateTimeField(default=datetime.now)


class SchoolDay(BaseModel):
    air_raid_alert = BooleanField()
    datetime = DateTimeField(default=datetime.now)
