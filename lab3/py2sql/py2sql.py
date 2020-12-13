import os
import sqlite3
from typing import List, Tuple, Any, Type
import logging

from py2sql.db_object import DBObject, insert_object_query, create_table_query, foreign_keys


class Py2SQL:

    def __init__(self):
        self.__connection: sqlite3.Connection = None

    @property
    def cursor(self) -> sqlite3.dbapi2.Cursor:
        return self.__connection.cursor()

    def db_connect(self, db_name=":memory:") -> None:
        """
        Connect to the sqlite3 database stored in file with db_name name.
        If db_name was not set - create in memory DB.
        :param db_name:
        :return:
        """
        try:
            self.__connection = sqlite3.connect(db_name)
        except sqlite3.Error:
            logging.exception("Error connecting to database")

    def db_disconnect(self) -> None:
        """
        Disconnect from currently connected database
        :return:
        """
        if self.__connection:
            self.__connection.close()
        else:
            logging.exception("Database was not connected")

    def db_engine(self) -> str:
        """
        Get used db engine name and version
        :return:
        """
        return f"SQLite3 {sqlite3.sqlite_version}"

    def db_name(self, get_paths=False) -> List[str]:
        """
        get_paths=True
            Get list of current databases file names
        get_paths=False
            Get list of current databases file paths

        :param get_paths:
        :return:
        """
        curr_table = self.__run_single_query("PRAGMA database_list;")
        curr_table = [x[2] for x in curr_table]
        if not get_paths:
            curr_table = [os.path.basename(x) for x in curr_table]
        return curr_table

    def db_tables(self) -> List[str]:
        """Get list of all table names available in the connected database"""
        return flatten_structure(self.__run_single_query("SELECT name FROM sqlite_master WHERE type='table';"))

    def db_size(self) -> int:
        """Get size of the connected database in Mb"""
        page_count = self.__run_single_query_flatten("PRAGMA page_count;")[0]
        page_size = self.__run_single_query_flatten("PRAGMA page_size")[0]
        return page_size * page_count / (1024 * 1024)

    def db_table_structure(self, table) -> List[Tuple[int, str, str]]:
        """Get list of tuples with info about table attributes [(id:int, name:str, type:str)]"""
        res = self.__run_single_query(f"PRAGMA table_info('{table}')")
        return [(int(x[0]), str(x[1]), str(x[2])) for x in res]

    def db_table_size(self, table):
        """Get estimated size of the table in Mb"""
        return self.__run_single_query_flatten(f"""
            SELECT COUNT(*) *  -- The number of rows in the table
             ( 24 +        -- The length of all 4 byte int columns
               12 +        -- The length of all 8 byte int columns
               128 )       -- The estimate of the average length of all string columns
            FROM {table}
            """)[0] / (1024 * 1024)

    # py -> sql

    def save_object(self, db_object: Type[DBObject]):
        # TODO: add check on primary keys already exist
        q = insert_object_query(db_object)
        self.__run_single_query(q)

    def save_class(self, db_class: Type[DBObject]):
        # TODO: add check if table exists -> modify it
        col_info = self.__run_single_query(f"PRAGMA table_info('{db_class.__table_name__}')")
        print(col_info)
        if len(col_info) > 0:
            print("NEEDS to modify")
        else:
            q = create_table_query(db_class)
            fk = foreign_keys(db_class)
            for k in fk:
                pass

            print(q)
            self.__run_single_query(q)

    def save_hierarchy(self, root_class):
        pass

    def delete_object(self, db_object: Type[DBObject]):
        pass

    def delete_class(self, db_class):
        pass

    def delete_hierarchy(self, root_class):
        pass

    def __run_single_query(self, query) -> List[Any]:
        cursor = self.cursor
        cursor.execute(query)
        return cursor.fetchall()

    def __run_single_query_flatten(self, query) -> List[Any]:
        return flatten_structure(self.__run_single_query(query))


def flatten_structure(structure) -> List[Any]:
    return [i for level in structure for i in level]
