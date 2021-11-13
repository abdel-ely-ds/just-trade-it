import os

import pytest

from t_nachine.backtester import Backtest
from t_nachine.strategies import Bouncing


@pytest.fixture
def backtest_wrapper():
    return Backtest(strategy=Bouncing, analysis_type="MICRO")


STOCK_PATH = os.path.join("stocks")
BACKTEST_NAME = "test"


class TestBacktestWrapper:
    def test_run(self, backtest_wrapper):
        backtest_results = backtest_wrapper.run(stock_path=STOCK_PATH)
        backtest_wrapper.log_results(
            backtest_results=backtest_results, backtest_name=BACKTEST_NAME
        )
