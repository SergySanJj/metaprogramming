from . import sqlite_type


class String(sqlite_type.SQLiteType):
    type_ref = "TEXT"

    def __init__(self):
        super().__init__()

    @staticmethod
    def value_to_str(val) -> str:
        return f"'{str(val)}'"
