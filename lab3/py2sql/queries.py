from typing import Type, List

from .db_objects import DBObject, Column
from .db_types import DBInteger


def create_table_query(cls: Type[DBObject]) -> str:
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


def insert_object_query(db_object: DBObject) -> str:
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


def delete_object_query(db_object: DBObject) -> str:
    q = f"DELETE FROM {db_object.__table_name__}\n"
    cols = [c for c in db_object.obj_columns() if not (c.primary_key and c.col_type == DBInteger)]
    q += form_statement(db_object, cols)
    return q + ";"


def delete_table_query(cls: Type[DBObject]) -> str:
    q = f"DROP TABLE IF EXISTS {cls.__table_name__};"
    return q


def find_object_by_pk_query(db_object: DBObject, default_pk=True) -> str:
    q = f"SELECT * FROM {db_object.__table_name__}\n"

    p_k = db_object.obj_primary_keys()
    if not default_pk:
        p_k = [x for x in p_k if x.col_type != DBInteger]

    q += form_statement(db_object, p_k, statement="WHERE")
    return q + ";"


def update_object_by_pk_query(db_object: DBObject) -> str:
    q = f"UPDATE {db_object.__table_name__}\n"

    columns = db_object.obj_columns()
    columns = [x for x in columns if not x.primary_key]

    q += form_statement(db_object, columns, statement="SET")
    q += form_statement(db_object, db_object.obj_primary_keys(), statement="WHERE")

    return q + ";"


def form_statement(db_object: DBObject, columns: List[Column], statement="WHERE") -> str:
    options = []
    for p in columns:
        s = f"{p.name} = {p.col_type.value_to_str(getattr(db_object, p.name))}"
        options.append(s)
    where = ""
    if len(options) > 0:
        where = f" {statement} " + " AND ".join(options)
    return where
