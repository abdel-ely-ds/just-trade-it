import json
from copy import deepcopy

import pandas as pd
from pytrader.backtesting import (
    ALLOWED_ANALYSIS_TYPES,
    ANALYSIS_NOT_ALLOWED_MESSAGE,
    AnalysisNotAllowedError,
    Backtest,
    LogHandler,
    Strategy,
)


def update_strategy(startegy: Strategy, strategy_attrs: dict = None) -> Strategy:
    updated_strategy = deepcopy(startegy)
    for (
        key,
        value,
    ) in strategy_attrs.items():
        setattr(updated_strategy, key, value)
    return updated_strategy


def run(
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
