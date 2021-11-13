from typing import Protocol


class IntrinsicValueCalculator(Protocol):
    def __call__(self, *args, **kwargs) -> float:
        ...
