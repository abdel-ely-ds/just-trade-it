from pydantic import BaseModel, validator


class Dataset(BaseModel):
    train_x: pd.DataFrame
    train_y: pd.Series
    test_x: pd.DataFrame
    test_y: pd.Series

    @validator("train_x")
    def check_train(cls, v, values):
        if "train_x" in values and len(v) != len(values["train_x"]):
            raise ValueError("train_x and train_y don't have the same length")
        return v

    @validator("test_x")
    def check_test(cls, v, values):
        if "test_x" in values and len(v) != len(values["test_x"]):
            raise ValueError("test_x and test_y don't have the same length")
        return v
