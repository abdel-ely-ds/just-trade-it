import random
from functools import lru_cache

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as st
from tqdm import tqdm

from pytrader.constants import *

pd.options.display.float_format = "{:.3f}".format


class Analyzer:
    def __init__(self, backtest_results: pd.DataFrame):
        self._backtest_results = self._pre_process_results(backtest_results)
        self._enrich_results()

    def win_rate(self) -> float:
        return self._backtest_results[IS_LOSING].mean()

    def stats(self) -> pd.DataFrame:
        func = [MEAN, MIN, MAX, STD]
        columns = [DURATION, RISK_TO_REWARD]
        return self._backtest_results.groupby(IS_LOSING)[columns].agg(func)

    def missed_tp_by(self) -> pd.Series:
        """
        Computes maximum positive pnl of losing trades
        (ex: a losing trades that at some point had a pnl=+1.2*One_R -> distance_to_tp = risk_to_reward * One_R - PNL

        """
        losing_trades = self._backtest_results[IS_LOSING]
        return (losing_trades[MAX_PNL] / losing_trades[ONE_R]).describe()

    def plot_equity_curve(self, capital: float = 10_000, symbol: str = "") -> None:
        """
        It plots the equity of a stock using the results found using the backtest
        Args:
            capital (float): initial capital
            symbol (str): stock symbol if it's not passed we'll choose randomly

        Returns:
        """

        if not symbol:
            symbol = random.choice(self._backtest_results[SYMBOL].unique())

        stock = self._backtest_results[self._backtest_results[SYMBOL] == symbol]
        equity_curve = stock.groupby(EXIT_TIME)[PNL].sum()
        equity_curve.iloc[0] = equity_curve.iloc[0] + capital
        plt.plot(equity_curve.cumsum())
        plt.grid()
        plt.title(f"Equity Curve of {symbol.upper()}")
        plt.xlabel("time")
        plt.ylabel("equity €")

    def ruin_probability(
        self,
        capital: float = 10_000,
        ruin_level: float = 0.5,
        risk_per_trade: float = 0.01,
        nb_simulations: int = 1000,
        nb_trades: int = 1000,
    ) -> float:
        """ "
        Args:
            capital (float): initial capital
            ruin_level (float): the ruin is triggered if your equity is smaller than ruin_level * capital
            risk_per_trade (float): ris taken on each trade
            nb_simulations (int): number of simulations to run
            nb_trades (int): number of trades taken

        """

        equity_curves = (
            self._equity_curves_simulation(
                capital=capital,
                risk_per_trade=risk_per_trade,
                nb_simulations=nb_simulations,
                nb_trades=nb_trades,
            )
            <= ruin_level * capital
        )

        return equity_curves.any(axis=1).mean()

    def plot_simulated_equity_curve(
        self,
        capital: float = 10_000,
        risk_per_trade: float = 0.01,
        nb_simulations: int = 1000,
        nb_trades: int = 1000,
    ) -> None:

        equity_curves = self._equity_curves_simulation(
            capital=capital,
            risk_per_trade=risk_per_trade,
            nb_simulations=nb_simulations,
            nb_trades=nb_trades,
        )

        mean_equity_curve = equity_curves.mean(axis=0)
        conf_int = st.t.interval(
            0.99,
            equity_curves.shape[1] - 1,
            loc=equity_curves.mean(axis=0),
            scale=st.sem(equity_curves, axis=0),
        )
        lower_band = [conf_int[0][i] for i in range(nb_trades)]
        upper_band = [conf_int[1][i] for i in range(nb_trades)]
        plt.plot(mean_equity_curve)
        plt.plot(lower_band)
        plt.plot(upper_band)
        plt.grid()

    @lru_cache(maxsize=100)
    def _equity_curves_simulation(
        self,
        capital: float = 10_000,
        risk_per_trade: float = 0.01,
        nb_simulations: int = 1000,
        nb_trades: int = 1000,
    ) -> pd.DataFrame:

        # risk to reward distribution
        risk_value_counts = self._backtest_results[RISK_TO_REWARD].value_counts(
            normalize=True
        )
        dist = risk_value_counts.to_list()
        risk_to_rewards = risk_value_counts.index.to_list()
        expected_returns = [risk_per_trade * capital * r2r for r2r in risk_to_rewards]

        equity_curves = []
        for _ in tqdm(range(nb_simulations)):
            random_trades = [
                np.random.choice(expected_returns, p=dist) for _ in range(nb_trades)
            ]
            equity_curve = self._compute_equity_curve(random_trades, capital)
            equity_curves.append(equity_curve)

        # each row is an equity
        return pd.concat(equity_curves, axis=1)

    @staticmethod
    def _compute_equity_curve(
        trades_returns: list[float], capital: float = 10_000
    ) -> pd.Series:
        """
        Used for simulation purpose
        Args
            trades_returns (list): simulated returns of each trade
            capital (float): initial capital

        Returns:
            (pd.Series): the equity
        """
        trades_returns[0] = trades_returns[0] + capital
        return pd.Series(trades_returns).cumsum()

    def _enrich_results(self) -> None:
        self._backtest_results[IS_LOSING] = self._backtest_results[PNL] > 0
        self._backtest_results[RISK_TO_REWARD] = (
            self._backtest_results[EXIT_PRICE] - self._backtest_results[ENTRY_PRICE]
        ) / self._backtest_results[ONE_R]

    @staticmethod
    def _pre_process_results(df) -> pd.DataFrame:
        df_copy = df.copy()
        df_copy.index.rename(SYMBOL, inplace=True)
        df_copy.reset_index(inplace=True)
        return df_copy
