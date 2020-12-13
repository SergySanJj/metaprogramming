from . import sqlite_type


class Integer(sqlite_type.SQLiteType):
    type_ref = "INTEGER"

    def __init__(self):
        super().__init__()

    @staticmethod
    def value_to_str(val) -> str:
        return str(val)

    @staticmethod
    def convert_from_db(val):
        return val
