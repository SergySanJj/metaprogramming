from py2sql import *
from py2sql.db_object import DBObject, Column, get_table_name, create_table_query, ForeignKey, insert_object_query
from py2sql.sqlite_types.integer import Integer


# db = Py2SQL()
# db.db_connect("mydatabase.db")
# print(db.db_name())
#
# print(db.db_tables())
# print(db.db_size())
# print(db.db_table_structure("test4"))
# print(db.db_table_size("test4"))
#
# db.db_disconnect()
from py2sql.sqlite_types.string import String


class B(DBObject):
    __table_name__ = "b_table"

    val1 = Column(Integer, primary_key=True)
    val2 = Column(String, foreign_key=ForeignKey("A", "id"))
    val3 = Column(Integer, foreign_key=ForeignKey("R", "id", cascade=True))

    def test_f(self):
        pass


print(get_table_name(B))

a = B(val1=123, val2="Robert used text", val3=4)

print(a)
print(a.val1)

print(B.val1)
print(create_table_query(B))
print(insert_object_query(a))
