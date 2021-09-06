from pytrader.backtester import LogHandler
import os
import pytest

LOG_FOLDER = "logs"
BACKTESTED_NAMES_FILENAME = "backtest_names.txt"


@pytest.fixture
def log_handler():
    return LogHandler(log_folder=LOG_FOLDER,
                      backtest_names_filename=BACKTESTED_NAMES_FILENAME)


class TestLogHandler:
    def test_handle_logs_folder_creation(self, log_handler):
        """ check that once the log handler is initialized, a log folder is created"""
        assert log_handler._log_folder in os.listdir()

    def test_handle_logs_backtested_names_file(self, log_handler):
        """check that the backtest_names folder is created on the log folder"""
        assert log_handler._backtest_names_filename in os.listdir(log_handler._log_folder)
