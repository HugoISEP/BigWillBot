import logging
import time
from typing import List

import ta
from pandas import Series, DataFrame

from app.models.CryptoInfo import CryptoInfo
from app.services.Ftx import Ftx
from app.services.Utils import Utils


class BigWill:
    ao_param1 = 5
    ao_param2 = 32
    stoch_window = 14
    will_window = 14
    willr_buy_limit = -85
    willr_sell_limit = -10
    stoch_over_bought = 0.8
    stoch_over_sold = 0.2
    stop_loss_pct = 0.05
    take_profit_pct = 0.15
    max_shop = 35
    max_positions = 3
    log = logging.getLogger("BIG_WILL")

    def buy_condition(self, row: Series, previous_row=None) -> bool:
        return 0 <= row['AO'] < previous_row['AO'] and row['WillR'] < self.willr_buy_limit and row['EMA50'] > row['EMA100']

    # -- Condition to SELL market --
    def sell_condition(self, row: Series, previous_row=None) -> bool:
        return (row['AO'] < 0 and row['STOCH_RSI'] > self.stoch_over_sold) or row['WillR'] > self.willr_sell_limit

    def set_indicators(self, df: DataFrame):
        df['AO'] = ta.momentum.awesome_oscillator(
            df['high'],
            df['low'],
            window1=self.ao_param1,
            window2=self.ao_param2
        )
        df['STOCH_RSI'] = ta.momentum.stochrsi(close=df['close'], window=self.stoch_window)
        df['WillR'] = ta.momentum.williams_r(high=df['high'], low=df['low'], close=df['close'], lbp=self.will_window)
        df['EMA50'] = ta.trend.ema_indicator(close=df['close'], window=50)
        df['EMA100'] = ta.trend.ema_indicator(close=df['close'], window=100)

    def run(self):
        # -- Value initialisation --
        client = Ftx()
        pair_symbols = Utils.load_json_pair_symbols()
        balances_list = client.get_balances()
        total_usd_balance = sum([balance.usdValue for balance in balances_list])
        cryptos_in_buy_position: List[CryptoInfo] = []
        cryptos_in_sell_position: List[CryptoInfo] = []

        # Add crypto pair from json file
        # Get the data from all cryptos
        for pair in pair_symbols:
            data = client.get_data_from_pair(pair)
            df = Utils.clean_data(data)
            self.set_indicators(df)

            coin_symbol = pair.split("/")[0]

            optional_coins_number = [balance for balance in balances_list if balance.coin == coin_symbol]
            coins_number = optional_coins_number[0].free if len(optional_coins_number) == 1 else 0.0
            coins_usd_value = optional_coins_number[0].usdValue if len(optional_coins_number) == 1 else 0.0
            crypto_info = CryptoInfo(
                **{"symbol": coin_symbol, "coins": coins_number, "usd_value": coins_usd_value, "data": df})

            if crypto_info.usd_value < 0.05 * total_usd_balance:
                cryptos_in_buy_position.append(crypto_info)
            else:
                cryptos_in_sell_position.append(crypto_info)

        current_positions = len(cryptos_in_sell_position)

        self.log.info(
            f"cryptos in sell position: {len(cryptos_in_sell_position)}, "
            f"cryptos in buy position: {len(cryptos_in_buy_position)}"
        )

        # BUY
        if current_positions < self.max_positions:
            # Iterate through balance which has coin
            for crypto_info in cryptos_in_buy_position:
                current_row = crypto_info.data.iloc[-1]
                previous_row = crypto_info.data.iloc[-2]

                if self.buy_condition(current_row, previous_row):
                    market_name = crypto_info.symbol + "/USD"
                    client.cancel_orders(market_name)
                    time.sleep(2)

                    buy_quantity_in_usd = total_usd_balance / (self.max_positions - current_positions)
                    current_price = client.get_current_market_price(market_name)
                    quantity_to_buy = Utils.truncate(float(buy_quantity_in_usd) / current_price)

                    response = client.buy(
                        market_name,
                        quantity_to_buy
                    )

                    # Place Take Profit
                    client.sell(
                        market_name,
                        Utils.truncate(response.size),
                        current_price + self.take_profit_pct * current_price,
                        "limit"
                    )

        # SELL
        if len(cryptos_in_sell_position) > 0:
            for crypto_info in cryptos_in_sell_position:
                current_row = crypto_info.data.iloc[-1]
                previous_row = crypto_info.data.iloc[-2]

                if self.sell_condition(current_row):
                    market_name = crypto_info.symbol + "/USD"
                    client.cancel_orders(market_name)
                    time.sleep(2)

                    client.sell(
                        market_name,
                        Utils.truncate(crypto_info.coins)
                    )
