from typing import List, Dict

from t_nachine.backtester import Trade
from t_nachine.candlesticks import Candle
from t_nachine.constants import TRADES_ATTRIBUTES
from t_nachine.risk import RiskManger
import pandas as pd

RISK_TO_REWARD = 2.0
RISk_PER_TRADE = 0.01


def get_candles(data: pd.DataFrame, days: int = 3) -> List[Candle]:
    """
    returns the last candles

    Args:
        data: stock data
        days (int, optional): days. Defaults to 3.

    Returns:
        List[Candle]: last candles
    """
    return [
        Candle(
            data.Open[-i],
            data.High[-i],
            data.Low[-i],
            data.Close[-i],
        )
        for i in range(1, days + 1)
    ]


def add_attrs(
    trade: Trade,
    high,
    low,
    risk_manager: RiskManger = RiskManger(
        risk_to_reward=RISK_TO_REWARD, risk_per_trade=RISk_PER_TRADE
    ),
    **kwargs,
) -> None:
    """
    it adds some attributes to the trade for post optimization

    Args:
        trade (Trade): trade
        high ([type]): high price on the current candle
        low ([type]): low price on the current candle
        risk_manager (RiskManger, optional): a risk manager .
                     Defaults to RiskManger( risk_to_reward=RISK_TO_REWARD, risk_per_trade=RISk_PER_TRADE ).
    """
    # add one_r
    if not hasattr(trade, "one_r"):
        one_r = risk_manager.one_r(trade.entry_price, trade.sl)
        setattr(trade, "one_r", one_r)

    # add **kwargs
    for key, value in kwargs.items():
        if not hasattr(trade, key):
            setattr(trade, key, value)

    # track max positive pnl
    try:
        trade.max_pnl = max(high - trade.entry_price, trade.max_pnl)
    except AttributeError:
        setattr(trade, "max_pnl", high - trade.entry_price)

    # track max negative pnl
    try:
        trade.max_negative_pnl = min(low - trade.entry_price, trade.max_negative_pnl)
    except AttributeError:
        diff = low - trade.entry_price
        max_negative_pnl = 0 if diff > 0 else diff
        setattr(trade, "max_negative_pnl", max_negative_pnl)


def build_attr_dict(data: pd.DataFrame, features: List[str] = None) -> Dict[str, float]:
    if features is None:
        features = TRADES_ATTRIBUTES

    # add attributes
    attr_dict = {}
    for feature in features:
        try:
            attr_dict[feature] = data[feature][-1]
        except KeyError:
            print(f'feature: {feature} does not exist')
            pass
    return attr_dict
