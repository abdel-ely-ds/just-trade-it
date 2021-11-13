from t_nachine.backtester.wrapper.exception_messages import BACKTEST_NAME_ALREADY_EXISTS


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
