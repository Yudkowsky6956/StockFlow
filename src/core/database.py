import sqlite3

from .vars import HASH_DATABASE


class Database:
    @property
    def cursor(self):
        connection = sqlite3.connect(HASH_DATABASE)
        return connection.cursor()

    # def