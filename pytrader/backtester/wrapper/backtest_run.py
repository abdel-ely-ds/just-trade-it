import json
from typing import Type

import pandas as pd

from pytrader.backtester.core import Backtest, Strategy
from pytrader.backtester.wrapper.available_analysis import AVAILABLE_ANALYSIS
from pytrader.backtester.wrapper.exceptions import AnalysisNotAvailableError
from pytrader.backtester.wrapper.log_handler import LogHandler

from .utils import update_strategy


def backtest_run(
        strategy: Type[Strategy],
        backtest_name: str,
        stock: pd.DataFrame,
        cash: int = 20_000,
        commission: int = 0.0,
        exclusive_orders: bool = False,
        strategy_attrs: dict = None,
        analysis_type: str = "MACRO",
        log_handler: LogHandler = LogHandler(),
) -> json:
    # checks
    if strategy_attrs is None:
        strategy_attrs = {}
    if analysis_type not in AVAILABLE_ANALYSIS:
        raise AnalysisNotAvailableError(analysis_type)

    backtest_name = log_handler.handle_backtest_name(backtest_name)
    updated_strategy = update_strategy(strategy, strategy_attrs)

    # run
    bt = Backtest(
        stock,
        updated_strategy,
        cash=cash,
        commission=commission,
        exclusive_orders=exclusive_orders,
    )
    stats = bt.run()

    stats = stats[AVAILABLE_ANALYSIS[analysis_type]]

    # TODO: process the stats

    log_handler.log_backtest(backtest_name=backtest_name,
                             stats=stats.to_json(orient="split"),
                             strategy_attrs=strategy_attrs)
    return stats
