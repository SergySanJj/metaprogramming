import os
import sqlite3
from typing import List, Tuple, Any, Type
import logging

from py2sqlite.db_objects import DBObject, ForeignKey
from .db_types import DBInteger
from .queries import insert_object_query, create_table_query, find_object_by_pk_query, update_object_by_pk_query, \
    modify_table_query, delete_object_query, delete_table_query


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

    def save_object(self, db_object: DBObject):
        p_k = db_object.obj_primary_keys()
        p_k = [x for x in p_k if x.col_type != DBInteger]
        if len(p_k) == 0 or len(self._find_by_pk(db_object)) == 0:
            q = insert_object_query(db_object)
            self.__run_single_query(q, commit=True)
        else:
            q = update_object_by_pk_query(db_object)
            self.__run_single_query(q, commit=True)

    def _find_by_pk(self, db_object: DBObject):
        q = find_object_by_pk_query(db_object, False)
        return self.__run_single_query_flatten(q)

    def save_class(self, db_class: Type[DBObject]):
        col_info = self.__run_single_query(f"PRAGMA table_info('{db_class.__table_name__}')")
        # print(col_info)
        if len(col_info) > 0:
            q = modify_table_query(db_class, col_info)
            print(q)
            # cursor = self.cursor
            # cursor.executescript(q)
            # self.__connection.commit()
            pass
        else:
            q = create_table_query(db_class)
            refs: List[Type[DBObject]] = []
            Py2SQL.__traverse_references(db_class, refs)

            for k in refs:
                self.save_class(k)

            # print(q)
            self.__run_single_query(q, commit=True)

    @staticmethod
    def __traverse_references(root: Type[DBObject], res: List[Any]) -> List[Type[DBObject]]:
        fk: List[ForeignKey] = root.class_foreign_keys()
        for k in fk:
            ref = k.ref_table
            if ref not in res:
                res.append(ref)
                Py2SQL.__traverse_references(ref, res)
        return res

    def save_hierarchy(self, root_class: Type[DBObject]):
        self.save_class(root_class)
        subclasses = root_class.__subclasses__()
        for s in subclasses:
            self.save_hierarchy(s)

    def delete_object(self, db_object: DBObject):
        q = delete_object_query(db_object)
        self.__run_single_query(q, commit=True)

    def delete_class(self, db_class: Type[DBObject]):
        q = delete_table_query(db_class)
        self.__run_single_query(q, commit=True)

    def delete_hierarchy(self, root_class):
        self.delete_class(root_class)
        subclasses = root_class.__subclasses__()
        for s in subclasses:
            self.delete_hierarchy(s)

    def __run_single_query(self, query, commit=False) -> List[Any]:
        cursor = self.cursor
        cursor.execute(query)
        res = cursor.fetchall()
        if commit:
            self.__connection.commit()
        return res

    def __run_single_query_flatten(self, query) -> List[Any]:
        return flatten_structure(self.__run_single_query(query))


def flatten_structure(structure) -> List[Any]:
    return [i for level in structure for i in level]
