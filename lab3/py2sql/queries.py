from typing import Type

from .db_objects import DBObject
from .db_types import DBInteger


def create_table_query(cls: Type[DBObject]):
    values = []
    references = []
    for c in cls.class_columns():
        v = c.name + " " + c.col_type.db_type + " "

        if c.primary_key:
            v += "PRIMARY KEY "
            if c.col_type == DBInteger:
                v += "AUTOINCREMENT "

        values.append("\n" + v)

    for c in cls.class_columns():
        if c.foreign_key:
            v = f"\nFOREIGN KEY ({c.name}) REFERENCES {c.foreign_key.ref_table.__table_name__} " \
                f"({c.foreign_key.ref_column})"
            if c.foreign_key.cascade:
                v += " ON DELETE CASCADE"
            references.append(v)

    q = "CREATE TABLE IF NOT EXISTS " + cls.__table_name__ + \
        " (\n" + ",".join(values + references) + "\n);"
    return q


def insert_object_query(db_object: DBObject):
    q = f"INSERT INTO {db_object.__table_name__}"

    params, vals = [], []
    for c in db_object.obj_columns():
        append = False
        if c.primary_key:
            if c.col_type != DBInteger:
                append = True
        else:
            append = True

        if append:
            params.append(c.name)
            val = getattr(db_object, c.name)
            vals.append(c.col_type.value_to_str(val))

    q += f" ({','.join(params)})\n"
    q += f"VALUES({','.join(vals)})"

    return q + ";"
