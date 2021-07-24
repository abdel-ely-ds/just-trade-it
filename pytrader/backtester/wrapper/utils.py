from copy import deepcopy

from pytrader.backtester.backtesting import Strategy


def update_strategy(startegy: Strategy, strategy_attrs: dict = None) -> Strategy:
    """
    Adds some attributes to the strategy

    Args:
        startegy (Strategy): strategy
        strategy_attrs (dict, optional): additional attributes. Defaults to None.

    Returns:
        Strategy: [description]
    """
    updated_strategy = deepcopy(startegy)
    for (
        key,
        value,
    ) in strategy_attrs.items():
        setattr(updated_strategy, key, value)
    return updated_strategy
