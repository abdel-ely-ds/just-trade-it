import numpy as np
import pandas as pd


def EMA(prices: pd.Series, n: int) -> pd.Series:
    """
    exp moving average

    Args:
        prices (pd.Series): a collection of prices
        n (int): periods

    Returns:
        pd.Series: ema
    """
    return prices.s.ewm(span=n, adjust=False).mean()


def MACD(prices: pd.Series, nfast=50, nslow=100):
    fast = EMA(prices, n=nfast)
    slow = EMA(prices, n=nslow)
    return fast - slow


def STOCHASTICS(data, period, k):
    close, low, high = data.Close.s, data.Low.s, data.High.s
    l_period = low.rolling(window=period).min()
    h_period = high.rolling(window=period).max()
    per_k = 100 * (close - l_period) / (h_period - l_period)
    per_k = per_k.rolling(window=k).mean()
    return per_k


def RSI(price, n=14) -> pd.Series:
    prices = price.s
    deltas = np.diff(prices)
    seed = deltas[: n + 1]
    up = seed[seed >= 0].sum() / n
    down = -seed[seed < 0].sum() / n
    rs = up / down
    rsi = np.zeros_like(prices)
    rsi[:n] = 100.0 - 100.0 / (1.0 + rs)
    for i in range(n, len(prices)):
        delta = deltas[i - 1]  # The diff is 1 shorter
        if delta > 0:
            upval = delta
            downval = 0.0
        else:
            upval = 0.0
            downval = -delta
        up = (up * (n - 1) + upval) / n
        down = (down * (n - 1) + downval) / n
        rs = up / down
        rsi[i] = 100.0 - 100.0 / (1.0 + rs)
    return pd.Series(rsi)
