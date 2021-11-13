import os
from functools import lru_cache
from typing import Callable, Dict, Tuple, List, Optional

import numpy as np
import pandas as pd
from tqdm import tqdm

from t_nachine.backtester import Trade
from t_nachine.backtester.wrapper.utils import pre_process_path, pre_process_stock
from t_nachine.constants import *
from t_nachine.optimization.datasets_utils.dataset import Dataset
from t_nachine.optimization.datasets_utils.splitters import random_splitter

FEATURES = ['stochs', 'rsi', 'macd50_100', 'macd50_100_signal', 'bullish']


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

    def add_indicators(self):

        df_copy = self._backtest_results.copy()

        # set index from 0 to len(df)
        df_copy.index = range(len(df_copy))

        # supports
        for i in [50, 100]:
            df_copy['EMA' + str(i)] = df_copy['Close'].ewm(span=i, adjust=False).mean()

        df_copy['stochs'] = STOCHASTICS(df_copy, 5, 3)
        df_copy['rsi'] = RSI(df_copy['Close'], n=2)
        df_copy['macd50_100'] = df_copy['EMA50'] - df_copy['EMA100']
        df_copy['macd50_100_signal'] = df_copy['macd50_100'].ewm(span=9, adjust=False).mean()
        df_copy['bullish'] = df_copy['macd50_100'] > df_copy['macd50_100_signal']
        return df_copy

    @staticmethod
    def _build_features_of_a_trade(df: pd.DataFrame,
                                   trade: pd.DataFrame,
                                   history: int = 10,
                                   features: Optional[List[str]] = None
                                   ):

        if features is None:
            features = FEATURES

        # extra_columns
        extra_columns = ['EntryTime', 'ExitTime']

        x = pd.DataFrame(columns=[i for i in range(history * len(features))] + extra_columns)
        y = pd.DataFrame(columns=["label"] + extra_columns)

        if trade.EntryBar >= history:
            df_history = df.iloc[trade.EntryBar - history: trade.EntryBar]  # entry bar not included
            x = pd.DataFrame(df_history[features].to_numpy().reshape((1, history * len(features))))
            y = pd.DataFrame([trade.PnL >= 0])

            # add extra columns
            for extra in extra_columns:
                x[extra] = trade[extra]
                y[extra] = trade[extra]

        else:
            print(f'Entry Bar {trade.EntryBar} < {history}')

        return x, y

    def _build_features_of_trades_of_a_stock(self,
                                             df: pd.DataFrame,
                                             history: int = 10,
                                             features: Optional[List[str]] = None,
                                             symbol: str = "MSFT"
                                             ):
        if features is None:
            features = FEATURES

        x = pd.DataFrame()
        y = pd.DataFrame()

        trades = self[self._backtest_results[SYMBOL] == symbol]
        for i, t in trades.iterrows():
            x_trade, y_trade = self._build_features_of_a_trade(df=df,
                                                               trade=t,
                                                               history=history,
                                                               features=features
                                                               )

            x = x.append(x_trade)
            y = y.append(y_trade)

        x['Symbol'] = [symbol for _ in range(len(x))]
        y['Symbol'] = [symbol for _ in range(len(x))]

        return x, y

    def build(self,
              path: str,
              history: int = 10,
              features: List[str] = None
              ):

        x_features = pd.DataFrame()
        y_features = pd.DataFrame()

        symbols = self._backtest_results[SYMBOL].unique()
        for s in tqdm(symbols):
            # read and add indicators
            df = pd.read_csv(os.path.join(path, s))
            df = self.add_indicators(df)

            x_stock, y_stock = self._build_features_of_trades_of_a_stock(df=df,
                                                                         symbol=s,
                                                                         history=history,
                                                                         features=features
                                                                         )

            x_features = x_features.append(x_stock)
            y_features = y_features.append(y_stock)

        return x_features, y_features

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
