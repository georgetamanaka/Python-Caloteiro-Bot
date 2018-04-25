import sqlite3

class DBHelper:
    def __init__(self, dbname="database.db"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)
        self.cursor = self.conn.cursor()

    def setup(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS balance (
            chat_id int,
            creditor_id varchar(20),
            debtor_id varchar(20),
            value float
        );""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS chat_state (
            chat_id int,
            state int,
            creditor_id varchar(20),
            debtor_id varchar(20)
        );""")

    def search_chat(self, args):
        self.cursor.execute("SELECT * FROM chat_state WHERE chat_id = ?", args)
        return self.cursor.fetchone()

    def remove_chat(self, args):
        self.cursor.execute("DELETE * FROM chat_state WHERE chat_id = ?", args)
        self.conn.commit()

    def update_chat_state(self, args):
        self.cursor.execute("UPDATE chat_state SET state = ? WHERE chat_id = ?", args)
        self.conn.commit()

    def update_chat_creditor(self, args):
        self.cursor.execute("UPDATE chat_state SET creditor_id = ? WHERE chat_id = ?", args)
        self.conn.commit()

    def update_chat_debtor(self, args):
        self.cursor.execute("UPDATE chat_state SET debtor_id = ? WHERE chat_id = ?", args)
        self.conn.commit()

    def insert_chat(self, args):
        self.cursor.execute("INSERT INTO chat_state (chat_id, state) VALUES (?, ?)", args)
        self.conn.commit()

    def search_balance(self, args):
        self.cursor.execute("SELECT * FROM balance WHERE chat_id = ? AND creditor_id = ? AND debtor_id = ?", args)
        return self.cursor.fetchone()

    def remove_balance(self, args):
        self.cursor.execute("DELETE * FROM balance WHERE chat_id = ? AND creditor_id = ? AND debtor_id = ?", args)
        self.conn.commit()

    def update_balance(self, args):
        self.cursor.execute("UPDATE balance SET value = ? WHERE chat_id = ? AND creditor_id = ? AND debtor_id = ?", args)
        self.conn.commit()

    def insert_balance(self, args):
        self.cursor.execute("INSERT INTO balance (chat_id, creditor_id, debtor_id, value) VALUES (?, ?, ?, ?)", args)
        self.conn.commit()

    def overview(self, args):
        self.cursor.execute("SELECT * FROM balance WHERE chat_id = ?", args)
        vector = self.cursor.fetchall();
        vector.sort(key=lambda x:x[2])

        return vector

    def get_all(self):
        self.cursor.execute("SELECT * FROM balance")

        print("printandooooo")
        for linha in self.cursor.fetchall():
            print(linha)