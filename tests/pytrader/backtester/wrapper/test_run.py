import pandas as pd

from pytrader.backtester import execute
from pytrader.strategies import Bouncing


def test_placerholder():
    strategy = Bouncing
    backtest_name = "test"
    stock = pd.read_csv(
        r"C:\Users\abdel\Desktop\Workspace\trading-pytrader\tests\pytrader\backtester\wrapper\a.us.txt"
    )
    stock.set_index("Date", inplace=True)
    stock.index = pd.to_datetime(stock.index)
    stats = execute(strategy=strategy, backtest_name=backtest_name, stock=stock)
    assert type(stats) == pd.Series
