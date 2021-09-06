import json
import os

from pytrader.backtester.wrapper.exceptions import BackTestNameAlreadyExists

LOG_FOLDER = "logs"
BACKTESTED_NAMES_FILENAME = "backtest_names.txt"


class LogHandler:
    def __init__(
            self,
            log_folder: str = LOG_FOLDER,
            backtest_names_filename: str = BACKTESTED_NAMES_FILENAME,
    ) -> None:

        self._log_folder = log_folder
        self._backtest_names_filename = backtest_names_filename
        self.handle_logs()

    def handle_logs(self) -> None:
        """
        handles logs. It creates a folder where you can save all the backtests
        """

        # create a log folder if it does not exist
        if self._log_folder not in os.listdir():
            os.mkdir(self._log_folder)
            with open(
                    os.path.join(self._log_folder, self._backtest_names_filename), "w"
            ) as f:
                f.write(json.dumps({}))

    def get_backtest_names(self) -> dict:
        """
        it shows all used strategies backtested

        Returns:
            List[str]: list of strategy names
        """
        return json.load(
            open(os.path.join(self._log_folder, self._backtest_names_filename))
        )

    def handle_backtest_name(self, backtest_name: str) -> str:
        """

        Args:
            backtest_name: name on which the backtest will be saved
        Returns:
            str: name to used for logging the backtest experiment
        """

        backtest_names = self.get_backtest_names()

        if backtest_name not in backtest_names:
            return backtest_name.lower()
        raise BackTestNameAlreadyExists(existing_backtest_names=backtest_names.keys(),
                                        backtest_name=backtest_name)

    def _log_backtest(self, backtest_name: str, strategy_attrs: dict = {}):
        """
        it saves all the attributes of the strategy

        Args:
            backtest_name (str): name on which the backtest will be saved
            strategy_attrs (dict, optional): additional attributes. Defaults to None.
        """
        backtest_names = self.get_backtest_names()
        backtest_names[backtest_name] = strategy_attrs
        print(backtest_names)
        with open(os.path.join(self._log_folder, self._backtest_names_filename), "w") as f:
            f.write(json.dumps(backtest_names))

    def _log_backtest_stats(self, backtest_name: str, stats: dict) -> None:
        with open(os.path.join(self._log_folder, backtest_name), "w") as f:
            f.write(json.dumps(stats))

    def log_backtest(self, backtest_name, stats, strategy_attrs: dict = {}):
        self._log_backtest(backtest_name=backtest_name, strategy_attrs=strategy_attrs)
        self._log_backtest_stats(backtest_name=backtest_name, stats=stats)
