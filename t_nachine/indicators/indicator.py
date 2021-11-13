import numpy as np
import pandas as pd


def ema(stock: pd.DataFrame, n: int) -> pd.Series:
    return stock["Close"].s.ewm(span=n, adjust=False).mean()


def macd(stock: pd.DataFrame, n_fast=50, n_slow=100):
    fast = ema(stock, n=n_fast)
    slow = ema(stock, n=n_slow)
    return fast - slow


def stochastics(stock: pd.DataFrame, period: int, k: int):
    close, low, high = stock.Close, stock.Low, stock.High
    l_period = low.rolling(window=period).min()
    h_period = high.rolling(window=period).max()
    per_k = 100 * (close - l_period) / (h_period - l_period)
    per_k = per_k.rolling(window=k).mean()
    return per_k


def rsi(stock: pd.DataFrame, n=14) -> pd.Series:
    prices = stock["Close"]
    deltas = np.diff(prices)
    seed = deltas[: n + 1]
    up = seed[seed >= 0].sum() / n
    down = -seed[seed < 0].sum() / n
    rs = up / down
    rsi_values = np.zeros_like(prices)
    rsi_values[:n] = 100.0 - 100.0 / (1.0 + rs)
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
        rsi_values[i] = 100.0 - 100.0 / (1.0 + rs)
    return pd.Series(rsi_values)
