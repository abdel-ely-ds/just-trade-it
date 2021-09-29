import os
import warnings
from typing import Type

import pandas as pd
from tqdm import tqdm

from pytrader.backtester.core import Backtest, Strategy
from pytrader.backtester.wrapper.available_analysis import ANALYSIS_ATTRIBUTES
from pytrader.backtester.wrapper.exceptions import AnalysisNotAvailableError
from pytrader.backtester.wrapper.utils import (
    post_process_stats,
    pre_process_path,
    pre_process_stock,
    set_log_folder,
)

warnings.filterwarnings("ignore")
LOG_FOLDER = "logs"


class BacktestWrapper:
    def __init__(
        self,
        strategy: Type[Strategy],
        analysis_type: str = "MACRO",
        log_folder: str = LOG_FOLDER,
        cash: int = 20_000,
        commission: int = 0.0,
        exclusive_orders: bool = False,
    ):

        self._strategy = strategy
        self._analysis_type = analysis_type
        self._log_folder = log_folder
        self._cash = cash
        self._commission = commission
        self._exclusive_orders = exclusive_orders
        self._check_analysis()

    @property
    def strategy(self):
        return self._strategy

    @property
    def analysis_type(self):
        return self._analysis_type

    @property
    def log_folder(self):
        return self._log_folder

    @property
    def cash(self):
        return self._cash

    @property
    def commission(self):
        return self._commission

    @property
    def exclusive_orders(self):
        return self._exclusive_orders

    def _check_analysis(self):
        if self.analysis_type not in ANALYSIS_ATTRIBUTES:
            raise AnalysisNotAvailableError(self.analysis_type)

    def _run(self, stock_path: str, symbol: str, plot: bool = False) -> pd.DataFrame:
        """
        Args:
            stock_path (str):  the path to a stock

        Returns:
            [json]: the results of the backtest
        """
        bt = Backtest(
            pre_process_stock(pd.read_csv(stock_path)),
            strategy=self._strategy,
            cash=self._cash,
            commission=self._commission,
            exclusive_orders=self._exclusive_orders,
        )
        stats = bt.run()
        if plot:
            bt.plot()
        return post_process_stats(
            stats[ANALYSIS_ATTRIBUTES[self.analysis_type]], symbol
        )

    def run(self, stock_path: str, plot: bool = False) -> pd.DataFrame:
        """
        Args:
            stock_path: path to a stock or a folder of stocks
            plot: plot or not
        Returns:
            [pd.DataFrame]: the results of the backtest for each stock
        """
        prefix_path, stock_names = pre_process_path(stock_path)
        backtest_results = pd.DataFrame()

        for stock_name in tqdm(stock_names):
            try:
                backtest_results = backtest_results.append(
                    self._run(
                        os.path.join(prefix_path, stock_name),
                        stock_name.split(".")[0],
                        plot=plot,
                    )
                )
            except:
                pass
        backtest_results = backtest_results.reset_index(drop=True)
        return backtest_results

    def log_results(
        self, backtest_results: pd.DataFrame, backtest_name: str, ext: str = ".csv"
    ) -> None:
        """
        It creates a log folder where results would be saved to be analyzed later

        Args:
            backtest_results (pd.DataFrame): results of the backtest output of the method run
            backtest_name (str): the name on which the backtest would be saved
            ext (str): extension of the file
        """
        backtest_results.to_csv(
            os.path.join(
                set_log_folder(log_folder=self._log_folder), backtest_name + ext
            )
        )
