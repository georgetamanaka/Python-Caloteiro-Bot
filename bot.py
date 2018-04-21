from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ForceReply

def unknow(bot, update):
	#bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
	bot.send_message(chat_id=update.message.chat_id, text="Please, choose a valid command", reply_to_message_id=update.message.message_id, reply_markup=ForceReply(True, True))

def start(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me")

def echo(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text=update.message.text)

#def main():
updater = Updater(token='517500543:AAGRhhagJCuwESGJI1Ye2iSQb32POHZsnm4')
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(MessageHandler(Filters.text, echo))
dispatcher.add_handler(MessageHandler(Filters.command, unknow))

updater.start_polling()
