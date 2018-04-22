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
	bot.send_message(chat_id=update.message.chat_id, text="Quem emprestou o dinheiro? 💸", reply_markup=ForceReply(True, True))

def print_info(bot, update):
#	text = update.message.text
#	items = db.get_items()
#	db.add_item(text)
#	items = db.get_items()
	db = DBHelper()
	db.setup()
	db.add_item()
	db.get_all()

	print ("upadate_id: " + str(update.update_id))	
	print ("chat_id: " + str(update.message.chat_id))
	print ("username: " + str(update.message.chat.username))
	print ("first_name: " + str(update.message.chat.first_name))
	print ("last_name: " + str(update.message.chat.last_name))

	#db.get_all()

	bot.send_message(chat_id=update.message.chat_id, text=update.message.text)

def main():
	updater = Updater(token='517500543:AAGRhhagJCuwESGJI1Ye2iSQb32POHZsnm4')
	dispatcher = updater.dispatcher
	logging.basicConfig(level=logging.DEBUG,
	                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	dispatcher.add_handler(CommandHandler('start', start))
	dispatcher.add_handler(CommandHandler('emprestimo', loan))
	dispatcher.add_handler(MessageHandler(Filters.text, print_info))
	dispatcher.add_handler(MessageHandler(Filters.command, unknow))

	updater.start_polling()
	updater.idle()

if __name__ == '__main__':
	main()
