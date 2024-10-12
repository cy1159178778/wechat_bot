import os
import dbm

db_path = os.path.join("data", "db")


class Db:
    db = None
    db_name = None

    def __init__(self, db_name):
        self.db_name = os.path.join(db_path, db_name)
        self.db = dbm.open(self.db_name, 'c')
        # for k, v in self.db.items():
        #     print(f"{k}: {v}")

    def get_db(self):
        if self.db:
            return self.db

        self.db = dbm.open(self.db_name, 'c')
        return self.db

    def set_data(self, key, value):
        db = self.get_db()
        db[key] = value
        self.db.close()
        self.db = None

    def get_data(self, key):
        db = self.get_db()
        value = db.get(key, b"").decode("utf-8")
        return value

    def __del__(self):
        if self.db:
            self.db.close()
