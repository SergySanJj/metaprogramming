from py2sql import *


db = Py2SQL()
db.db_connect("mydatabase.db")
print(db.db_name())

print(db.db_tables())
print(db.db_size())

db.db_disconnect()

