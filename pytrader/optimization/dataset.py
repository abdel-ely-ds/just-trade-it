from dataclasses import dataclass
from functools import lru_cache
from typing import Callable, Dict, Tuple

import numpy as np
import pandas as pd
from sklearn.utils import shuffle
from tqdm import tqdm

from pytrader.backtester.wrapper.utils import pre_process_path, pre_process_stock
from pytrader.optimization.analysis import Constants


@dataclass
class Train:
    x: pd.DataFrame
    y: pd.Series


@dataclass
class Test:
    x: pd.DataFrame
    y: pd.Series


class Dataset:
    def __init__(
        self,
        backtest_results: pd.DataFrame,
        stock_path: str,
        indicators: Dict[str, Callable[..., pd.Series]],
        constants: Constants = Constants(),
    ):
        self._backtest_results = backtest_results.copy()
        self._stock_path = stock_path
        self._indicators = indicators
        self._features = list(self._indicators.keys())
        self._constants = constants
        self._n_features = len(self._features)

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
    def features(self):
        return self._features

    @property
    def constants(self):
        return self._constants

    def _enrich_stock(self, stock: pd.DataFrame) -> None:
        for ind_name, ind in self.indicators:
            stock[ind_name] = ind(stock)

    @staticmethod
    def _transform_stock(stock):
        for f in ["Open", "High", "Low", "Close"]:
            stock[f] = (stock[f].pct_change(1)).cumsum()
        stock.dropna(inplace=True)

    @lru_cache(maxsize=100)
    def build(self, history: int = 10) -> Tuple[np.array, np.array]:
        prefix_path, stock_names = pre_process_path(self.stock_path)
        x = np.array(np.zeros((1, history * len(self.indicators))))
        y = np.array(
            np.zeros(
                1,
            )
        )
        for stock_name in tqdm(stock_names):
            stock = pre_process_stock(os.path.join(prefix_path, stock_name))
            x_bis, y_bis = self._build(stock, stock_name, history=history)
            x, y = x.append(x_bis, axis=0), y.append(y_bis, axis=0)
        return x[1:], y[1:]

    def _build(
        self, stock: pd.DataFrame, symbol: str, history: int = 10
    ) -> Tuple[np.array, np.array]:
        x = np.array(np.zeros((1, history * len(self.indicators))))
        y = np.array(
            np.zeros(
                1,
            )
        )

        for ind, trade in self.backtest_results[
            self.backtest_results["symbol"] == symbol
        ].iterrows():
            entry_bar = int(trade[self.constants.ENTRY_BAR])
            x = np.append(
                x,
                stock.iloc[entry_bar - self._n_features : entry_bar][self.features]
                .to_numpy()
                .reshape((1, self._n_features * len(self.features))),
                axis=0,
            )
            y = np.append(y, trade[self.constants.IS_LOSING])

        return x, y

    @staticmethod
    def random_split(
        x: pd.DataFrame, y: pd.Series, random_state: int = 0, percentage: float = 0.8
    ) -> Tuple[Train, Test]:
        shuffled_x, shuffled_y = shuffle(x, random_state=random_state), shuffle(
            y, random_state=random_state
        )
        index = int(len(shuffled_x) * percentage)
        return Train(shuffled_x[:index], shuffled_y[:index]), Test(
            shuffled_x[index:], shuffled_y[index:]
        )
