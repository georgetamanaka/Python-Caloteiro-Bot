import logging
import time

from telegram import ForceReply, ChatAction, ReplyKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from dbhelper import DBHelper

CHAT_ID, CHAT_STATE, CREDITOR_ID, DEBTOR_ID, VALUE_AMT = range(5)

def get_chat(db, id, state):
	id = int(id)
	
	chat = db.search_chat((id, )) 

	if(chat == None):
		db.insert_chat((id, state))
	else:
		db.update_chat_state((state, id))

	return chat

def unknow(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="Comando inválido.", reply_to_message_id=update.message.message_id, reply_markup=ForceReply(True, True))

def start(bot, update):
	custom_keyboard = [['/emprestimo', '/pagamento'], 
						['/overview', '/dividas']]

	
	bot.send_message(chat_id=update.message.chat_id, 
					text="Olá, eu sou o caloteiroBot", 
					reply_markup=ReplyKeyboardMarkup(custom_keyboard))

def loan(bot, update):
	db = DBHelper()

	get_chat(db, update.message.chat_id, 0)

	bot.send_message(chat_id=update.message.chat_id, 
					text="Quem emprestou?", 
					reply_to_message_id = update.message.message_id,
					reply_markup=ForceReply(True, False), 
					parse_mode=ParseMode.HTML)

def payment(bot, update):
	db = DBHelper()

	get_chat(db, update.message.chat_id, 3)

	bot.send_message(chat_id=update.message.chat_id, 
					text="Quem emprestou?", 
					reply_markup=ForceReply(True, False))

def ask_for_creditor(bot, update, db):
	db.update_chat_creditor((update.message.text, update.message.chat_id))
	
	bot.send_message(chat_id=update.message.chat_id, 
					text="Quem pegou emprestado?", 
					reply_markup=ForceReply(True, False))

def ask_for_value(bot, update, db):
	db.update_chat_debtor((update.message.text, update.message.chat_id))
	
	bot.send_message(chat_id=update.message.chat_id, 
					text="Qual o valor?", 
					reply_markup=ForceReply(True, False))


def getBalance(db, chat, amount):
	args = (chat[CHAT_ID], chat[CREDITOR_ID], chat[DEBTOR_ID])

	balance = db.search_balance(args)

	if(balance == None):
		args = (chat[CHAT_ID], chat[CREDITOR_ID], chat[DEBTOR_ID], amount)
		db.insert_balance(args)
	else:
		amount = balance[3] + amount

		if (amount == 0):
			db.remove_balance(args)
		else:
			args = (amount, chat[CHAT_ID], chat[CREDITOR_ID], chat[DEBTOR_ID])
			db.update_balance(args)
		
		db.get_all()

	return balance


def finishLoan(bot, update, db, chat):
	balance = getBalance(db, chat, float(update.message.text))

	message = "<b>Emprestimo registrado!</b>💰\n" \
			"Credor: " + balance[1] + \
			"\nCaloteiro: " + balance[2] + \
			"\n<i>Valor: R$" + update.message.text + \
			'\n\n</i>"Aceita vale-refeição?"' \
			"\n<i>- Julius</i>"

	bot.send_message(chat_id=update.message.chat_id, 
					text=message, 
					parse_mode=ParseMode.HTML)

	db.update_chat_state((-1, int(update.message.chat_id)))


def finishPayment(bot, update, db, chat_info):	
	getBalance(db, chat_info, -float(update.message.text))

	message = "<b>Pagamento registrado!</b>💰\n" + \
	          "Credor: " + str(chat_info[2]) + \
	          "\nCaloteiro: " + str(chat_info[3]) + \
	          "\n<i>Valor: R$" + str(float(update.message.text)) + \
              '\n\n</i>Aceita vale-refeição?"' \
              "\n<i>- Julius</i>"

	bot.send_message(chat_id=update.message.chat_id, 
					text=message, 
					parse_mode=ParseMode.HTML)

	db.update_chat_state((-1, int(update.message.chat_id)))

def balance_overview(bot, update):
	db = DBHelper()
	db.setup()

	nDebtor = 1
	debtor = ""
	chatBalance = db.overview((int(update.message.chat_id), ))
	message = "<b>Balanço de dívidas</b>💰\n"

	for transaction in chatBalance:
		if(transaction[2] != debtor):
			debtor = transaction[2]
			message += "\n" + str(nDebtor) + ". " + debtor + " deve:\n"
			nDebtor += 1

		message += "para " + transaction[1] + " R$" + str(transaction[3]) + "\n"

	bot.send_message(chat_id=update.message.chat_id, text=message, parse_mode=ParseMode.HTML)

def control(bot, update):
	db = DBHelper()
	
	#fetch chat infos (id, state)
	chat = get_chat(db, update.message.chat_id, -1) 
		
	state = chat[1]

	if(state == 0):
		ask_for_creditor(bot, update, db)
		db.update_chat_state((1, int(update.message.chat_id)))
	
	elif(state == 1):
		ask_for_value(bot, update, db)
		db.update_chat_state((2, int(update.message.chat_id)))
	
	elif(state == 2):
		finishLoan(bot, update, db, chat)
	
	elif(state == 3):
		ask_for_creditor(bot, update, db)
		db.update_chat_state((4, int(update.message.chat_id)))
	
	elif(state == 4):
		ask_for_value(bot, update, db)
		db.update_chat_state((5, int(update.message.chat_id)))
	
	elif(state == 5):
		finishPayment(bot, update, db, chat)

def main():
	updater = Updater(token='517500543:AAGRhhagJCuwESGJI1Ye2iSQb32POHZsnm4')
	dispatcher = updater.dispatcher
	
	logging.basicConfig(level=logging.DEBUG,
	                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	
	dispatcher.add_handler(CommandHandler('start', start))
	dispatcher.add_handler(CommandHandler('emprestimo', loan))
	dispatcher.add_handler(CommandHandler('pagamento', payment))
	dispatcher.add_handler(CommandHandler('overview', balance_overview))
	dispatcher.add_handler(MessageHandler(Filters.text, control))
	dispatcher.add_handler(MessageHandler(Filters.command, unknow))

	updater.start_polling()
	updater.idle()

if __name__ == '__main__':
	main()
