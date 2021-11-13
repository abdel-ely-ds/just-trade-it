from functools import partial

import pandas as pd
import numpy as np
from typing import Union, Type

from t_nachine.backtester.core._plotting import plot
from t_nachine.backtester.core._util import try_, _Data, _Indicator
from t_nachine.backtester.core.backtesting import _Broker, _OutOfMoneyError
from t_nachine.backtester.core.stats import Stats
from t_nachine.backtester.core.strategy import Strategy
from t_nachine.backtester.core.validate_data import validate_data


class Backtest:

    def __init__(
            self,
            # data: pd.DataFrame,
            # strategy: Type[Strategy],
            *,
            cash: float = 10_000,
            commission: float = 0.0,
            margin: float = 1.0,
            trade_on_close=False,
            hedging=False,
            exclusive_orders=False,
    ):
        self._cash = cash
        self._broker = partial(
            _Broker,
            cash=cash,
            commission=commission,
            margin=margin,
            trade_on_close=trade_on_close,
            hedging=hedging,
            exclusive_orders=exclusive_orders,

        )
        self._strategy = None
        self._data = None
        self._results = None
        self._stats = Stats()

    def run(self, data: pd.DataFrame, strategy: Type[Strategy], **kwargs) -> pd.Series:

        data = validate_data(data, self._cash)
        self._data: pd.DataFrame = data

        self._strategy = strategy

        data = _Data(self._data.copy(deep=False))
        broker: _Broker = self._broker(data=data, index=data.index)
        strategy: Strategy = self._strategy(broker, data, kwargs)

        strategy.init()
        data._update()  # Strategy.init might have changed/added to data.df

        # Indicators used in Strategy.next()
        indicator_attrs = {
            attr: indicator
            for attr, indicator in strategy.__dict__.items()
            if isinstance(indicator, _Indicator)
        }.items()

        # Skip first few candles where indicators are still "warming up"
        # +1 to have at least two entries available
        start = 1 + max(
            (
                np.isnan(indicator.astype(float)).argmin(axis=-1).max()
                for _, indicator in indicator_attrs
            ),
            default=0,
        )

        # Disable "invalid value encountered in ..." warnings. Comparison
        # np.nan >= 3 is not invalid; it's False.
        with np.errstate(invalid="ignore"):

            for i in range(start, len(self._data)):
                # Prepare data and indicators for `next` call
                data._set_length(i + 1)
                for attr, indicator in indicator_attrs:
                    # Slice indicator on the last dimension (case of 2d indicator)
                    setattr(strategy, attr, indicator[..., : i + 1])

                # Handle orders processing and broker stuff
                try:
                    broker.next()
                except _OutOfMoneyError:
                    break

                # Next tick, a moment before bar close
                strategy.next()
            else:
                # Close any remaining open trades so they produce some stats
                for trade in broker.trades:
                    trade.close()

                # Re-run broker one last time to handle orders placed in the last strategy
                # iteration. Use the same OHLC values as in the last broker iteration.
                if start < len(self._data):
                    try_(broker.next, exception=_OutOfMoneyError)

            # Set data back to full length
            # for future `indicator._opts['data'].index` calls to work
            data._set_length(len(self._data))

            self._results = self._stats.compute_stats(data=self._data,
                                                      equity=broker.equity,
                                                      trades=broker.closed_trades,
                                                      strategy=strategy,
                                                      cash=broker._cash)
        return self._results

    def plot(
            self,
            *,
            results: pd.Series = None,
            filename=None,
            plot_width=None,
            plot_equity=True,
            plot_return=False,
            plot_pl=True,
            plot_volume=True,
            plot_drawdown=False,
            smooth_equity=False,
            relative_equity=True,
            superimpose: Union[bool, str] = True,
            resample=True,
            reverse_indicators=False,
            show_legend=True,
            open_browser=True,
    ):
        if results is None:
            if self._results is None:
                raise RuntimeError("First issue `backtest.run()` to obtain results.")
            results = self._results

        plot(
            results=results,
            df=self._data,
            indicators=results._strategy._indicators,
            filename=filename,
            plot_width=plot_width,
            plot_equity=plot_equity,
            plot_return=plot_return,
            plot_pl=plot_pl,
            plot_volume=plot_volume,
            plot_drawdown=plot_drawdown,
            smooth_equity=smooth_equity,
            relative_equity=relative_equity,
            superimpose=superimpose,
            resample=resample,
            reverse_indicators=reverse_indicators,
            show_legend=show_legend,
            open_browser=open_browser,
        )
