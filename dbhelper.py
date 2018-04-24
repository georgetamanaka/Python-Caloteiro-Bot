import sqlite3

class DBHelper:
    def __init__(self, dbname="database.db"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)
        self.cursor = self.conn.cursor()

    def setup(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS balance (
            chat_id varchar(10),
            creditor_id varchar(20),
            debtor_id varchar(20),
            value float
        );""")

    def select_register(self, args):
        #args = (str(chat_id), creditor_username, debtor_username)
        self.cursor.execute("SELECT * FROM balance WHERE chat_id = ? AND creditor_id = ? AND debtor_id = ?", args)

        return self.cursor.fetchone()

    def delete_register(self, args):
        self.cursor.execute("DELETE * FROM balance WHERE chat_id = ? AND creditor_id = ? AND debtor_id = ?", args)

    def update_register(self, args):
        self.cursor.execute("UPDATE balance SET value = ? WHERE chat_id = ? AND creditor_id = ? AND debtor_id = ?", args)

    def add_register(self, args):
        #reg = self.select_register(str(chat_id), creditor_username, debtor_username)

        #if (reg == None):
        #   args = (str(chat_id), creditor_username, debtor_username, round(value, 2))
        self.cursor.execute("INSERT INTO balance (chat_id, creditor_id, debtor_id, value) VALUES (?, ?, ?, ?)", args)
        #else:
        #   self.update_register(args)
            
        self.conn.commit()

    def overview_chat(self, chat_id):
        arg1 = (str(chat_id),)
        self.cursor.execute("SELECT * FROM balance WHERE chat_id = ?", arg1)

        #user = ""
        vector = self.cursor.fetchall();
        vector.sort(key=lambda x:x[2])

        #print ("Balanço de dívidas:")

        #i = 0

        #for linha in vector:
        #   if(user != linha[2]):
        #       i += 1
        #       print ("\n" + str(i) + ". " + linha[2] + " deve:")
        #       user = linha[2]
        #   
        #   print ("para " + linha[1] + " " + str(linha[3]))

    def get_all(self):
        self.cursor.execute("SELECT * FROM balance")

        for linha in self.cursor.fetchall():
            print(linha)

