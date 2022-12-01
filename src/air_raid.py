from json.decoder import JSONDecodeError
from logging import getLogger
from urllib.parse import urljoin

import requests

from src import current_bot


class AirRaidApi:
    def __init__(self, url: str, timeout: int | float) -> None:
        self.url = url
        self.timeout = timeout
        self.logger = getLogger("telegram_bot")

    def get_status(self, tag: str) -> bool:
        response = requests.get(url=self.url, timeout=self.timeout)

        if not response.text:
            self.logger.debug("response is empty")

        self.logger.debug(response.text)

        try:
            response_data = response.json()
        except JSONDecodeError:
            self.logger.debug("response format is an invalid json string")

        for alert in response_data["alerts"]:
            if tag in alert["location_title"]:
                return True

        return False

    def make_url(self, endpoint: str) -> str:
        return urljoin(self.url, endpoint)


def get_api() -> AirRaidApi:
    return AirRaidApi(**current_bot.config.AIR_RAID_API)
