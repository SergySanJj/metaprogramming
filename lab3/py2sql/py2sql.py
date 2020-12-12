class Py2SQL:

    def __init__(self):
        pass

    def db_connect(self, **db):
        pass

    def db_disconnect(self):
        pass

    def db_engine(self):
        pass

    def db_name(self):
        pass

    def db_tables(self):
        pass

    def db_size(self):
        pass

    def db_table_structure(self, table):
        pass

    def db_table_size(self, table):
        pass

    # py -> sql

    def save_object(self, db_object):
        pass

    def save_class(self, db_class):
        pass

    def save_hierarchy(self, root_class):
        pass

    def delete_object(self, db_object):
        pass

    def delete_class(self, db_class):
        pass

    def delete_hierarchy(self, root_class):
        pass
