import sqlite3  # ou outro banco
import models.connection as database

db = database.conexao()


class Database:
    def __init__(self, db_name='devgpt.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def execute_script(self, script_path):
        with open(script_path, 'r') as f:
            self.conn.executescript(f.read())

    def close(self):
        self.conn.close()
