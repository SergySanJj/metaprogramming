from . import sqlite_type


class Integer(sqlite_type.SQLiteType):
    type_ref = "INTEGER"

    def set_to(self, value):
        if type(value) == int:
            self.val = value
        else:
            raise ValueError

    def __init__(self):
        super().__init__()
