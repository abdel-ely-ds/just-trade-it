import pandas as pd

from pytrader.backtester import backtest_run
from pytrader.strategies import Bouncing


def test_backtest_run():
    strategy = Bouncing
    backtest_name = "test"
    stocks_directory = r"C:\Users\abdel\Desktop\Workspace\trading-pytrader\tests\pytrader\backtester\wrapper\stocks"

    backtest_results = backtest_run(strategy=strategy,
                                    backtest_name=backtest_name,
                                    stocks_directory=stocks_directory,
                                    analysis_type="MICRO")
    print(backtest_results)
    assert {'a.us.txt', 'anh_b.us.txt'} == set(backtest_results.keys())
