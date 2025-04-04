import sqlite3  # ou outro banco
import models.connection as database
import csv

db = database.conexao()


class Database:
    def __init__(self, db_name='devgpt.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def execute_script(self, script_path):
        with open(script_path, 'r') as f:
            self.conn.executescript(f.read())

    def insert_from_csv(self, csv_path):
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                self.db.cursor.execute(
                    "INSERT INTO agents (name, description) VALUES (?, ?)",
                    (row['name'], row['description'])
                )
        self.db.conn.commit()

    def close(self):
        self.conn.close()
