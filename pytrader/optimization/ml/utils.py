import joblib


def save(model, path="logs/model.pkl"):
    return joblib.dump(model, path)


def load(path="logs/model.pkl"):
    return joblib.load(path)
