from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters)

def start(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me")

def echo(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text=update.message.text)

#def main():
updater = Updater(token='517500543:AAGRhhagJCuwESGJI1Ye2iSQb32POHZsnm4')
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(MessageHandler(Filters.text, echo))
updater.start_polling()
