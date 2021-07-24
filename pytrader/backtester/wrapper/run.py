import json

import pandas as pd

from pytrader.backtester.backtesting import Backtest, Strategy
from pytrader.backtester.wrapper.exceptions import (
    ALLOWED_ANALYSIS_TYPES,
    AnalysisNotAllowedError,
)
from pytrader.backtester.wrapper.log_handler import LogHandler

from .utils import update_strategy


def execute(
    strategy: Strategy,
    backtest_name: str,
    stock: pd.Series,
    cash: int = 20_000,
    commission: int = 0.0,
    exclusive_orders: bool = False,
    strategy_attrs: dict = None,
    analysis_type: str = "MACRO",
    log_handler: LogHandler = LogHandler(),
) -> json:
    # checks
    if analysis_type not in ALLOWED_ANALYSIS_TYPES:
        raise AnalysisNotAllowedError(analysis_type)

    # handling logs
    backtest_name = log_handler.handle_backtest_name(backtest_name)

    updated_strategy = update_strategy(strategy, strategy_attrs)
    bt = Backtest(
        stock,
        updated_strategy,
        cash=cash,
        commission=commission,
        exclusive_orders=exclusive_orders,
    )
    stats = bt.run()
    stats = stats[ALLOWED_ANALYSIS_TYPES[analysis_type]]

    # todo: process stats

    return stats.to_json(orient="split")
