from abc import ABC, abstractmethod


class DBType(ABC):
    db_type = None
    python_type = None

    @classmethod
    @abstractmethod
    def value_to_str(cls, val) -> str:
        pass

    @classmethod
    @abstractmethod
    def convert_from_db(cls, val):
        pass
