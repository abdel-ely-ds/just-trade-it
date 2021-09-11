import json
import os
from typing import Type

import pandas as pd
from tqdm import tqdm

from pytrader.backtester.core import Backtest, Strategy
from pytrader.backtester.wrapper.available_analysis import ANALYSIS_ATTRIBUTES
from pytrader.backtester.wrapper.exceptions import AnalysisNotAvailableError
from pytrader.backtester.wrapper.log_handler import LogHandler

from .utils import (
    post_process_stats,
    pre_process_path,
    pre_process_stock,
    update_strategy,
)


class BacktestWrapper:
    def __init__(
        self,
        strategy: Type[Strategy],
        analysis_type: str = "MACRO",
        strategy_attrs: dict = None,
        log_handler: LogHandler = LogHandler(),
        cash: int = 20_000,
        commission: int = 0.0,
        exclusive_orders: bool = False,
    ):

        self._strategy = strategy
        self._backtest_name = backtest_name
        self._log_handler = log_handler
        self._cash = cash
        self._commission = commission
        self._exclusive_orders = exclusive_orders
        self._analysis_type = analysis_type
        self._strategy_attrs = strategy_attrs
        self._check_analysis()

    @property
    def strategy(self):
        return self._strategy

    @property
    def log_handler(self):
        return self._log_handler

    @property
    def cash(self):
        return self._cash

    @property
    def commission(self):
        return self._commission

    @property
    def exclusive_orders(self):
        return self._exclusive_orders

    @property
    def analysis_type(self):
        return self._analysis_type

    @property
    def strategy_attrs(self):
        return self._strategy_attrs

    def _check_analysis(self):
        if self._analysis_type not in ANALYSIS_ATTRIBUTES:
            raise AnalysisNotAvailableError(self._analysis_type)

    def _run(self, stock_path: str) -> json:
        """
        Args:
            stock_path (str):  the path to a stock

        Returns:
            [json]: the results of the backtest
        """

        bt = Backtest(
            pre_process_stock(pd.read_csv(stock_path)),
            update_strategy(self._strategy, self._strategy_attrs),
            cash=self._cash,
            commission=self._commission,
            exclusive_orders=self._exclusive_orders,
        )
        stats = bt.run()
        return post_process_stats(stats[ANALYSIS_ATTRIBUTES[self._analysis_type]])

    def run(self, stock_path: str) -> dict:
        """
        Args:
            stock_path: path to a stock or a folder of stocks
        Returns:
            [dict]: the results of the backtest for each stock
        """
        prefix_path, stock_names = pre_process_path(stock_path)
        backtest_results = {}
        for stock_name in tqdm(stock_names):
            backtest_results[stock_name] = self._run(
                os.path.join(prefix_path, stock_name)
            )

        return backtest_results

    def log_results(self, backtest_results: dict, backtest_name: str) -> None:
        """
        It creates a log folder where results would be saved to be analyzed later

        Args:
            backtest_results (dict): results of the backtest output of the method run
            backtest_name (str): the name on which the backtest would be saved

        """
        self._log_handler.log_backtest(
            backtest_name=backtest_name,
            backtest_results=backtest_results,
            strategy_attrs=self._strategy_attrs,
        )
