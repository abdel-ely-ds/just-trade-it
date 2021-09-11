import json
from typing import Type
import os
from tqdm import tqdm
import pandas as pd

from pytrader.backtester.core import Backtest, Strategy
from pytrader.backtester.wrapper.available_analysis import AVAILABLE_ANALYSIS
from pytrader.backtester.wrapper.exceptions import AnalysisNotAvailableError
from pytrader.backtester.wrapper.log_handler import LogHandler

from .utils import update_strategy, post_process_stats, pre_process_stock


def backtest_run(
        strategy: Type[Strategy],
        backtest_name: str,
        stocks_directory: str,
        cash: int = 20_000,
        commission: int = 0.0,
        exclusive_orders: bool = False,
        strategy_attrs: dict = None,
        analysis_type: str = "MACRO",
        log_handler: LogHandler = LogHandler(),
) -> json:

    # checks
    if analysis_type not in AVAILABLE_ANALYSIS:
        raise AnalysisNotAvailableError(analysis_type)

    backtest_name = log_handler.handle_backtest_name(backtest_name)

    stock_names = os.listdir(stocks_directory)
    backtest_results = {}

    for stock_name in tqdm(stock_names):
        bt = Backtest(
            pre_process_stock(pd.read_csv(os.path.join(stocks_directory, stock_name))),
            update_strategy(strategy, strategy_attrs),
            cash=cash,
            commission=commission,
            exclusive_orders=exclusive_orders,
        )
        stats = bt.run()
        stats = stats[AVAILABLE_ANALYSIS[analysis_type]]
        backtest_results[stock_name] = post_process_stats(stats)

    return backtest_results
