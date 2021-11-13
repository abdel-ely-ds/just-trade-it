import os
import warnings
from typing import Type
import pandas as pd
from tqdm import tqdm

from t_nachine.backtester.core.backtest import Backtest as BacktestCore
from t_nachine.backtester.core.strategy import Strategy
from t_nachine.backtester.wrapper.utils import (
    post_process_stats,
    pre_process_path,
    pre_process_stock,
    set_log_folder,
)
from t_nachine.constants import TRADES

warnings.filterwarnings("ignore")
LOG_FOLDER = "logs"


class Backtest:
    def __init__(
        self,
        log_folder: str = LOG_FOLDER,
        cash: int = 20_000,
        commission: int = 0.0,
        exclusive_orders: bool = False,
    ):

        self._bt = BacktestCore(
            cash=cash, commission=commission, exclusive_orders=exclusive_orders
        )
        self._log_folder = log_folder

    @property
    def bt(self):
        return self._bt

    @property
    def log_folder(self):
        return self._log_folder

    def _run(
        self, strategy: Type[Strategy], stock_path: str, symbol: str
    ) -> pd.DataFrame:

        stats = self.bt.run(
            data=pre_process_stock(pd.read_csv(stock_path)), strategy=strategy
        )
        return post_process_stats(stats[TRADES], symbol)

    def run(self, strategy: Type[Strategy], stock_path: str) -> pd.DataFrame:
        """
        Args:
            strategy: strategy to backtest
            stock_path: path to a stock or a folder of stocks
        Returns:
            [pd.DataFrame]: the results of the backtest for each stock
        """
        prefix_path, stock_names = pre_process_path(stock_path)
        backtest_results = pd.DataFrame()

        for stock_name in tqdm(stock_names):
            try:
                backtest_results = backtest_results.append(
                    self._run(
                        strategy,
                        os.path.join(prefix_path, stock_name),
                        stock_name.split(".")[0],
                    )
                )
            except IndexError:
                pass
        backtest_results = backtest_results.reset_index(drop=True)
        backtest_results.drop_duplicates(inplace=True)
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
            ),
            index=False,
        )
