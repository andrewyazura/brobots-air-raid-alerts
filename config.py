from environs import Env
from pytz import timezone

env = Env()
env.read_env()


class Config:
    with env.prefixed("BOT_"):
        BOT = {
            "TOKEN": env.str("TOKEN"),
            "OWNER_IDS": env.list("OWNER_IDS"),
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
                "file": {"format": env.str("FORMAT"), "datefmt": env.str("DATEFMT")}
            },
            "handlers": {
                "file": {
                    "level": env.log_level("LEVEL"),
                    "formatter": "file",
                    "class": "logging.handlers.TimedRotatingFileHandler",
                    "filename": env.str("FILENAME"),
                    "when": env.str("ROTATE_TIME"),
                    "backupCount": env.int("ROTATE_BACKUP_COUNT"),
                    "utc": True,
                }
            },
            "loggers": {
                "telegram_bot": {"level": env.log_level("LEVEL"), "handlers": ["file"]}
            },
        }

    with env.prefixed("AIR_RAID_API_"):
        AIR_RAID_API = {"url": env.str("URL"), "timeout": env.float("TIMEOUT")}

    with env.prefixed("JOB_SEND_ALERT_"):
        JOB_SEND_ALERT = {
            "time": env.time("TIME"),
            "days": tuple(int(day) for day in env.list("DAYS")),
        }

    LOCATION = env.str("LOCATION")
