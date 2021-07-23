from abc import ABC, abstractmethod


class IPattern(ABC):
    @abstractmethod
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def __bool__(self):
        pass

    @abstractmethod
    def __eq__(self, o: object) -> bool:
        pass
