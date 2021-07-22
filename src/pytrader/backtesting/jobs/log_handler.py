import json
import os
from pprint import pprint
from typing import List

WARNING_MESSAGE = """
    ====================================================
    WARNING! The key already exists in the log file
    here are the keys {} saved in the log file
    ====================================================
"""
LOG_FOLDER = "logs"
BACKTESTED_NAMES_FILENAME = "backtest_names.txt"


class LogHandler:
    def __init__(
        self,
        log_folder: str = LOG_FOLDER,
        strategies_backtested_filename: str = BACKTESTED_NAMES_FILENAME,
    ) -> None:

        self._log_folder = log_folder
        self._backtest_names_filename = strategies_backtested_filename
        self.handle_logs()

    def handle_logs(self) -> None:
        """
        handles logs. It creates a folder where you can save all the backtests
        """

        # create a log folder if it does not exist
        if self._log_folder not in os.listdir():
            os.mkdir(self._log_folder)
            with open(
                os.path.join(self._log_folder, self._backtest_names_filename)
            ) as f:
                f.write(json.dumps({}))

    def get_backtest_names(self) -> List[str]:
        """
        it shows all used strategies backtested

        Returns:
            List[str]: list of strategy names
        """
        backtest_names = json.load(
            open(os.path.join(self._log_folder, self._backtest_names_filename))
        ).keys()

        return list(backtest_names)

    def handle_backtest_name(self, backtest_name: str) -> str:
        """

        Args:
            backtest_name: name on which the backtest will be saved
        Returns:
            str: name to used for logging the backtest expirement
        """

        backtest_names = self.get_backtest_names()
        new_backtest_name = backtest_name

        if backtest_name in backtest_names:
            pprint(WARNING_MESSAGE.format(backtest_names))
            ans = input("Do you want to overwrite: [y/n] ?")
            print("\n")
            if not ans.lower().startswith("y"):
                new_backtest_name = input("Please provide a new log name: ")
                new_backtest_name = new_backtest_name.lower()
        return new_backtest_name

    def log_backtest(self, backtest_name: str, strategy_attrs: dict = None):
        """
        it saves all the attributes of the strategy

        Args:
            strategy_name (str): name on which the backtest will be saved
            strategy_attrs (dict, optional): additional attributes. Defaults to None.
        """
        backtest_names = self.get_backtest_names()
        backtest_names[backtest_name] = strategy_attrs
        with open(os.path.join(self._log_folder, self._backtest_names_filename)) as f:
            f.write(json.dumps(backtest_names))

    def log_backtest_stats(self, stats: dict, backtest_name: str) -> None:
        with open(os.path.join(self._log_folder, backtest_name), 'w') as f:
            f.write(json.dumps(stats))
