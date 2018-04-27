import logging
import time

from telegram import ForceReply, ChatAction, ReplyKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from dbhelper import DBHelper

def unknow(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="Comando inválido.", reply_to_message_id=update.message.message_id, reply_markup=ForceReply(True, True))

def start(bot, update):
	custom_keyboard = [['/emprestimo', '/pagamento'], ['/overview', '/dividas']]
	reply_markup = ReplyKeyboardMarkup(custom_keyboard)
	bot.send_message(chat_id=update.message.chat_id, text="Olá, eu sou o caloteiroBot", reply_markup=reply_markup)

def loan(bot, update):
	db = DBHelper()
	db.setup()

	chat = db.search_chat((int(update.message.chat_id), )) 

	if(chat == None):
		arg1 = (int(update.message.chat_id), 0)
		db.insert_chat(arg1)
	
	db.update_chat_state((0, int(update.message.chat_id)))
	bot.send_message(chat_id=update.message.chat_id, text="Quem emprestou?", reply_markup=ForceReply(True, False))

def payment(bot, update):
	db = DBHelper()
	db.setup()

	chat = db.search_chat((int(update.message.chat_id), )) 

	if(chat == None):
		arg1 = (int(update.message.chat_id), 3)
		db.insert_chat(arg1)
	
	db.update_chat_state((3, int(update.message.chat_id)))
	bot.send_message(chat_id=update.message.chat_id, text="Quem emprestou?", reply_markup=ForceReply(True, False))

def ask_for_creditor(bot, update, db):
	db.update_chat_creditor((update.message.text, update.message.chat_id))
	bot.send_message(chat_id=update.message.chat_id, text="Quem pegou emprestado?", reply_markup=ForceReply(True, False))

def ask_for_value(bot, update, db):
	db.update_chat_debtor((update.message.text, update.message.chat_id))
	bot.send_message(chat_id=update.message.chat_id, text="Qual o valor?", reply_markup=ForceReply(True, False))

def finish_loan(bot, update, db, chat):
	value = float(update.message.text)
	transaction = db.search_balance((chat[0], chat[2], chat[3])) 

	if(transaction == None):
		db.insert_balance((chat[0], chat[2], chat[3], value))
	else:
		value = transaction[3] + float(update.message.text)
		db.update_balance((value, chat[0], chat[2], chat[3]))

	message = '<b>Emprestimo registrado!</b>💰\nCredor: ' + str(chat[2]) + "\nCaloteiro: " + str(chat[3]) + "\n<i>Valor: R$" + str(value) + '</i>\n\n"Aceita vale-refeição?"\n<i>- Julius</i>'
	bot.send_message(chat_id=update.message.chat_id, text=message, parse_mode=ParseMode.HTML)
	db.update_chat_state((-1, int(update.message.chat_id)))
	db.get_all()

def finish_payment(bot, update, db, chat):
	value = float(update.message.text)
	transaction = db.search_balance((chat[0], chat[2], chat[3])) 

	if(transaction == None):
		db.insert_balance((chat[0], chat[2], chat[3], value))
	else:
		value = transaction[3] - float(update.message.text)
		db.update_balance((value, chat[0], chat[2], chat[3]))

	message = '<b>Pagamento registrado!</b>💰\nCredor: ' + str(chat[2]) + "\nCaloteiro: " + str(chat[3]) + "\n<i>Valor: R$" + str(value) + '</i>\n\n"Aceita vale-refeição?"\n<i>- Julius</i>'
	bot.send_message(chat_id=update.message.chat_id, text=message, parse_mode=ParseMode.HTML)
	db.update_chat_state((-1, int(update.message.chat_id)))
	db.get_all()

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

def message(bot, update):
	db = DBHelper()
	db.setup()

	chat = db.search_chat((int(update.message.chat_id), )) 

	if(chat == None):
		start(bot, update)
	else:
		state = int(chat[1])

		if(state == 0):
			ask_for_creditor(bot, update, db)
			db.update_chat_state((1, int(update.message.chat_id)))
		elif(state == 1):
			ask_for_value(bot, update, db)
			db.update_chat_state((2, int(update.message.chat_id)))
		elif(state == 2):
			finish_loan(bot, update, db, chat)
		elif(state == 3):
			ask_for_creditor(bot, update, db)
			db.update_chat_state((4, int(update.message.chat_id)))
		elif(state == 4):
			ask_for_value(bot, update, db)
			db.update_chat_state((5, int(update.message.chat_id)))
		elif(state == 5):
			finish_payment(bot, update, db)

def main():
	updater = Updater(token='517500543:AAGRhhagJCuwESGJI1Ye2iSQb32POHZsnm4')
	dispatcher = updater.dispatcher
	
	logging.basicConfig(level=logging.DEBUG,
	                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	
	dispatcher.add_handler(CommandHandler('start', start))
	dispatcher.add_handler(CommandHandler('emprestimo', loan))
	dispatcher.add_handler(CommandHandler('pagamento', payment))
	dispatcher.add_handler(CommandHandler('overview', balance_overview))
	dispatcher.add_handler(MessageHandler(Filters.text, message))
	dispatcher.add_handler(MessageHandler(Filters.command, unknow))

	updater.start_polling()
	updater.idle()

if __name__ == '__main__':
	main()
