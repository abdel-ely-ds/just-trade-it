from pytrader.candlesticks import Candle
from pytrader.patterns import (
    AnyReversalPattern,
    InsideBarReversalPattern,
    OrgReversalPattern,
    PinReversalPattern,
    TradeThroughReversalPattern,
)


class TestReversalPatterns:
    def test_org_reversal(self):
        candle = Candle(10, 50, 0.2, 3)
        pre_candle = Candle(80, 100, 2, 41)
        support = [8, 10]
        org_reversal = OrgReversalPattern(candle, pre_candle, support)
        assert org_reversal == False
