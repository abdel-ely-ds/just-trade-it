import pandas as pd
import numpy as np
import warnings


def validate_data(data: pd.DataFrame, cash: float):
    # Convert index to datetime index
    data = data.copy(deep=False)
    if (
        not data.index.is_all_dates
        and not isinstance(data.index, pd.RangeIndex)
        # Numeric index with most large numbers
        and (
            data.index.is_numeric()
            and (data.index > pd.Timestamp("1975").timestamp()).mean() > 0.8
        )
    ):
        try:
            data.index = pd.to_datetime(data.index, infer_datetime_format=True)
        except ValueError:
            pass

    if "Volume" not in data:
        data["Volume"] = np.nan

    if len(data) == 0:
        raise ValueError("OHLC `data` is empty")
    if len(data.columns & {"Open", "High", "Low", "Close", "Volume"}) != 5:
        raise ValueError(
            "`data` must be a pandas.DataFrame with columns "
            "'Open', 'High', 'Low', 'Close', and (optionally) 'Volume'"
        )
    if data[["Open", "High", "Low", "Close"]].isnull().values.any():
        raise ValueError(
            "Some OHLC values are missing (NaN). "
            "Please strip those lines with `df.dropna()` or "
            "fill them in with `df.interpolate()` or whatever."
        )
    if np.any(data["Close"] > cash):
        warnings.warn(
            "Some prices are larger than initial cash value. Note that fractional "
            "trading is not supported. If you want to trade Bitcoin, "
            "increase initial cash, or trade μBTC or satoshis instead (GH-134).",
            stacklevel=2,
        )
    if not data.index.is_monotonic_increasing:
        warnings.warn(
            "Data index is not sorted in ascending order. Sorting.", stacklevel=2
        )
        data = data.sort_index()
    if not data.index.is_all_dates:
        warnings.warn(
            "Data index is not datetime. Assuming simple periods, "
            "but `pd.DateTimeIndex` is advised.",
            stacklevel=2,
        )

    return data
