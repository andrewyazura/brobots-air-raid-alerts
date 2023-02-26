from json.decoder import JSONDecodeError
from logging import getLogger

import requests

from src import current_bot


class AirRaidApi:
    def __init__(self, url: str, timeout: int | float, token: str) -> None:
        self.url = url
        self.timeout = timeout
        self.token = token
        self.logger = getLogger("telegram_bot")

    def get_status(self, tag: str) -> bool:
        response = requests.get(
            url=self.url,
            timeout=self.timeout,
            headers={"Authorization": f"Bearer {self.token}"},
        )

        if not response.text:
            self.logger.debug("response is empty")

        self.logger.debug(response.text)

        try:
            response_data = response.json()
        except JSONDecodeError:
            self.logger.debug("response format is an invalid json string")

        for alert in response_data["alerts"]:
            if tag in alert["n"]:
                return True

        return False


def get_api() -> AirRaidApi:
    return AirRaidApi(**current_bot.config.AIR_RAID_API)
