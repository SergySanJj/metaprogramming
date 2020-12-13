# py2sqlite


## install
```
pip install py2sqlite==0.4.0
```

To use py2sqlite in your project include this dependencies
```python
from py2sqlite import Py2SQL
from py2sqlite.db_objects import *
from py2sqlite.db_types import *
```

## Documentation 

<a href="docs/py2sqlite.html">Documentation</a>

## Connection

SQLite is file and in-memody database, to connect to certain db use:
```python
# creates db class
db = Py2SQL()
# connects to mydatabase.db or creates it if it does not exist
db.db_connect("mydatabase.db") 
# disconnect from current db
db.db_disconnect()
```

## Database info

Get db engine info
```python
db.db_engine()
```

Get list of current databases filenames or full paths
```python
db.db_name()
```

Get tables available in the connected database
```python
db.db_tables()
```

Get size of the connected database
```python
db.db_size()
```

Get list of tuples with info about table attributes
```python
db.db_table_structure()
```

Get estimated size of table
```python
db.db_table_size()
```

## Usage sample

```python

```
