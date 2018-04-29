import logging
import time

from telegram import ForceReply, ChatAction, ReplyKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import bot


def main():
	updater = Updater(token='517500543:AAGRhhagJCuwESGJI1Ye2iSQb32POHZsnm4')
	dispatcher = updater.dispatcher
	
	logging.basicConfig(level=logging.DEBUG,
	                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	
	dispatcher.add_handler(CommandHandler('start', bot.start))
	dispatcher.add_handler(CommandHandler('emprestimo', bot.loan))
	dispatcher.add_handler(CommandHandler('pagamento', bot.payment))
	dispatcher.add_handler(CommandHandler('overview', bot.balance_overview))
	dispatcher.add_handler(MessageHandler(Filters.text, bot.control))
	dispatcher.add_handler(MessageHandler(Filters.command, bot.unknow))

	updater.start_polling()
	updater.idle()

if __name__ == '__main__':
	main()