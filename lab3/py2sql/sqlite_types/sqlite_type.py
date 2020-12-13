from abc import ABC, abstractmethod


class SQLiteType(ABC):
    type_ref = "None"

    def __init__(self):
        self.val = None

    @staticmethod
    @abstractmethod
    def value_to_str(val) -> str:
        return str(val)
