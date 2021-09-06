import pandas as pd

from pytrader.backtester import backtest_run
from pytrader.strategies import Bouncing


def test_backtest_run():
    strategy = Bouncing
    backtest_name = "test"
    stock = pd.read_csv(
        r"C:\Users\abdel\Desktop\Workspace\trading-pytrader\tests\pytrader\backtester\wrapper\a.us.txt"
    )
    stock.set_index("Date", inplace=True)
    stock.index = pd.to_datetime(stock.index)
    stats = backtest_run(strategy=strategy, backtest_name=backtest_name, stock=stock, analysis_type="MACRO")
    print(stats)
    assert type(stats) == pd.Series
