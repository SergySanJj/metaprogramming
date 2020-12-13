from py2sql import *


db = Py2SQL()
db.db_connect("mydatabase.db")
print(db.db_name())

print(db.db_tables())
print(db.db_size())
print(db.db_table_structure("test4"))
print(db.db_table_size("test4"))

db.db_disconnect()

