import os

import pytest

from pytrader.backtester import BacktestWrapper
from pytrader.strategies import Bouncing


@pytest.fixture
def backtest_wrapper():
    return BacktestWrapper(strategy=Bouncing, analysis_type="MICRO")


STOCK_PATH = os.path.join("stocks")
BACKTEST_NAME = "test"


class TestBacktestWrapper:
    def test_run(self, backtest_wrapper):
        backtest_results = backtest_wrapper.run(stock_path=STOCK_PATH)
        backtest_wrapper.log_results(
            backtest_results=backtest_results, backtest_name=BACKTEST_NAME
        )
