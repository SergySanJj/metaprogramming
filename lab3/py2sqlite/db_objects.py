from abc import ABC, ABCMeta
import inspect
import logging
from typing import Type, List, Any

from .db_types import DBType, typecheck


class Column:
    """
    Represents a column of a table in object type declaration
    """

    def __init__(self, col_type: Type[DBType], foreign_key=None, primary_key=False, hierarchy_ref=False):
        """

        :param col_type: type for all values in a column
        :param foreign_key: specify a link
        :param primary_key: whether to use as a primary key
        """
        self.col_type = col_type
        self.foreign_key: ForeignKey = foreign_key
        self.primary_key = primary_key
        self.name = None
        self.hierarchy_ref = hierarchy_ref

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


class DBObjectMeta(ABCMeta):
    """
    DBObject metaclass
    Used for dynamically finding primary key and initializing db_type, python_type and pk_name values
    """

    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pks = cls.class_primary_keys()
        pks = [x for x in pks if x not in cls.__base__.class_primary_keys()]

        if len(pks) == 1:
            pk = pks[0]
            cls.db_type = pk.col_type.db_type
            cls.python_type = cls
            cls.pk_name = pk.name

            if cls.__base__ != DBObject:
                b: Type[DBObject] = cls.__base__
                setattr(cls, f"hierarchy_ref_{b.__name__}",
                        Column(b, hierarchy_ref=True))
                ro = getattr(cls, f"hierarchy_ref_{b.__name__}")
                ro.name = f"hierarchy_ref_{b.__name__}"

        elif not inspect.isabstract(cls) and cls.__name__ != 'DBObject':
            logging.warning(f'Class {cls.__name__} cannot be aggregated in other DBObject')


class DBObject(DBType, metaclass=DBObjectMeta):
    """
    Represents an object with a corresponding row in a corresponding table in database
    """

    __table_name__ = "default_table"
    db_type = None
    python_type = None
    pk_name = None

    def __init__(self, **kwargs):
        """

        :param kwargs: dict of exact values for each column
        """
        obj_column_names = [c.name for c in self.obj_columns(True)]
        for k, v in kwargs.items():
            if k in obj_column_names:
                setattr(self, k, v)
            else:
                print("Attribute not found:", k)

    def __str__(self):
        return str(self.__dict__)

    @classmethod
    def class_columns(cls, with_parent=False) -> List[Column]:
        res = [getattr(cls, a) for a in dir(cls) if isinstance(getattr(cls, a), Column) if
               not getattr(cls, a).hierarchy_ref]

        if not with_parent:
            if cls.class_hierarchy_ref():
                reference: Column = cls.class_hierarchy_ref()
                res = [x for x in res if x not in reference.col_type.class_columns()]
        return res

    def obj_columns(self, with_parent=False) -> List[Column]:
        return self.__class__.class_columns(with_parent)

    @classmethod
    def class_hierarchy_ref(cls):
        a = [getattr(cls, a) for a in dir(cls) if isinstance(getattr(cls, a), Column) if getattr(cls, a).hierarchy_ref]
        if len(a) > 0:
            return a[0]
        else:
            return None

    def hierarchy_ref(self):
        return self.__class__.class_hierarchy_ref()

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

    @classmethod
    @typecheck
    def value_to_str(cls, val: "DBObject") -> str:
        # return value of primary key
        return str(getattr(val, val.pk_name))
