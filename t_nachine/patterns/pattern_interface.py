from typing import Protocol


class Pattern(Protocol):
    def __init__(self, **kwargs):
        ...

    def __bool__(self):
        ...

    def __eq__(self, o: object) -> bool:
        ...
