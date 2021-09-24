import math
from collections import OrderedDict

import numpy as np

STOP_LOSS_LOOKUP_TABLE = OrderedDict(
    [(5, 0.01), (10, 0.02), (50, 0.03), (100, 0.05), (math.inf, 0.10)]
)


class RiskManger:
    """
    Class that manages risk
    """

    def __init__(
        self,
        risk_to_reward: float = 2.0,
        risk_per_trade: float = 0.01,
        sl_lookup_table: dict = STOP_LOSS_LOOKUP_TABLE,
    ):
        self._risk2reward = risk_to_reward
        self._risk = risk_per_trade
        self._sl_lookup_table = sl_lookup_table

    def stop_loss(self, price: float) -> float:
        """
        it calculates the stop loss based on the sl_lookup table

        Args:
            price (float): the price of the triggering candle
        Returns:
            [float]: the stop loss
        """
        for key_price, value in self._sl_lookup_table.items():
            if price < key_price:
                return price - value

    def target(self, entry: float, stop_loss: float) -> float:
        """
        it computes the target price

        Args:
            entry (float): entry price
            stop_loss (float): stop loss price

        Returns:
            float: the target price
        """
        one_r = RiskManger.one_r(entry, stop_loss)
        return entry + self._risk2reward * one_r

    @staticmethod
    def one_r(entry: float, stop_loss: float) -> float:
        """
        it computes the one R distance
        Args:
            entry (float): entry price
            stop_loss (float): the stop loss price

        Returns:
            float: one_r distance
        """
        return entry - stop_loss

    def entry_price(self, price: float, limit: float = 1) -> float:
        """
        computes entry price

        Args:
            price (float): price of trigging candle
            limit (float): 1 entry price

        Returns:
            float: entry price
        """
        for key_price, value in self._sl_lookup_table.items():
            if price < key_price:
                return price + limit * value

    def shares(self, capital: float, entry: float, stop_loss: float) -> int:
        """
        computes number of shares to buy

        Args:
            capital (float): initial capital or equity
            entry (float): entry price
            stop_loss (float): stop loss price
        Returns:
            [int]: share size
        """
        return np.ceil(self._risk * capital / self.one_r(entry, stop_loss))
