from pytrader.risk import RiskManger
from pytrader.risk import STOP_LOSS_LOOKUP_TABLE

risk_manager = RiskManger(risk_to_reward=2.0)


def test_stop_loss():
    price = 49
    expected_sl = price - STOP_LOSS_LOOKUP_TABLE[50]
    assert expected_sl == risk_manager.stop_loss(price)


def test_target():
    entry = 5
    stop_loss = 0
    expected_target = 15
    assert expected_target == risk_manager.target(entry, stop_loss)


def test_one_r():
    entry = 11
    stop_loss = 9
    expected_one_r = 2
    assert expected_one_r == risk_manager.one_r(entry, stop_loss)
