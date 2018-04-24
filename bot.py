import logging
import time
from telegram import ForceReply, ChatAction, ReplyKeyboardMarkup
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
	bot.send_message(chat_id=update.message.chat_id, text="Quem emprestou? 💸", reply_markup=ForceReply(True, True))

def payment(bot, update):
	arg1 = (int(update.message.chat_id), )
	chat = db.search_chat(arg1) 

	if(chat == None):
		arg1 = (int(update.message.chat_id), 0)
		db.insert_chat(arg1)

	#bot.send_message(chat_id=update.message.chat_id, text=update.message.text)

def message(bot, update):
	db = DBHelper()
	db.setup()

	chat = db.search_chat((int(update.message.chat_id), )) 
	print("chaaat: " + str(chat))

	if(chat == None):
		start(bot, update)
	else:
		state = int(chat[1])

		if(state == 0):
			db.update_chat_creditor((update.message.text, update.message.chat_id))
			db.update_chat_state((1, int(update.message.chat_id)))
			bot.send_message(chat_id=update.message.chat_id, text="Quem recebeu? 💸", reply_markup=ForceReply(True, True))
		elif(state == 1):
			db.update_chat_debtor((update.message.text, update.message.chat_id))
			db.update_chat_state((2, int(update.message.chat_id)))
			bot.send_message(chat_id=update.message.chat_id, text="Qual o valor? 💸", reply_markup=ForceReply(True, True))
		elif(state == 2):
			value = float(update.message.text)
			db.update_balance((chat[0], chat[2], chat[3], value))
			message = "Emprestimo registrado!\nCredor: " + str(chat[2]) + "\nCaloteiro: " + str(chat[3]) + "\nValor: " + str(value)
			bot.send_message(chat_id=update.message.chat_id, text=message)

def main():
	updater = Updater(token='517500543:AAGRhhagJCuwESGJI1Ye2iSQb32POHZsnm4')
	dispatcher = updater.dispatcher
	
	logging.basicConfig(level=logging.DEBUG,
	                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	
	dispatcher.add_handler(CommandHandler('start', start))
	dispatcher.add_handler(CommandHandler('emprestimo', loan))
	dispatcher.add_handler(CommandHandler('pagamento', payment))
	dispatcher.add_handler(MessageHandler(Filters.text, message))
	dispatcher.add_handler(MessageHandler(Filters.command, unknow))

	updater.start_polling()
	updater.idle()

if __name__ == '__main__':
	main()
