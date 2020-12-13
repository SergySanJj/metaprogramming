from abc import ABC
from typing import Type, List, Any

from .db_types import DBType


class Column:
    def __init__(self, col_type: Type[DBType], foreign_key=None, primary_key=False):
        self.col_type = col_type
        self.foreign_key: ForeignKey = foreign_key
        self.primary_key = primary_key
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name


class ForeignKey:
    def __init__(self, ref_table: Type["DBObject"], ref_column, cascade=False):
        self.ref_table = ref_table
        self.ref_column = ref_column
        self.cascade = cascade


class DBObject(ABC):
    __table_name__ = "default_table"

    def __init__(self, **kwargs):
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
    def class_foreign_keys(cls) -> List[Any]:
        return [c.foreign_key for c in cls.class_columns() if c.foreign_key]

    def obj_foreign_keys(self) -> List[Any]:
        return self.__class__.class_foreign_keys()
