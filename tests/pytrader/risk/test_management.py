import pytest
from pytrader.risk import STOP_LOSS_LOOKUP_TABLE, RiskManger

RISK_TO_REWARD = 2.0
RISK_PER_TRADE = 0.01


@pytest.fixture
def risk_manager():
    return RiskManger(risk_per_trade=RISK_PER_TRADE, risk_to_reward=RISK_TO_REWARD)


class TestRiskManager:
    def test_stop_loss(self, risk_manager):
        price = 49
        expected_sl = price - STOP_LOSS_LOOKUP_TABLE[50]
        assert expected_sl == risk_manager.stop_loss(price)

    def test_target(self, risk_manager):
        entry = 5
        stop_loss = 0
        expected_target = entry + (entry - stop_loss) * RISK_TO_REWARD
        assert expected_target == risk_manager.target(entry, stop_loss)

    def test_one_r(self, risk_manager):
        entry = 11
        stop_loss = 9
        expected_one_r = 2
        assert expected_one_r == risk_manager.one_r(entry, stop_loss)

    def test_shares(self, risk_manager):
        capital = 20_000
        one_r = 100
        entry = 800
        stop_loss = 700
        expected_shares = RISK_PER_TRADE * capital / one_r
        assert expected_shares == risk_manager.shares(capital, entry, stop_loss)
