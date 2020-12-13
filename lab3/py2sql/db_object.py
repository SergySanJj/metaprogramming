from abc import ABC
from typing import Type, List

from .sqlite_types import DBInteger


class Column:
    def __init__(self, col_type, foreign_key=None, primary_key=False):
        self.col_type = col_type
        self.foreign_key: ForeignKey = foreign_key
        self.primary_key = primary_key


class ForeignKey:
    def __init__(self, ref_table, ref_column, cascade=False):
        self.ref_table = ref_table
        self.ref_column = ref_column
        self.cascade = cascade


class DBObject(ABC):
    __table_name__ = "table_name"

    def __init__(self, **kwargs):
        print(kwargs)
        for k, v in kwargs.items():
            print(k, v)
            if k in self.columns():
                self.__setattr__(k, v)
            else:
                print("No such attribute ", k)

    def __str__(self):
        return str(self.__dict__)

    def columns(self) -> List[str]:
        return [a for a in dir(self.__class__) if isinstance(getattr(self.__class__, a), Column)]


def get_column(obj, col_name: str) -> Column:
    return getattr(obj.__class__, col_name)


def get_table_name(obj: Type[DBObject]):
    return getattr(obj, "__table_name__")


def create_table_query(cls):
    values = []
    references = []
    columns = tuple(set(dir(cls)) - set(dir(DBObject)))
    columns = [x for x in columns if not callable(getattr(cls, x))]
    for c in columns:
        v = ""
        v += c + " "
        column: Column = getattr(cls, c)
        v += column.col_type.db_type + " "

        if column.primary_key:
            v += "PRIMARY KEY "
            if column.col_type == DBInteger:
                v += "AUTOINCREMENT "

        values.append("\n" + v)

    for c in columns:
        column: Column = getattr(cls, c)
        if column.foreign_key:
            v = ""
            v += f"""\nFOREIGN KEY ({c}) REFERENCES {column.foreign_key.ref_table} ({column.foreign_key.ref_column})"""
            if column.foreign_key.cascade:
                v += " ON DELETE CASCADE"
            references.append(v)

    q = "CREATE TABLE IF NOT EXISTS " + getattr(cls, "__table_name__") + \
        " (\n" + \
        ",".join(values + references) + \
        "\n);"
    return q


def insert_object_query(db_object):
    q = f"INSERT INTO {db_object.__table_name__}"
    params = []

    for c in db_object.columns():
        if get_column(db_object, c).primary_key:
            if get_column(db_object, c).col_type != DBInteger:
                params.append(c)
        else:
            params.append(c)

    q += f" ({','.join(params)})\n"

    vals = []
    for p in params:
        col_type = get_column(db_object, p).col_type
        vals.append(col_type.value_to_str(getattr(db_object, p)))

    q += f"VALUES({','.join(vals)})"

    return q + ";"

