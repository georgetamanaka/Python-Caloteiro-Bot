import sqlite3

class BotDataBase:
    def __init__(self, dbname="database.db"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)
        self.cursor = self.conn.cursor()

    def setup(self):        
        self.createBalancesTable()
        self.createChatsTable()
        self.createUsersTable()

    """
    CRUD functionality for balance tables.
    """
    def createBalancesTable(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS balance (
            chat_id int,
            creditor_id varchar(20),
            debtor_id varchar(20),
            value float,

            UNIQUE (chat_id, creditor_id, debtor_id)
        );""")

    def createBalance(self, args):
        self.cursor.execute("INSERT OR IGNORE INTO balance (chat_id, creditor_id, debtor_id, value) VALUES (?, ?, ?, ?)", args)
        self.conn.commit()

    def readBalance(self, args):
        self.cursor.execute("SELECT * FROM balance WHERE chat_id = ? AND creditor_id = ? AND debtor_id = ?", args)
        return self.cursor.fetchone()

    def updateBalance(self, args):
        self.cursor.execute("UPDATE balance SET value = ? WHERE chat_id = ? AND creditor_id = ? AND debtor_id = ?", args)
        self.conn.commit()

    def deleteBalance(self, args):
        self.cursor.execute("DELETE FROM balance WHERE chat_id = ? AND creditor_id = ? AND debtor_id = ?", args)
        self.conn.commit()

    """
    CRUD functionality for chats tables.
    """
    def createChatsTable(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS chat_state (
            chat_id int,
            state int,
            creditor_id varchar(20),
            debtor_id varchar(20),
            amount float,

            UNIQUE (chat_id)
        )""")

    def createChat(self, args):
        self.cursor.execute("INSERT OR IGNORE INTO chat_state (chat_id, state) VALUES (?, ?)", args)
        self.conn.commit()

    def readChat(self, args):
        self.cursor.execute("SELECT * FROM chat_state WHERE chat_id = ?", args)
        return self.cursor.fetchone()

    def updateChatState(self, args):
        self.cursor.execute("UPDATE chat_state SET state = ? WHERE chat_id = ?", args)
        self.conn.commit()

    def updateChatCreditor(self, args):
        print("updating chat creditor...")
        self.cursor.execute("UPDATE chat_state SET creditor_id = ? WHERE chat_id = ?", args)
        self.conn.commit()

    def updateChatDebtor(self, args):
        self.cursor.execute("UPDATE chat_state SET debtor_id = ? WHERE chat_id = ?", args)
        self.conn.commit()

    def updateChatAmount(self, args):
        self.cursor.execute("UPDATE chat_state SET amount = ? WHERE chat_id = ?", args)
        self.conn.commit()    
    
    def deletechat(self, args):
        self.cursor.execute("DELETE FROM chat_state WHERE chat_id = ?", args)
        self.conn.commit()

    """
    CRUD functionality for users tables.
    """
    def createUsersTable(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users (
            user_id varchar(20),
            credits float,
            debts float,

            UNIQUE (user_id)
        );""")

    def createUser(self, args):
        self.cursor.execute("INSERT OR IGNORE INTO users (user_id, credits, debts) VALUES (?, ?, ?)", args)
        self.conn.commit()

    def readUser(self, args):
        self.cursor.execute("SELECT * FROM users WHERE user_id = ?", args)
        return self.cursor.fetchone()

    def updateUserCredits(self, args):
        self.cursor.execute("UPDATE users SET credits = ? WHERE user_id = ?", args)
        self.conn.commit()

    def updateUserDebts(self, args):
        self.cursor.execute("UPDATE users SET debts = ? WHERE user_id = ?", args)
        self.conn.commit()

    def searchUser(self, args):
        self.cursor.execute("SELECT * FROM users WHERE user_id = ?", args)
        return self.cursor.fetchone()

    def updateUserCredits(self, args):
        self.cursor.execute("UPDATE users SET credits = ? WHERE user_id = ?", args)
        self.conn.commit()

    def overview(self, args):
        self.cursor.execute("SELECT * FROM balance WHERE chat_id = ?", args)
        vector = self.cursor.fetchall();
        vector.sort(key=lambda x:x[2])

        return vector

    def getAll(self):
        self.cursor.execute("SELECT * FROM balance")

        print("----------------------------")
        for linha in self.cursor.fetchall():
            print(linha)