from configparser import ConfigParser
from typing import Optional, Dict, Any
from requests import Request, Session, Response
from app.models.Notification import Notification

path_to_configuration_file = "config.ini"


class ApiService:
    def __init__(
            self,
            base_url: str,
    ) -> None:
        config_init = ConfigParser()
        config_init.read(path_to_configuration_file)
        config = config_init["AUTHENTICATION"]

        self._api_key = config["API_KEY"]
        self._api_key_name = config["API_KEY_NAME"]
        self._session = Session()
        self._base_url = base_url

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request('GET', path, params=params)

    def _post(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request('POST', path, json=params)

    def _delete(self,
                path: str,
                params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request('DELETE', path, json=params)

    def _request(self, method: str, path: str, **kwargs) -> Any:
        request = Request(method, self._base_url + path, {self._api_key_name: self._api_key}, **kwargs)
        response = self._session.send(request.prepare())

        return self._process_response(response)

    @staticmethod
    def _process_response(response: Response) -> Any:
        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()
            raise
        else:
            if not data:
                raise Exception(data)
            return data

    def post_notification(self, notification: Notification) -> str:
        return self._post("notification", notification.dict())
