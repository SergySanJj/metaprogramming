from abc import ABC
from typing import Type


class DBObject(ABC):
    __table_name__ = "table_name"

    def __init__(self, **kwargs):
        print(kwargs)
        for k, v in kwargs.items():
            print(k, v)
            if k in self.columns:
                self.__setattr__(k, v)
            else:
                print("No such attribute ", k)

    def __str__(self):
        s = "{"
        for x in self.__dict__.keys():
            s += f"{x}: {self.__getattribute__(x)} "
        return s + "}"

    @property
    def columns(self):
        return tuple(set(dir(self.__class__)) - set(dir(DBObject)))


class ColumnClass:
    def __init__(self, col_type, foreign_key=None, primary_key=False):
        self.col_type = col_type
        self.foreign_key: ForeignKeyClass = foreign_key
        self.primary_key = primary_key


def Column(col_type, foreign_key=None, primary_key=False):
    return ColumnClass(col_type, foreign_key, primary_key)


class ForeignKeyClass:
    def __init__(self, ref_table, ref_column, cascade=False):
        self.ref_table = ref_table
        self.ref_column = ref_column
        self.cascade = cascade


def ForeignKey(ref_table, ref_column, cascade=False):
    return ForeignKeyClass(ref_table, ref_column, cascade)


def get_table_name(cls: Type[DBObject]):
    return getattr(cls, "__table_name__")


def create_table_query(cls):
    values = []
    references = []
    columns = tuple(set(dir(cls)) - set(dir(DBObject)))

    for c in columns:
        if not callable(getattr(cls, c)):
            v = ""
            v += c + " "
            column: ColumnClass = getattr(cls, c)
            v += column.col_type.type_ref + " "

            if column.primary_key:
                v += "PRIMARY KEY "

            values.append("\n" + v)

    for c in columns:
        if not callable(getattr(cls, c)):
            column: ColumnClass = getattr(cls, c)
            if column.foreign_key:
                v = ""
                v += f"""\nFOREIGN KEY ({c}) REFERENCES {column.foreign_key.ref_table} ({column.foreign_key.ref_column})"""
                if column.foreign_key.cascade:
                    v += " ON DELETE CASCADE"
                references.append(v)

    q = "CREATE TABLE IF NOT EXISTS " + getattr(cls, "__table_name__") + \
        " (\n" + \
        ",".join(values + references) + \
        "\n)"
    return q


def reference():
    pass
