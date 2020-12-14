from py2sqlite import Py2SQL
from py2sqlite.db_objects import *
from py2sqlite.db_types import *

db = Py2SQL()
db.db_connect("mydatabase.db")


class R(DBObject):
    __table_name__ = "r_table"
    id = Column(DBInteger, primary_key=True)
    some_field = Column(DBString)


class A(DBObject):
    __table_name__ = "a_table"
    id = Column(DBInteger, primary_key=True)
    r_ref = Column(DBInteger, foreign_key=ForeignKey(R, "id", cascade=True))


class B(DBObject):
    __table_name__ = "b_table"

    # Integer primary keys are automatically assigned as autoincremental values
    val1 = Column(DBInteger, primary_key=True)
    val2 = Column(DBString)
    val4 = Column(DBList)
    val5 = Column(DBSet)
    val6 = Column(DBDict)

    # aggregation
    val_a = Column(A)
    r_ref = Column(DBInteger, foreign_key=ForeignKey(R, "id", cascade=True))

    def test_f(self):
        pass


# C will inherit all B fields and add specific own
class C(B):
    __table_name__ = "c_table"
    additional = Column(DBInteger, primary_key=True)


# Even if next 2 lines will be commented out, tables A and R will be saved
# due to the outgoing references in B
db.save_class(A)
db.save_class(R)

db.save_hierarchy(B)

r = R(some_field="some string")
db.save_object(r)

b = B(val2="Robert used text",
      r_ref=db.max_id(R, "id"),
      val_a=A(r_ref=db.max_id(R, "id")),
      val4=[1, 2, 3],
      val5={1, 2, 3, 4},
      val6={"key": [1, 2]})

c = C(val2="Other",
      r_ref=db.max_id(R, "id"),
      val_a=A(r_ref=db.max_id(R, "id")),
      val4=[1],
      val5={1},
      val6={"key": [1, 2]},
      additional=2)

db.save_object(c)
db.save_object(b)

# User will get warning from this class because it does not have a primary key to be referenced
class NoPk(DBObject):
    __table_name__ = "str_table"

    other_val = Column(DBInteger)


# This object will have string primary key and so only single row with equal pk will exist
class StrPrim(DBObject):
    __table_name__ = "str_table"

    str_val = Column(DBString, primary_key=True)
    other_val = Column(DBString)
    # no_ref = Column(DBInteger, foreign_key=ForeignKey(NoPk, "other_val", cascade=True))


str_pr = StrPrim(str_val="sss", other_val="ab")

db.save_class(StrPrim)
db.save_object(str_pr)
db.save_object(str_pr)
db.save_object(str_pr)
