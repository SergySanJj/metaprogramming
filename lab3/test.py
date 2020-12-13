from py2sql import *
from py2sql.db_object import DBObject, Column, get_table_name, create_table_query, ForeignKey, insert_object_query, \
    foreign_keys
from py2sql.sqlite_types.dict import DBDict
from py2sql.sqlite_types.integer import Integer

db = Py2SQL()
db.db_connect("mydatabase.db")
# print(db.db_name())
#
# print(db.db_tables())
# print(db.db_size())
# print(db.db_table_structure("test4"))
# print(db.db_table_size("test4"))
#
# db.db_disconnect()
from py2sql.sqlite_types.list import DBList
from py2sql.sqlite_types.set import DBSet
from py2sql.sqlite_types.string import String


class A(DBObject):
    __table_name__ = "a_table"
    id = Column(Integer, primary_key=True)


class R(DBObject):
    __table_name__ = "r_table"
    id = Column(Integer, primary_key=True)



class B(DBObject):
    __table_name__ = "b_table"

    val1 = Column(Integer, primary_key=True)
    val2 = Column(String, foreign_key=ForeignKey(A, "id"))
    val3 = Column(Integer, foreign_key=ForeignKey(R, "id", cascade=True))
    val4 = Column(DBList)
    val5 = Column(DBSet)
    val6 = Column(DBDict)

    def test_f(self):
        pass


class C(B):
    __table_name__ = "c_table"

    val7 = Column(Integer)


# print(get_table_name(B))

a = B(val1=123,
      val2="Robert used text",
      val3=4,
      val4=[1, 2, 3],
      val5={1, 2, 3, 4},
      val6={"key": [1, 2]})

# print(a)
# print(a.val1)
#
# print(B.val1)
# print(create_table_query(B))
# print(insert_object_query(a))
#
# print(create_table_query(C))
print(db.save_class(B))
print(foreign_keys(B))
