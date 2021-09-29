import pandas as pd
from sklearn.utils import shuffle

from pytrader.optimization.datasets_utils.dataset import Dataset


def random_splitter(
    x: pd.DataFrame, y: pd.DataFrame, random_state: int = 0, percentage: float = 0.8
) -> Dataset:
    shuffled_x, shuffled_y = shuffle(x, random_state=random_state), shuffle(
        y, random_state=random_state
    )
    index = int(len(shuffled_x) * percentage)
    return Dataset(
        train_x=shuffled_x[:index],
        train_y=shuffled_y[:index],
        test_x=shuffled_x[index:],
        test_y=shuffled_y[index:],
    )
