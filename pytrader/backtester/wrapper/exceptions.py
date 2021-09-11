from pytrader.backtester.wrapper.available_analysis import ANALYSIS_ATTRIBUTES
from pytrader.backtester.wrapper.exception_messages import (
    ANALYSIS_NOT_AVAILABLE_MESSAGE,
    BACKTEST_NAME_ALREADY_EXISTS,
)


class AnalysisNotAvailableError(Exception):
    def __init__(self, analysis_type, message=ANALYSIS_NOT_AVAILABLE_MESSAGE):
        self.analysis_type = analysis_type
        self.message = message
        super().__init__(
            self.message.format(self.analysis_type, ANALYSIS_ATTRIBUTES.keys())
        )


class BackTestNameAlreadyExists(Exception):
    def __init__(
        self,
        existing_backtest_names,
        backtest_name,
        message=BACKTEST_NAME_ALREADY_EXISTS,
    ):
        self.backtest_name = backtest_name
        self.existing_backtest_names = existing_backtest_names
        self.message = message
        super().__init__(
            self.message.format(self.backtest_name, self.existing_backtest_names)
        )
