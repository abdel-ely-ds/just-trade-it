import sys
from abc import ABCMeta, abstractmethod
from typing import Tuple, Callable
import numpy as np
import pandas as pd

from tradeit.backtester.core._util import _as_str, _Indicator, try_
from tradeit.backtester.core.backtesting import _Orders
from tradeit.backtester.core._broker import _Broker
from tradeit.backtester.core._data import _Data
from tradeit.backtester.core.order import Order
from tradeit.backtester.core.position import Position
from tradeit.backtester.core.trade import Trade
from itertools import chain


class Strategy(metaclass=ABCMeta):
    def __init__(self, broker, data, params):
        self._indicators = []
        self._broker: _Broker = broker
        self._data: _Data = data
        self._params = self._check_params(params)

    def __repr__(self):
        return "<Strategy " + str(self) + ">"

    def __str__(self):
        params = ",".join(
            f"{i[0]}={i[1]}"
            for i in zip(self._params.keys(), map(_as_str, self._params.values()))
        )
        if params:
            params = "(" + params + ")"
        return f"{self.__class__.__name__}{params}"

    def _check_params(self, params):
        for k, v in params.items():
            if not hasattr(self, k):
                raise AttributeError(
                    f"Strategy '{self.__class__.__name__}' is missing parameter '{k}'."
                    "Strategy class should define parameters as class variables before they "
                    "can be optimized or run with."
                )
            setattr(self, k, v)
        return params

    def I(
        self,  # noqa: E741, E743
        func: Callable,
        *args,
        name=None,
        plot=True,
        overlay=None,
        color=None,
        scatter=False,
        **kwargs,
    ) -> np.ndarray:
        """
        Declare indicator. An indicator is just an array of values,
        but one that is revealed gradually in
        `core.core.Strategy.next` much like
        `core.core.Strategy.data` is.
        Returns `np.ndarray` of indicator values.

        `func` is a function that returns the indicator array(s) of
        same length as `core.core.Strategy.data`.

        In the plot legend, the indicator is labeled with
        function name, unless `name` overrides it.

        If `plot` is `True`, the indicator is plotted on the resulting
        `core.core.Backtest.plot`.

        If `overlay` is `True`, the indicator is plotted overlaying the
        price candlestick chart (suitable e.g. for moving averages).
        If `False`, the indicator is plotted standalone below the
        candlestick chart. By default, a heuristic is used which decides
        correctly most of the time.

        `color` can be string hex RGB triplet or X11 color name.
        By default, the next available color is assigned.

        If `scatter` is `True`, the plotted indicator marker will be a
        circle instead of a connected line segment (default).

        Additional `*args` and `**kwargs` are passed to `func` and can
        be used for parameters.

        For example, using simple moving average function from TA-Lib:

            def init():
                self.sma = self.I(ta.SMA, self.data.Close, self.n_sma)
        """
        if name is None:
            params = ",".join(filter(None, map(_as_str, chain(args, kwargs.values()))))
            func_name = _as_str(func)
            name = f"{func_name}({params})" if params else f"{func_name}"
        else:
            name = name.format(
                *map(_as_str, args),
                **dict(zip(kwargs.keys(), map(_as_str, kwargs.values()))),
            )

        try:
            value = func(*args, **kwargs)
        except Exception as e:
            raise RuntimeError(f'Indicator "{name}" errored with exception: {e}')

        if isinstance(value, pd.DataFrame):
            value = value.values.T

        if value is not None:
            value = try_(lambda: np.asarray(value, order="C"), None)
        is_arraylike = value is not None

        # Optionally flip the array if the user returned e.g. `df.values`
        if is_arraylike and np.argmax(value.shape) == 0:
            value = value.T

        if (
            not is_arraylike
            or not 1 <= value.ndim <= 2
            or value.shape[-1] != len(self._data.Close)
        ):
            raise ValueError(
                "Indicators must return (optionally a tuple of) numpy.arrays of same "
                f'length as `data` (data shape: {self._data.Close.shape}; indicator "{name}"'
                f'shape: {getattr(value, "shape" , "")}, returned value: {value})'
            )

        if plot and overlay is None and np.issubdtype(value.dtype, np.number):
            x = value / self._data.Close
            # By default, overlay if strong majority of indicator values
            # is within 30% of Close
            with np.errstate(invalid="ignore"):
                overlay = ((x < 1.4) & (x > 0.6)).mean() > 0.6

        value = _Indicator(
            value,
            name=name,
            plot=plot,
            overlay=overlay,
            color=color,
            scatter=scatter,
            # _Indicator.s Series accessor uses this:
            data=self.data,
        )
        self._indicators.append(value)
        return value

    @abstractmethod
    def init(self):
        """
        Initialize the strategy.
        Override this method.
        Declare indicators (with `core.core.Strategy.I`).
        Precompute what needs to be precomputed or can be precomputed
        in a vectorized fashion before the strategy starts.

        If you extend composable strategies from `core.lib`,
        make sure to call:

            super().init()
        """

    @abstractmethod
    def next(self):
        """
        Main strategy runtime method, called as each new
        `core.core.Strategy.data`
        instance (row; full candlestick bar) becomes available.
        This is the main method where strategy decisions
        upon data precomputed in `core.core.Strategy.init`
        take place.

        If you extend composable strategies from `core.lib`,
        make sure to call:

            super().next()
        """

    def buy(
        self,
        *,
        size: float = 1 - sys.float_info.epsilon,
        limit: float = None,
        stop: float = None,
        sl: float = None,
        tp: float = None,
    ):
        """
        Place a new long order. For explanation of parameters, see `Order` and its properties.

        See also `Strategy.sell()`.
        """
        assert (
            0 < size < 1 or round(size) == size
        ), "size must be a positive fraction of equity, or a positive whole number of units"
        return self._broker.new_order(size, limit, stop, sl, tp)

    def sell(
        self,
        *,
        size: float = 1 - sys.float_info.epsilon,
        limit: float = None,
        stop: float = None,
        sl: float = None,
        tp: float = None,
    ):
        """
        Place a new short order. For explanation of parameters, see `Order` and its properties.

        See also `Strategy.buy()`.
        """
        assert (
            0 < size < 1 or round(size) == size
        ), "size must be a positive fraction of equity, or a positive whole number of units"
        return self._broker.new_order(-size, limit, stop, sl, tp)

    @property
    def equity(self) -> float:
        """Current account equity (cash plus assets)."""
        return self._broker.equity

    @property
    def data(self) -> _Data:
        return self._data

    @property
    def position(self) -> Position:
        """Instance of `core.core.Position`."""
        return self._broker.position

    @property
    def orders(self) -> Tuple[Order, ...]:
        """List of orders (see `Order`) waiting for execution."""
        return _Orders(self._broker.orders)

    @property
    def trades(self) -> Tuple[Trade, ...]:
        """List of active trades (see `Trade`)."""
        return tuple(self._broker.trades)

    @property
    def closed_trades(self) -> Tuple[Trade, ...]:
        """List of settled trades (see `Trade`)."""
        return tuple(self._broker.closed_trades)
