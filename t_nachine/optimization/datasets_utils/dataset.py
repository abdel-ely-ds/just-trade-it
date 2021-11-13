from dataclasses import dataclass

import numpy as np


@dataclass
class Dataset:
    train_x: np.ndarray
    train_y: np.ndarray
    test_x: np.ndarray
    test_y: np.ndarray
