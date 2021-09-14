import pandas as pd


def test_analyze():
    btr = pd.read_csv("../backtester/wrapper/logs/test.csv")
    print(btr)
