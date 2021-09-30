from tradeit.candlesticks import Candle
from tradeit.patterns import OrgReversalPattern


class TestReversalPatterns:
    def test_org_reversal(self):
        # not a reversal

        candle = Candle(10, 50, 0.2, 3)
        pre_candle = Candle(80, 100, 2, 41)
        support = [8, 10]
        org_reversal = OrgReversalPattern(candle, pre_candle, support)
        assert org_reversal == False

        candle = Candle(10, 50, 0.2, 20)
        pre_candle = Candle(80, 100, 2, 41)
        support = [8, 10]
        org_reversal = OrgReversalPattern(candle, pre_candle, support)
        assert org_reversal == True
