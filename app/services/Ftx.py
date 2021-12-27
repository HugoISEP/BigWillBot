import logging

from typing import List
from time import time

import ftx
from pydantic import parse_obj_as

from app.configuration.Configuration import Configuration
from app.models.FtxBalance import FtxBalance
from app.models.PlaceOrderResponse import PlaceOrderResponse
from app.services.Utils import Utils


class Ftx:
    client = None
    log = logging.getLogger("FTX")
    # Equivalent to 15min in seconds
    time_frame = 900

    def __init__(self):
        config = Configuration()
        self.client = ftx.FtxClient(
            api_key=config.api_key,
            api_secret=config.api_secret,
            subaccount_name=config.subaccount_name
        )

    def get_data_from_pair(self, pair_symbol: str) -> dict:
        return self.client.get_historical_data(
            market_name=pair_symbol,
            resolution=self.time_frame,
            limit=Utils.NUMBER_OF_VALUES,
            start_time=float(round(time())) - Utils.NUMBER_OF_VALUES * self.time_frame,
            end_time=float(round(time()))
        )

    def get_balances(self) -> List[FtxBalance]:
        try:
            data = self.client.get_balances()
            list_balances: List[FtxBalance] = parse_obj_as(List[FtxBalance], data)
            self.log.info(f"Get balances")
            return list_balances
        except Exception as e:
            self.log.error(f"Get balances: {e}")

    def buy(self, pair_symbol: str, tokens_number: float) -> PlaceOrderResponse:
        try:
            response = PlaceOrderResponse(**self.client.place_order(
                market=pair_symbol,
                side="buy",
                size=tokens_number,
                type="market",
                price=None
            ))
            self.log.info(f"Buy order: {response.size} coins at {response.market} market")
            return response
        except Exception as e:
            self.log.error(f"Buy order {pair_symbol} for {tokens_number} coins: {e}")

    def get_current_market_price(self, pair_symbol: str):
        try:
            response = self.client.get_market(pair_symbol)["price"]
            self.log.info(f"Current {pair_symbol} market price: {response}")
            return response
        except Exception as e:
            self.log.error(f"Current market price: {e}")

    def sell(self, pair_symbol: str, coins_numbers: float, price=None,
             order_type: str = "market") -> PlaceOrderResponse:
        try:
            response = PlaceOrderResponse(**self.client.place_order(
                market=pair_symbol,
                side="sell",
                size=coins_numbers,
                type=order_type,
                price=price
            ))
            self.log.info(f"{order_type} sell order: {response.size} coins at {response.market} market")
            return response
        except Exception as e:
            self.log.error(f"Fail {order_type} sell order {pair_symbol} for {coins_numbers} coins: {e}")

    def cancel_orders(self, pair_symbol: str):
        try:
            self.client.cancel_orders(pair_symbol)
            self.log.info(f"Cancel order for {pair_symbol} market")
        except Exception as e:
            self.log.error(f"Cancel order for {pair_symbol} market: {e}")
