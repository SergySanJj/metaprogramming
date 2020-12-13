from py2sqlite import *

from py2sqlite import Py2SQL
from py2sqlite.db_objects import *
from py2sqlite.db_types import *

db = Py2SQL()
db.db_connect("mydatabase.db")


class R(DBObject):
    __table_name__ = "r_table"
    id = Column(DBInteger, primary_key=True)


class A(DBObject):
    __table_name__ = "a_table"
    id = Column(DBInteger, primary_key=True)
    r_ref = Column(DBInteger, foreign_key=ForeignKey(R, "id", cascade=True))


class B(DBObject):
    __table_name__ = "b_table"

    val1 = Column(DBInteger, primary_key=True)
    val2 = Column(DBString, foreign_key=ForeignKey(A, "id"))
    val3 = Column(DBInteger, foreign_key=ForeignKey(R, "id", cascade=True))

    val4 = Column(DBList)
    val5 = Column(DBSet)
    val6 = Column(DBDict)

    def test_f(self):
        pass


class C(B):
    __table_name__ = "c_table"

    val7 = Column(DBInteger)

    r_ref = Column(DBInteger, foreign_key=ForeignKey(R, "id"))


a = B(val1=123,
      val2="Robert used text",
      val3=4,
      val4=[1, 2, 3],
      val5={1, 2, 3, 4},
      val6={"key": [1, 2]})

db.save_class(B)


db.save_hierarchy(B)
db.save_object(a)
db.delete_hierarchy(R)


db.delete_object(a)


class StrPrim(DBObject):
    __table_name__ = "str_table"

    str_val = Column(DBString, primary_key=True)
    other_val = Column(DBString)


str_pr = StrPrim(str_val="sssss", other_val="ab")

db.save_class(StrPrim)

db.save_object(str_pr)
