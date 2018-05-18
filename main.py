import logging
import time

from telegram import ForceReply, ChatAction, ReplyKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler, Filters
from dbhelper import BotDataBase
import bot

EXIT, RECEIVER, AMOUNT, REGISTER = range(-1, 3)

def main():
	updater = Updater(token='510827284:AAGMbXJrrZG-hZyzdvf7Tnrbx-XxGcT22-c')
	dispatcher = updater.dispatcher
	
	logging.basicConfig(level=logging.DEBUG,
	                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	
	updater.dispatcher.add_handler(CallbackQueryHandler(bot.cancel))

	dispatcher.add_handler(
		ConversationHandler(
			entry_points=[CommandHandler('emprestimo', bot.loanStart), 
			              CommandHandler('pagamento', bot.paymentStart)],

		    states={
		        RECEIVER: [MessageHandler([Filters.text], bot.requestDebtor)],

		        AMOUNT: [MessageHandler([Filters.text], bot.requestAmount)],

		        REGISTER: [MessageHandler([Filters.text], bot.registerTransaction)]
		    },

		    fallbacks=[CommandHandler('exit', exit)],
		    allow_reentry = True
	    )
	)

	dispatcher.add_handler(CommandHandler('overview', bot.balanceOverview))
	dispatcher.add_handler(CommandHandler('stats', bot.stats))

	updater.start_polling()
	updater.idle()

if __name__ == '__main__':
	db = BotDataBase()
	db.setup()
	main()