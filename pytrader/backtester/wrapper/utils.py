from copy import deepcopy
from typing import Type

from pytrader.backtester.core import Strategy


def update_strategy(strategy: Type[Strategy], strategy_attrs: dict = None) -> Type[Strategy]:
    """
    Adds some attributes to the strategy

    Args:
        strategy (Strategy): strategy
        strategy_attrs (dict, optional): additional attributes. Defaults to None.

    Returns:
        Strategy: [description]
    """
    if strategy_attrs is None:
        strategy_attrs = {}
    updated_strategy = deepcopy(strategy)
    for (
            key,
            value,
    ) in strategy_attrs.items():
        setattr(updated_strategy, key, value)
    return updated_strategy
