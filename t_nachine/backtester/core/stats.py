from __future__ import annotations

from typing import List

import pandas as pd
import numpy as np

from t_nachine.backtester.core.strategy import Strategy
from t_nachine.backtester.core.backtesting import Trade
from t_nachine.constants import TRADES_ATTRIBUTES


def geometric_mean(returns):
    returns = returns.fillna(0) + 1
    return (
        0
        if np.any(returns <= 0)
        else np.exp(np.log(returns).sum() / (len(returns) or np.nan)) - 1
    )


class Stats(pd.Series):
    def __repr__(self):
        # Prevent expansion due to _equity and _trades dfs
        with pd.option_context("max_colwidth", 20):
            return super().__repr__()

    @staticmethod
    def compute_stats(
            data: pd.DataFrame, equity, trades: List[Trade], strategy: Strategy, cash: float
    ) -> Stats:

        index = data.index

        equity = pd.Series(equity).bfill().fillna(cash).values

        equity_df = pd.DataFrame(
            {"Equity": equity},
            index=index,
        )
        trades_dict = {
                "Size": [t.size for t in trades],
                "EntryBar": [t.entry_bar for t in trades],
                "ExitBar": [t.exit_bar for t in trades],
                "OneR": [t.one_r for t in trades],
                "SlPrice": [t.sl for t in trades],
                "TpPrice": [t.tp for t in trades],
                "EntryPrice": [t.entry_price for t in trades],
                "ExitPrice": [t.exit_price for t in trades],
                "MaxPnL": [t.max_pnl for t in trades],
                "MaxNegativePnl": [t.max_negative_pnl for t in trades],
                "PnL": [t.pl for t in trades],
                "ReturnPct": [t.pl_pct for t in trades],
                "EntryTime": [t.entry_time for t in trades],
                "ExitTime": [t.exit_time for t in trades],
            }
        for feature in TRADES_ATTRIBUTES:
            try:
                trades_dict[feature] = [getattr(t, feature) for t in trades]
            except AttributeError:
                pass

        trades_df = pd.DataFrame(trades_dict)

        pl = trades_df["PnL"]
        returns = trades_df["ReturnPct"]

        s = pd.Series(dtype=object)
        s.loc["Start"] = index[0]
        s.loc["End"] = index[-1]
        s.loc["Duration"] = s.End - s.Start

        have_position = np.repeat(0, len(index))
        for t in trades:
            have_position[t.entry_bar: t.exit_bar + 1] = 1  # type: ignore

        s.loc["Exposure Time [%]"] = (
                have_position.mean() * 100
        )  # In "n bars" time, not index time
        s.loc["Equity Final [$]"] = equity[-1]
        s.loc["Equity Peak [$]"] = equity.max()
        s.loc["Return [%]"] = (equity[-1] - equity[0]) / equity[0] * 100
        c = data.Close.values
        s.loc["Buy & Hold Return [%]"] = (c[-1] - c[0]) / c[0] * 100  # long-only return

        day_returns = gmean_day_return = annual_trading_days = np.array(np.nan)
        if index.is_all_dates:
            day_returns = equity_df["Equity"].resample("D").last().dropna().pct_change()
            gmean_day_return = geometric_mean(day_returns)
            annual_trading_days = (
                365
                if index.dayofweek.to_series().between(5, 6).mean() > 2 / 7 * 0.6
                else 252
            )

        annualized_return = (1 + gmean_day_return) ** annual_trading_days - 1
        s.loc["Return (Ann.) [%]"] = annualized_return * 100
        s.loc["Volatility (Ann.) [%]"] = (
                np.sqrt(
                    (
                            day_returns.var(ddof=int(bool(day_returns.shape)))
                            + (1 + gmean_day_return) ** 2
                    )
                    ** annual_trading_days
                    - (1 + gmean_day_return) ** (2 * annual_trading_days)
                )
                * 100
        )  # noqa: E501
        # s.loc['Return (Ann.) [%]'] = gmean_day_return * annual_trading_days * 100
        # s.loc['Risk (Ann.) [%]'] = day_returns.std(ddof=1) * np.sqrt(annual_trading_days) * 100

        # Our Sharpe mismatches `empyrical.sharpe_ratio()` because they use arithmetic mean return
        # and simple standard deviation
        s.loc["Sharpe Ratio"] = np.clip(
            s.loc["Return (Ann.) [%]"] / (s.loc["Volatility (Ann.) [%]"] or np.nan),
            0,
            np.inf,
        )  # noqa: E501
        # Our Sortino mismatches `empyrical.sortino_ratio()` because they use arithmetic mean return
        s.loc["Sortino Ratio"] = np.clip(
            annualized_return
            / (
                    np.sqrt(np.mean(day_returns.clip(-np.inf, 0) ** 2))
                    * np.sqrt(annual_trading_days)
            ),
            0,
            np.inf,
        )  # noqa: E501
        s.loc["# Trades"] = n_trades = len(trades)
        s.loc["Win Rate [%]"] = win_rate = (
            np.nan if not n_trades else (pl > 0).sum() / n_trades * 100
        )  # noqa: E501
        s.loc["Best Trade [%]"] = returns.max() * 100
        s.loc["Worst Trade [%]"] = returns.min() * 100
        mean_return = geometric_mean(returns)
        s.loc["Profit Factor"] = returns[returns > 0].sum() / (
                abs(returns[returns < 0].sum()) or np.nan
        )  # noqa: E501
        s.loc["Expectancy [%]"] = returns[returns > 0].mean() * win_rate + returns[
            returns < 0
            ].mean() * (100 - win_rate)
        s.loc["SQN"] = np.sqrt(n_trades) * pl.mean() / (pl.std() or np.nan)
        s.loc["_strategy"] = strategy
        s.loc["_equity_curve"] = equity_df
        s.loc["_trades"] = trades_df

        s = Stats(s)
        return s
