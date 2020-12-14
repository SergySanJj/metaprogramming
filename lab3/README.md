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

### Object operations

To use ORM, data class has to be inherited from DBObject and set ```__table_name__``` argument

```python
class SampleDataClass(DBObject):
    __table_name__ = "sample_table_name"
```

py2sqlite supports next python data types:

int, float, str, list, tuple, dict, set, frozenset, array

They are represented by:

DBInteger, DBFloat, DBString, DBCollection, DBArray, DBDict, DBTuple, DBList, DBSet

```python
from py2sqlite.db_types import *

class SampleDataClass(DBObject):
    __table_name__ = "sample_table_name"

    int_var = Column(DBInteger)
    float_var = Column(DBFloat)
    str_var = Column(DBString)

    arr_var = Column(DBArray)
    coll_var = Column(DBCollection)
    dict_var = Column(DBDict)
    tuple_var = Column(DBTuple)
    list_var = Column(DBList)
    set_var = Column(DBSet)
    
```

Column class has additional parameters:
- foreign_key
- primary_key

One entity can have only one primary key

```python
from py2sqlite import Py2SQL
from py2sqlite.db_objects import *
from py2sqlite.db_types import *

class SampleDataClass(DBObject):
    __table_name__ = "sample_table_name"

    int_var = Column(DBInteger, primary_key=True)
    float_var = Column(DBFloat)
    str_var = Column(DBString)
    
```

To set foreign key use next syntax

```python
from py2sqlite import Py2SQL
from py2sqlite.db_objects import *
from py2sqlite.db_types import *

class A(DBObject):
    __table_name__ = "a_table"
    id = Column(DBInteger, primary_key=True)

class SampleDataClass(DBObject):
    __table_name__ = "sample_table_name"

    int_var = Column(DBInteger, primary_key=True)
    float_var = Column(DBFloat)
    str_var = Column(DBString)
    a_reference = Column(DBInteger,  foreign_key=ForeignKey(A, "id", cascade=True))
    
```

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

db.delete_hierarchy(B)
```
