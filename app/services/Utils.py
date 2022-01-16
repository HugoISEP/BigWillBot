import json
from math import floor
from typing import List

import pandas as pd


class Utils:

    NUMBER_OF_VALUES = 200
    NOTIFICATION_TOPIC = "BIG_WILL"

    @staticmethod
    def load_json_pair_symbols() -> List[str]:
        with open("app/resources/pair_symbols.json", 'r') as f:
            return json.load(f)["ftxClassicPair"]

    @staticmethod
    def clean_data(data: dict) -> pd.DataFrame():
        df = pd.DataFrame(
            columns=["startTime", "open", "high", "low", "close", "volume"],
            data=data
        )
        df.drop(range(0, Utils.NUMBER_OF_VALUES, 2), axis="index", inplace=True)

        df["close"] = pd.to_numeric(df["close"])
        df["high"] = pd.to_numeric(df["high"])
        df["low"] = pd.to_numeric(df["low"])
        df["open"] = pd.to_numeric(df["open"])
        df = df.set_index(df["startTime"])

        del df["startTime"]
        del df["volume"]

        return df

    @staticmethod
    def get_results_data_frame():
        return pd.DataFrame(columns=["date", "transaction_type", "symbol_pair", "position", "reason", "price", "fee", "fiat", "coins"])

    @staticmethod
    def truncate(n: float, decimals=3):
        return floor(float(n) * 10 ** decimals) / 10 ** decimals

    @staticmethod
    def get_token_name_from_market_name(market: str) -> str:
        return market.split("/")[0]
