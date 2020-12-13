from abc import ABC
from typing import Type, List

from .db_types import DBType


class Column:
    """
    Represents a column of a table in object type declaration
    """

    def __init__(self, col_type: Type[DBType], foreign_key=None, primary_key=False):
        """

        :param col_type: type for all values in a column
        :param foreign_key: specify a link
        :param primary_key: whether to use as a primary key
        """
        self.col_type = col_type
        self.foreign_key: ForeignKey = foreign_key
        self.primary_key = primary_key
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name


class ForeignKey:
    """
    Represents a link between two columns of different tables
    """

    def __init__(self, ref_table: Type["DBObject"], ref_column: str, cascade=False):
        """

        :param ref_table: an object with a corresponding table to ling
        :param ref_column: a column to link
        :param cascade: whether to delete if links deletes
        """
        self.ref_table = ref_table
        self.ref_column = ref_column
        self.cascade = cascade


class DBObject(ABC):
    __table_name__ = "default_table"
    """
    Represents an object with a corresponding row in a corresponding table in database
    """

    def __init__(self, **kwargs):
        """

        :param kwargs: dict of exact values for each column
        """
        obj_column_names = [c.name for c in self.obj_columns()]
        for k, v in kwargs.items():
            if k in obj_column_names:
                setattr(self, k, v)
            else:
                print("Attribute not found:", k)

    def __str__(self):
        return str(self.__dict__)

    @classmethod
    def class_columns(cls) -> List[Column]:
        return [getattr(cls, a) for a in dir(cls) if isinstance(getattr(cls, a), Column)]

    def obj_columns(self) -> List[Column]:
        return self.__class__.class_columns()

    @classmethod
    def class_foreign_keys(cls) -> List[ForeignKey]:
        return [c.foreign_key for c in cls.class_columns() if c.foreign_key]

    def obj_foreign_keys(self) -> List[ForeignKey]:
        return self.__class__.class_foreign_keys()

    @classmethod
    def class_primary_keys(cls) -> List[Column]:
        return [c for c in cls.class_columns() if c.primary_key]

    def obj_primary_keys(self) -> List[Column]:
        return self.__class__.class_primary_keys()
