from t_nachine.intrinsic_value.dcf import DCF
from t_nachine.intrinsic_value.protocol import IntrinsicValueCalculator
from t_nachine.intrinsic_value.data_loader import DataLoader, Fundamentals


def compute(
    stock_symbol: str,
    data_loader: DataLoader,
    calculator: IntrinsicValueCalculator = DCF(),
) -> float:
    data: Fundamentals = data_loader(stock_symbol)
    return calculator(data)
