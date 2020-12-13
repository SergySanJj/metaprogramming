from abc import ABC, abstractmethod


class DBType(ABC):
    """
    Base class for all objects
    """

    db_type = None
    python_type = None

    @classmethod
    @abstractmethod
    def value_to_str(cls, val: "DBType") -> str:
        """
        Convert object to string
        :param val: object to convert
        :return: string object representation
        """
        pass

    @classmethod
    @abstractmethod
    def convert_from_db(cls, val: "DBType"):
        pass
