import sys

from environs import Env
from pytz import timezone

env = Env()
env.read_env(override=True)


class Config:
    with env.prefixed("BOT_"):
        BOT = {
            "TOKEN": env.str("TOKEN"),
            "OWNER_NICKNAMES": env.list("OWNER_NICKNAMES"),
            "REPORT_TO_IDS": env.list("REPORT_TO_IDS"),
            "CHANNEL_IDS": env.list("CHANNEL_IDS"),
        }

    with env.prefixed("DEFAULTS_"):
        DEFAULTS = {
            "parse_mode": env.str("PARSE_MODE"),
            "run_async": env.bool("RUN_ASYNC"),
            "tzinfo": timezone(env.str("TIME_ZONE")),
        }

    with env.prefixed("DB_"):
        DB_CONFIG = {
            "database": env.str("NAME"),
            "host": env.str("HOST"),
            "port": env.int("PORT"),
            "user": env.str("USER"),
            "password": env.str("PASSWORD"),
        }

    with env.prefixed("LOG_"):
        LOG_CONFIG = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {"format": env.str("FORMAT"), "datefmt": env.str("DATEFMT")}
            },
            "handlers": {
                "default": {
                    "level": env.log_level("LEVEL"),
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": sys.stdout,
                }
            },
            "loggers": {
                "telegram_bot": {
                    "level": env.log_level("LEVEL"),
                    "handlers": ["default"],
                },
                "urllib3": {"level": env.log_level("LEVEL"), "handlers": ["default"]},
            },
        }

    with env.prefixed("AIR_RAID_API_"):
        AIR_RAID_API = {
            "url": env.str("URL"),
            "timeout": env.float("TIMEOUT"),
            "token": env.str("TOKEN"),
        }

    with env.prefixed("JOB_SEND_ALERT_"):
        JOB_SEND_ALERT = {"interval": env.int("INTERVAL"), "first": env.int("FIRST")}

    LOCATION = env.str("LOCATION")
