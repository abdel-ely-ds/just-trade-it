from t_nachine.intrinsic_value import DCF
import pytest


@pytest.fixture
def calculator() -> DCF:
    return DCF()


def test_dcf(calculator: DCF):
    expected_value = 1.12

    assert expected_value == calculator(
        interest_rate=0.03,
        tax_rate=0.3,
        mv_of_equity=4_000_000_000,
        bv_of_debt=25_000_000,
        beta=0.80,
        risk_free_rate=0.04341,
        market_risk_premium=0.084,
        current_fcf=200_000_000,
        growth_rate=0.12,
        gdb_growth_rate=0.07,
        shares_outstanding=4_000_000_000,
        cash=1_350_000_00,
        debt=325_000_000,
        factor=1.2,
        n=10,
    )
