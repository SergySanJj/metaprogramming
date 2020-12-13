from . import sqlite_type
import json
import jsonpickle


class DBSet(sqlite_type.SQLiteType):
    type_ref = "TEXT"

    def __init__(self):
        super().__init__()

    @staticmethod
    def value_to_str(val) -> str:
        return f"'{json.dumps(jsonpickle.encode(val))}'"

    @staticmethod
    def convert_from_db(val):
        return jsonpickle.decode(val)
