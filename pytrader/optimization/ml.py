from lightgbm import LGBMClassifier

from pytrader.optimization.dataset import Dataset


class MLModel:
    def __init__(
        self,
        dataset: Dataset,
        n_estimators: int = 200,
        random_state: int = 2020,
        n_jobs: int = -1,
        learning_rate: float = 0.06,
        percentage: float = 0.8,
    ):

        self._dataset = dataset
        self._model = LGBMClassifier(
            n_estimators=n_estimators,
            n_jobs=n_jobs,
            learning_rate=learning_rate,
            random_state=random_state,
        )

        self._x, self._y = dataset.build()
        self._train, self._test = dataset.random_split(
            self._x, self._y, random_state=random_state, percentage=percentage
        )

    @property
    def dataset(self):
        return self._dataset

    @property
    def model(self):
        return self._model

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def train(self):
        return self._train

    @property
    def test(self):
        return self._test

    def fit(self):
        self.model.fit(self.train.x, self.train.y)

    def predict(self, x_sample):
        self.model.predict(x_sample)