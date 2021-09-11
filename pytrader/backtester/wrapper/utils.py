import json
import os
from copy import deepcopy
from typing import Type

import pandas as pd

from pytrader.backtester.core import Strategy


def update_strategy(
    strategy: Type[Strategy], strategy_attrs: dict = None
) -> Type[Strategy]:
    """
    Adds some attributes to the strategy

    Args:
        strategy (Strategy): strategy
        strategy_attrs (dict, optional): additional attributes. Defaults to None.

    Returns:
        Strategy: [description]
    """

    updated_strategy = deepcopy(strategy)

    try:
        for (
            key,
            value,
        ) in strategy_attrs.items():
            setattr(updated_strategy, key, value)
    except AttributeError:
        pass

    return updated_strategy


def post_process_stats(stats: pd.Series) -> json:
    stats_copy = stats.copy()
    try:
        stats_copy["Duration"] = stats_copy["Duration"].dt.days
    except KeyError:
        pass

    try:
        stats_copy = stats_copy.to_frame().T
    except AttributeError:
        pass

    return stats_copy.to_json(orient="split")


def pre_process_stock(stock: pd.DataFrame) -> pd.DataFrame:
    stock_copy = stock.copy()
    stock_copy.set_index("Date", inplace=True)
    stock_copy.index = pd.to_datetime(stock.index)
    return stock_copy


def pre_process_path(stocks_path: str) -> tuple[str, list[str]]:
    try:
        prefix_path = stocks_path
        stock_names = os.listdir(stocks_path)

    except NotADirectoryError:
        stocks_path_split = stocks_path.split("\\")
        prefix_path = "\\".join(stocks_path_split[:-1])
        stock_names = [stocks_path_split[-1]]

    return prefix_path, stock_names
