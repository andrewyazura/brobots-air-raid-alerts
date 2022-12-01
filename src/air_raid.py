from logging import getLogger
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from src import current_bot


class AirRaidApi:
    def __init__(self, url: str, timeout: int | float) -> None:
        self.url = url
        self.timeout = timeout
        self.logger = getLogger("telegram_bot")

    def get_status(self, tag: str) -> bool:
        response = requests.get(
            url=self.make_url("/s/air_alert_ua"),
            timeout=self.timeout,
            params={"q": str(tag)},
        )

        if not response.text:
            self.logger.debug("response is empty")

        soup = BeautifulSoup(markup=response.text, features="html.parser")
        last_message = soup.find_all(
            name="div", attrs={"class": "tgme_widget_message"}
        )[-1]
        message_text = last_message.find(
            name="div", attrs={"class": "tgme_widget_message_text"}
        ).getText()

        air_raid = "відбій" not in message_text.lower()

        return air_raid

    def make_url(self, endpoint: str) -> str:
        return urljoin(self.url, endpoint)


def get_api() -> AirRaidApi:
    return AirRaidApi(**current_bot.config.AIR_RAID_API)
