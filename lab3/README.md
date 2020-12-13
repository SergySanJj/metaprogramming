# py2sqlite
ORM for Python 3 and SQLite 


# Installation
```
pip install py2sqlite
```

# Documentation 

<a href="/docs/py2sqlite.html">Link</a>


# Usage
```python
from py2sqlite import *
```

### Connection

SQLite is file and in-memody database, to connect to certain db use:
```python
# creates db class
db = Py2SQL()
# connects to mydatabase.db or creates it if it does not exist
db.db_connect("mydatabase.db") 
# disconnect from current db
db.db_disconnect()
```

### Database info

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

### Usage example

```python

```