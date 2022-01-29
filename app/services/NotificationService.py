from configparser import ConfigParser

from app.models.Notification import Notification
from app.services.ApiService import ApiService
from app.services.Utils import Utils

path_to_configuration_file = "config.ini"


class NotificationService:
    _api_service: ApiService

    def __init__(self):
        config_init = ConfigParser()
        config_init.read(path_to_configuration_file)
        config = config_init["DEFAULT"]
        api_url = config["api_base_url"]
        self._api_service = ApiService(api_url)

    def send_buy_notification(self, coin: str, amount: float):
        notification = Notification(
            title="Buy order",
            body=f"buy order for {amount} {coin}",
            topic=Utils.NOTIFICATION_TOPIC)
        self._api_service.post_notification(notification)

    def send_sell_notification(self, coin: str, amount: float):
        notification = Notification(
            title="Sell order",
            body=f"sell order for {amount} {coin}",
            topic=Utils.NOTIFICATION_TOPIC)
        self._api_service.post_notification(notification)
