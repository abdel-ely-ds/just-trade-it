from typing import List

from pytrader.candlesticks import Candle
from pytrader.patterns import IPattern


class OrgReversalPattern(IPattern):
    def __init__(self, candle: Candle, pre_candle: Candle, support: List[float]):
        """

        Args:
            candle (Candle): today's candle
            pre_candle (Candle): yesterday's candle
            support (List[float]): support
        """
        self._candle = candle
        self._pre_candle = pre_candle
        self._support = support

    def __bool__(self) -> bool:
        """
        pattern logic
        """
        cond1 = self._candle.above_support(
            self._support[0]
        ) and self._pre_candle.above_support(self._support[1])
        # cut the support
        cond2 = self._candle.low < self._support[0]
        # lower highs and lower lows
        cond3 = (
            self._candle.high < self._pre_candle.high
            and self._candle.low < self._pre_candle.low
        )
        return all([cond1, cond2, cond3])

    def __eq__(self, o: object) -> bool:
        if self.__bool__() and o:
            return True
        return False


class InsideBarReversalPattern(IPattern):
    def __init__(self, candle: Candle, pre_candle: Candle, support: List[float]):
        """

        Args:
            candle (Candle): today's candle
            pre_candle (Candle): yesterday's candle
            support (List[float]): support
        """
        self._candle = candle
        self._pre_candle = pre_candle
        self._support = support

    def __bool__(self):
        """
        pattern logic
        """
        cond1 = self._candle.above_support(
            self._support[0]
        ) and self._pre_candle.above_support(self._support[1])
        # cut support
        cond2 = self._.candle.low < self._support[0]
        # Lower highs and higher hihgs
        cond3 = (
            self._candle.high < self._pre_candle.high
            and self._candle.low > self._pre_candle.low
        )
        return all([cond1, cond2, cond3])

    def __eq__(self, o: object) -> bool:
        if self.__bool__() and o:
            return True
        return False


class TradeThroughReversalPattern(IPattern):
    def __init__(self, candle: Candle, pre_candle: Candle, support: List[float]):
        """

        Args:
            candle (Candle): today's candle
            pre_candle (Candle): yesterday's candle
            support (List[float]): support
        """
        self._candle = candle
        self._pre_candle = pre_candle
        self._support = support

    def __bool__(self):
        """
        pattern logic
        """
        cond1 = (
            self._pre_candle.bear()
            and self._pre_candle.open > self._support[1]
            and self._pre_candle.close < self._support[1]
        )
        cond2 = (
            self._candle.bull()
            and self._candle.open < self._support[0]
            and self._candle.close > self._support[0]
        )
        # lower highs and lower lows
        cond3 = (
            self._candle.high < self._pre_candle.high
            and self._candle.low < self._pre_candle.low
        )
        return all([cond1, cond2, cond3])

    def __eq__(self, o: object) -> bool:
        if self.__bool__() and o:
            return True
        return False


class PinReversalPattern(IPattern):
    def __init__(self, candle: Candle, support: List[float]):
        """

        Args:
            candle (Candle): today's candle
            pre_candle (Candle): yesterday's candle
            support (List[float]): support
        """
        self._candle = candle
        self._support = support

    def __bool__(self):
        """
        pattern logic
        """
        cond1 = self._candle.above_support(self._support[0])
        cond2 = self._candle.low < self._support[0]
        cond3 = self._candle.bull_pin(ratio=2 / 3)
        return all([cond1, cond2, cond3])

    def __eq__(self, o: object) -> bool:
        if self.__bool__() and o:
            return True
        return False


class AnyReversalPattern(IPattern):
    def __init__(self, candle: Candle, pre_candle: Candle, support: List[float]):
        """

        Args:
            candle (Candle): today's candle
            pre_candle (Candle): yesterday's candle
            support (List[float]): support
        """
        self._candle = candle
        self._pre_candle = pre_candle
        self._support = support

    # bad code
    def __bool__(self):
        """
        pattern logic
        """

        org_revsersal = OrgReversalPattern(
            candle=self._candle, pre_candle=self._pre_candle, support=self._support
        )

        inside_bar_reversal = InsideBarReversalPattern(
            candle=self._candle, pre_candle=self._pre_candle, support=self._support
        )

        trade_through_reversal = TradeThroughReversalPattern(
            candle=self._candle, pre_candle=self._pre_candle, support=self._support
        )

        pin_reversal = PinReversalPattern(candle=self._candle, support=self._support)

        return any(
            org_revsersal, inside_bar_reversal, trade_through_reversal, pin_reversal
        )

    def __eq__(self, o: object) -> bool:
        if self.__bool__() and o:
            return True
        return False
