from abc import ABC, abstractmethod


class SQLiteType(ABC):
    type_ref = "None"

    def __init__(self):
        self.val = None

    @abstractmethod
    def set_to(self, value):
        self.val = value

    def get(self):
        return self.val
