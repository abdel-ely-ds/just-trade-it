from functools import partial
from typing import Type, Union

from tradeit.backtester.core._plotting import plot
from tradeit.backtester.core._util import _Indicator, try_, _data_period
from tradeit.backtester.core.strategy import Strategy
import pandas as pd
from numbers import Number
import numpy as np
import warnings
from tradeit.backtester.core._broker import _Broker, _OutOfMoneyError
from tradeit.backtester.core._data import _Data


# noinspection PyProtectedMember
class Backtest:
    def __init__(
            self,
            data: pd.DataFrame,
            strategy: Type[Strategy],
            *,
            cash: float = 10_000,
            commission: float = 0.0,
            margin: float = 1.0,
            trade_on_close=False,
            hedging=False,
            exclusive_orders=False,
    ):

        if not (isinstance(strategy, type) and issubclass(strategy, Strategy)):
            raise TypeError("`strategy` must be a Strategy sub-type")
        if not isinstance(data, pd.DataFrame):
            raise TypeError("`data` must be a pandas.DataFrame with columns")
        if not isinstance(commission, Number):
            raise TypeError(
                "`commission` must be a float value, percent of " "entry order price"
            )

        data = data.copy(deep=False)

        # Convert index to datetime index
        if (
                not data.index.is_all_dates
                and not isinstance(data.index, pd.RangeIndex)
                # Numeric index with most large numbers
                and (
                data.index.is_numeric()
                and (data.index > pd.Timestamp("1975").timestamp()).mean() > 0.8
        )
        ):
            try:
                data.index = pd.to_datetime(data.index, infer_datetime_format=True)
            except ValueError:
                pass

        if "Volume" not in data:
            data["Volume"] = np.nan

        if len(data) == 0:
            raise ValueError("OHLC `data` is empty")
        if len(data.columns & {"Open", "High", "Low", "Close", "Volume"}) != 5:
            raise ValueError(
                "`data` must be a pandas.DataFrame with columns "
                "'Open', 'High', 'Low', 'Close', and (optionally) 'Volume'"
            )
        if data[["Open", "High", "Low", "Close"]].isnull().values.any():
            raise ValueError(
                "Some OHLC values are missing (NaN). "
                "Please strip those lines with `df.dropna()` or "
                "fill them in with `df.interpolate()` or whatever."
            )
        if np.any(data["Close"] > cash):
            warnings.warn(
                "Some prices are larger than initial cash value. Note that fractional "
                "trading is not supported. If you want to trade Bitcoin, "
                "increase initial cash, or trade μBTC or satoshis instead (GH-134).",
                stacklevel=2,
            )
        if not data.index.is_monotonic_increasing:
            warnings.warn(
                "Data index is not sorted in ascending order. Sorting.", stacklevel=2
            )
            data = data.sort_index()
        if not data.index.is_all_dates:
            warnings.warn(
                "Data index is not datetime. Assuming simple periods, "
                "but `pd.DateTimeIndex` is advised.",
                stacklevel=2,
            )

        self._data: pd.DataFrame = data
        self._broker = partial(
            _Broker,
            cash=cash,
            commission=commission,
            margin=margin,
            trade_on_close=trade_on_close,
            hedging=hedging,
            exclusive_orders=exclusive_orders,
            index=data.index,
        )
        self._strategy = strategy
        self._results = None

    def run(self, **kwargs) -> pd.Series:
        """
        Run the backtest. Returns `pd.Series` with results and statistics.

        Keyword arguments are interpreted as strategy parameters.

            >>> Backtest(GOOG, SmaCross).run()
            Start                     2004-08-19 00:00:00
            End                       2013-03-01 00:00:00
            Duration                   3116 days 00:00:00
            Exposure Time [%]                     93.9944
            Equity Final [$]                      51959.9
            Equity Peak [$]                       75787.4
            Return [%]                            419.599
            Buy & Hold Return [%]                 703.458
            Return (Ann.) [%]                      21.328
            Volatility (Ann.) [%]                 36.5383
            Sharpe Ratio                         0.583718
            Sortino Ratio                         1.09239
            Calmar Ratio                         0.444518
            Max. Drawdown [%]                    -47.9801
            Avg. Drawdown [%]                    -5.92585
            Max. Drawdown Duration      584 days 00:00:00
            Avg. Drawdown Duration       41 days 00:00:00
            # Trades                                   65
            Win Rate [%]                          46.1538
            Best Trade [%]                         53.596
            Worst Trade [%]                      -18.3989
            Avg. Trade [%]                        2.35371
            Max. Trade Duration         183 days 00:00:00
            Avg. Trade Duration          46 days 00:00:00
            Profit Factor                         2.08802
            Expectancy [%]                        8.79171
            SQN                                  0.916893
            _strategy                            SmaCross
            _equity_curve                           Eq...
            _trades                       Size  EntryB...
            dtype: object
        """
        data = _Data(self._data.copy(deep=False))
        broker: _Broker = self._broker(data=data)
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

            self._results = self._compute_stats(broker, strategy)
        return self._results

    @staticmethod
    def _compute_drawdown_duration_peaks(dd: pd.Series):
        iloc = np.unique(np.r_[(dd == 0).values.nonzero()[0], len(dd) - 1])
        iloc = pd.Series(iloc, index=dd.index[iloc])
        df = iloc.to_frame("iloc").assign(prev=iloc.shift())
        df = df[df["iloc"] > df["prev"] + 1].astype(int)
        # If no drawdown since no trade, avoid below for pandas sake and return nan series
        if not len(df):
            return (dd.replace(0, np.nan),) * 2
        df["duration"] = df["iloc"].map(dd.index.__getitem__) - df["prev"].map(
            dd.index.__getitem__
        )
        df["peak_dd"] = df.apply(
            lambda row: dd.iloc[row["prev"]: row["iloc"] + 1].max(), axis=1
        )
        df = df.reindex(dd.index)
        return df["duration"], df["peak_dd"]

    def _compute_stats(self, broker: _Broker, strategy: Strategy) -> pd.Series:
        data = self._data
        index = data.index

        equity = pd.Series(broker._equity).bfill().fillna(broker._cash).values
        dd = 1 - equity / np.maximum.accumulate(equity)
        dd_dur, dd_peaks = self._compute_drawdown_duration_peaks(
            pd.Series(dd, index=index)
        )

        equity_df = pd.DataFrame(
            {"Equity": equity, "DrawdownPct": dd, "DrawdownDuration": dd_dur},
            index=index,
        )

        trades = broker.closed_trades
        trades_df = pd.DataFrame(
            {
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
        )
        trades_df["Duration"] = trades_df["ExitTime"] - trades_df["EntryTime"]

        pl = trades_df["PnL"]
        returns = trades_df["ReturnPct"]
        durations = trades_df["Duration"]

        def _round_timedelta(value, _period=_data_period(index)):
            if not isinstance(value, pd.Timedelta):
                return value
            resolution = (
                    getattr(_period, "resolution_string", None) or _period.resolution
            )
            return value.ceil(resolution)

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

        def geometric_mean(returns):
            returns = returns.fillna(0) + 1
            return (
                0
                if np.any(returns <= 0)
                else np.exp(np.log(returns).sum() / (len(returns) or np.nan)) - 1
            )

        day_returns = gmean_day_return = annual_trading_days = np.array(np.nan)
        if index.is_all_dates:
            day_returns = equity_df["Equity"].resample("D").last().dropna().pct_change()
            gmean_day_return = geometric_mean(day_returns)
            annual_trading_days = (
                365
                if index.dayofweek.to_series().between(5, 6).mean() > 2 / 7 * 0.6
                else 252
            )

        # Annualized return and risk metrics are computed based on the (mostly correct)
        # assumption that the returns are compounded. See: https://dx.doi.org/10.2139/ssrn.3054517
        # Our annualized return matches `empyrical.annual_return(day_returns)` whereas
        # our risk doesn't; they use the simpler approach below.
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
        max_dd = -np.nan_to_num(dd.max())
        s.loc["Calmar Ratio"] = np.clip(
            annualized_return / (-max_dd or np.nan), 0, np.inf
        )
        s.loc["Max. Drawdown [%]"] = max_dd * 100
        s.loc["Avg. Drawdown [%]"] = -dd_peaks.mean() * 100
        s.loc["Max. Drawdown Duration"] = _round_timedelta(dd_dur.max())
        s.loc["Avg. Drawdown Duration"] = _round_timedelta(dd_dur.mean())
        s.loc["# Trades"] = n_trades = len(trades)
        s.loc["Win Rate [%]"] = win_rate = (
            np.nan if not n_trades else (pl > 0).sum() / n_trades * 100
        )  # noqa: E501
        s.loc["Best Trade [%]"] = returns.max() * 100
        s.loc["Worst Trade [%]"] = returns.min() * 100
        mean_return = geometric_mean(returns)
        s.loc["Avg. Trade [%]"] = mean_return * 100
        s.loc["Max. Trade Duration"] = _round_timedelta(durations.max())
        s.loc["Avg. Trade Duration"] = _round_timedelta(durations.mean())
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

        s = Backtest._Stats(s)
        return s

    class _Stats(pd.Series):
        def __repr__(self):
            # Prevent expansion due to _equity and _trades dfs
            with pd.option_context("max_colwidth", 20):
                return super().__repr__()

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
        """
        Plot the progression of the last backtest run.

        If `results` is provided, it should be a particular result
        `pd.Series` such as returned by
        `core.core.Backtest.run` or
        `core.core.Backtest.optimize`, otherwise the last
        run's results are used.

        `filename` is the path to save the interactive HTML plot to.
        By default, a strategy/parameter-dependent file is created in the
        current working directory.

        `plot_width` is the width of the plot in pixels. If None (default),
        the plot is made to span 100% of browser width. The height is
        currently non-adjustable.

        If `plot_equity` is `True`, the resulting plot will contain
        an equity (initial cash plus assets) graph section. This is the same
        as `plot_return` plus initial 100%.

        If `plot_return` is `True`, the resulting plot will contain
        a cumulative return graph section. This is the same
        as `plot_equity` minus initial 100%.

        If `plot_pl` is `True`, the resulting plot will contain
        a profit/loss (P/L) indicator section.

        If `plot_volume` is `True`, the resulting plot will contain
        a trade volume section.

        If `plot_drawdown` is `True`, the resulting plot will contain
        a separate drawdown graph section.

        If `smooth_equity` is `True`, the equity graph will be
        interpolated between fixed points at trade closing times,
        unaffected by any interim asset volatility.

        If `relative_equity` is `True`, scale and label equity graph axis
        with return percent, not absolute cash-equivalent values.

        If `superimpose` is `True`, superimpose larger-timeframe candlesticks
        over the original candlestick chart. Default downsampling rule is:
        monthly for daily data, daily for hourly data, hourly for minute data,
        and minute for (sub-)second data.
        `superimpose` can also be a valid [Pandas offset string],
        such as `'5T'` or `'5min'`, in which case this frequency will be
        used to superimpose.
        Note, this only works for data with a datetime index.

        If `resample` is `True`, the OHLC data is resampled in a way that
        makes the upper number of candles for Bokeh to plot limited to 10_000.
        This may, in situations of overabundant data,
        improve plot's interactive performance and avoid browser's
        `Javascript Error: Maximum call stack size exceeded` or similar.
        Equity & dropdown curves and individual trades data is,
        likewise, [reasonably _aggregated_][TRADES_AGG].
        `resample` can also be a [Pandas offset string],
        such as `'5T'` or `'5min'`, in which case this frequency will be
        used to resample, overriding above numeric limitation.
        Note, all this only works for data with a datetime index.

        If `reverse_indicators` is `True`, the indicators below the OHLC chart
        are plotted in reverse order of declaration.

        [Pandas offset string]: \
            https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#dateoffset-objects

        [TRADES_AGG]: lib.html#core.lib.TRADES_AGG

        If `show_legend` is `True`, the resulting plot graphs will contain
        labeled legends.

        If `open_browser` is `True`, the resulting `filename` will be
        opened in the default web browser.
        """
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
