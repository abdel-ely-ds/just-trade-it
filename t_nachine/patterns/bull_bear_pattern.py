from t_nachine.candlesticks import Candle


class BullBearPattern:
    def __init__(self, candle: Candle, pre_candle: Candle):
        """

        Args:
            candle (Candle): today's candle
            pre_candle (Candle): yesterday's candle
        """
        self._candle = candle
        self._pre_candle = pre_candle

    def __bool__(self) -> bool:
        """
        pattern logic
        """
        cond1 = self._candle.bull()
        cond2 = self._pre_candle.bear()

        # closing above high of previous candle
        cond3 = self._candle.close > self._pre_candle.high

        return all([cond1, cond2, cond3])

    def __eq__(self, o: object) -> bool:
        return isinstance(o, bool) and self.__bool__() == o
