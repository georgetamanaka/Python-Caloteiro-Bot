import sqlite3

class DBHelper:
    def __init__(self, dbname="test.db"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)
        self.cursor = self.conn.cursor()

    def setup(self):

        self.conn.execute("""CREATE TABLE IF NOT EXISTS balance (
            chat_id text
        );
        """)

        self.conn.commit()

    def add_item(self):
        
        #self.conn.execute("""INSERT INTO balance (chat_id, creditor_username, debtor_username, debt_value) \
        #    SELECT name FROM (SELECT ?, ?, ?, ?) as tmp
        #   WHERE NOT EXISTS (
        #        SELECT chat_id, creditor_username, debtor_username FROM balance WHERE chat_id = ?,
        #        creditor_username = ?, debtor_username = ?
        #       ) LIMIT 1""", (chat_id, creditor_username, debtor_username, debt_value))


        self.conn.execute("""INSERT INTO balance (chat_id) \
            VALUES ('george')""")

        self.conn.commit()

    def get_all(self):
        self.cursor.execute("""
        SELECT * FROM balance""")

        for linha in self.cursor.fetchall():
            print(linha) 