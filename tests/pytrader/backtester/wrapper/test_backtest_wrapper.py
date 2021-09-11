import pytest

from pytrader.backtester import BacktestWrapper
from pytrader.strategies import Bouncing


@pytest.fixture
def backtest_wrapper():
    return BacktestWrapper(strategy=Bouncing)


class TestBacktestWrapper:
    def test_run(self, backtest_wrapper):
        stocks_path = r"C:\Users\abdel\Desktop\Workspace\trading-pytrader\tests\pytrader\backtester\wrapper\stocks"
        backtest_results = backtest_wrapper.run(stocks_path)
        assert {"a.us.txt", "anh_b.us.txt"} == set(backtest_results.keys())
