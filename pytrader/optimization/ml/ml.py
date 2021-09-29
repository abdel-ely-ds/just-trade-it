import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.metrics import precision_score, recall_score

from pytrader.constants import *
from pytrader.optimization.datasets_utils import Dataset
from pytrader.optimization.ml.utils import save


class ML:
    def __init__(
        self,
        dataset: Dataset,
        n_estimators: int = 200,
        random_state: int = 2020,
        n_jobs: int = -1,
        learning_rate: float = 0.06,
    ):
        self._dataset = dataset
        self._model = LGBMClassifier(
            n_estimators=n_estimators,
            n_jobs=n_jobs,
            learning_rate=learning_rate,
            random_state=random_state,
        )

    @property
    def dataset(self):
        return self._dataset

    @property
    def model(self):
        return self._model

    def fit(self):
        self.model.fit(self.dataset.train_x, self.dataset.train_y)

    def evaluate(self) -> pd.DataFrame:
        train_y, test_y = self.dataset.train_y, self.dataset.test_y
        # predictions
        train_preds = self.model.predict(self.dataset.train_x)
        test_preds = self.model.predict(self.dataset.test_x)

        train_recall, train_precision = (
            recall_score(train_y, train_preds),
            precision_score(train_y, train_preds),
        )
        test_recall, test_precision = recall_score(test_y, test_preds), precision_score(
            test_y, test_preds
        )

        return pd.DataFrame(
            [train_recall, train_precision, test_recall, test_precision],
            columns=[RECALL_TRAIN, PRECISION_TRAIN, RECALL_TEST, PRECISION_TEST],
        )

    def predict(self, x_sample):
        self.model.predict(x_sample)

    def save(self, path: str = "logs/model.pkl") -> None:
        save(self.model, path)
