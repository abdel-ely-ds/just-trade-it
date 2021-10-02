import os
from functools import lru_cache
from typing import Callable, Dict, Tuple

import numpy as np
import pandas as pd
from tqdm import tqdm

from tradeit.backtester.wrapper.utils import pre_process_path, pre_process_stock
from tradeit.constants import *
from tradeit.optimization.datasets_utils.dataset import Dataset
from tradeit.optimization.datasets_utils.splitters import random_splitter


class DatasetBuilder:
    def __init__(
        self,
        backtest_results: pd.DataFrame,
        stock_path: str,
        indicators: Dict[str, Callable[..., pd.Series]],
        splitter: Callable[..., Dataset] = random_splitter,
    ):
        self._backtest_results = backtest_results.copy()
        self._stock_path = stock_path
        self._indicators = indicators
        self._splitter = splitter
        self._features = list(self._indicators.keys())

    @property
    def backtest_results(self):
        return self._backtest_results

    @property
    def indicators(self):
        return self._indicators

    @property
    def stock_path(self):
        return self._stock_path

    @property
    def splitter(self):
        return self._splitter

    @property
    def features(self):
        return self._features

    @lru_cache(maxsize=100)
    def build(
        self,
        history: int = 2,
        random_state: int = 2021,
        percentage: float = 0.8,
    ) -> Dataset:
        prefix_path, stock_names = pre_process_path(self.stock_path)
        x = np.array(np.zeros((1, history * len(self.indicators))))
        y = np.array(
            np.zeros(
                1,
            )
        )
        for stock_name in tqdm(stock_names[:1]):
            try:
                stock = pre_process_stock(
                    pd.read_csv(os.path.join(prefix_path, stock_name))
                )
                x_tmp, y_tmp = self._build(
                    stock, stock_name.split(".")[0], history=history
                )
                x = np.append(x, x_tmp, axis=0)
                y = np.append(y, y_tmp, axis=0)

            except Exception as e:
                print("error: ", e)
                print("stock: ", stock_name)

        return self.splitter(
            x[1:], y[1:], random_state=random_state, percentage=percentage
        )

    def _build(
        self, stock: pd.DataFrame, symbol: str, history: int = 10
    ) -> Tuple[np.array, np.array]:
        x = np.array(np.zeros((1, history * len(self.features))))
        y = np.array(
            np.zeros(
                1,
            )
        )
        # build a a feature dataframe
        stock = self._build_features(stock)

        for ind, trade in self.backtest_results[
            self.backtest_results[SYMBOL] == symbol
        ].iterrows():
            entry_bar = int(trade[ENTRY_BAR])
            x = np.append(
                x,
                stock.iloc[entry_bar - history : entry_bar]
                .to_numpy()
                .reshape((1, history * len(self.features))),
                axis=0,
            )
            y = np.append(y, trade[IS_LOSING])

        return x[1:], y[1:]

    def _build_features(self, stock: pd.DataFrame) -> pd.DataFrame:
        transformed_stock = self._transform_stock(stock)
        for ind_name, ind in self.indicators.items():
            transformed_stock[ind_name] = ind(stock)
        return transformed_stock[self.features]

    @staticmethod
    def _transform_stock(stock):
        stock_copy = stock.copy()
        for f in [OPEN, HIGH, LOW, CLOSE]:
            stock_copy[f] = (stock_copy[f].pct_change(1)).cumsum()
        stock_copy.dropna(inplace=True)
        return stock_copy
