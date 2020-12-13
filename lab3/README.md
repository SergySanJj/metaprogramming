# py2sqlite
ORM for Python 3 and SQLite 


# Installation
```
pip install py2sqlite
```


# Documentation 

<a href="docs/py2sqlite.html">Link</a>

# Usage

### Connection

Create Py2SQL class
```python
db = Py2SQL()
```

Connects to db file or create it if it does not exist
```python
db.db_connect("mydatabase.db")
```

Disconnect from current db
```python
db.db_disconnect()
```


### Database info

Db engine name and version
```python
db.db_engine()
```

List of current databases filenames
```python
db.db_name()
```

Tables available in the connected database
```python
db.db_tables()
```

Size of the connected database
```python
db.db_size()
```

List of tuples with info about table attributes
```python
db.db_table_structure()

```

Get estimated size of table
```python
db.db_table_size()
```

### 

### Usage example

```python
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

    r_ref = Column(DBInteger, foreign_key=ForeignKey(R, "id", cascade=True))
    a_ref = Column(DBInteger, foreign_key=ForeignKey(A, "id", cascade=True))

    def test_f(self):
        pass


# C will inherit all B fields and add specific own
class C(B):
    __table_name__ = "c_table"

    val7 = Column(DBInteger)
    r_ref = Column(DBInteger, foreign_key=ForeignKey(R, "id"))


db.save_class(A)
db.save_class(R)
db.save_hierarchy(B)

r = R(some_field="some string")

a = A(r_ref=1)

b = B(val2="Robert used text",
      r_ref=1,
      a_ref=1,
      val4=[1, 2, 3],
      val5={1, 2, 3, 4},
      val6={"key": [1, 2]})

c = C(val2="Robert used text",
      r_ref=1,
      a_ref=1,
      val4=[1, 2, 3],
      val5={1, 2, 3, 4},
      val6={"key": [1, 2]},
      val7=12)

objects = [r, a, b, c]
for i in range(5):
    for o in objects:
        db.save_object(o)

db.delete_object(a)


# This object will have string primary key and so only single row with equal pk will exist
class StrPrim(DBObject):
    __table_name__ = "str_table"

    str_val = Column(DBString, primary_key=True)
    other_val = Column(DBString)


str_pr = StrPrim(str_val="sssss", other_val="ab")

db.save_class(StrPrim)
db.save_object(str_pr)
db.save_object(str_pr)
db.save_object(str_pr)
```
