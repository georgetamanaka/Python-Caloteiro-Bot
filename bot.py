try:
	from telegram import ForceReply, ChatAction, ReplyKeyboardMarkup, ParseMode
	from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
	from dbhelper import BotDataBase

except KeyboardInterrupt:
	print ("\n\nStopping...")
	raise SystemExit

except:
	print("[!] Requirements are not installed... Please run the 'setup.py' script first.")
	raise SystemExit

CHAT_ID, CHAT_STATE, CREDITOR_ID, DEBTOR_ID, VALUE_AMT = range(5)
EXIT, RECEIVER, AMOUNT, REGISTER = range(-1, 3)
PAYMENT = -1
LOAN = 1

def start(bot, update):
	bot.send_message(chat_id=update.message.chat_id, 
					text="Olá, eu sou o caloteiroBot")

def getChat(chatId):
	data = BotDataBase()

	data.createChat((chatId, -1))

	return data.readChat((chatId, ))

def getBalance(chatInfo):
	BotDataBase().createBalance((chatInfo[CHAT_ID], chatInfo[CREDITOR_ID], chatInfo[DEBTOR_ID], 0))
	balance = BotDataBase().readBalance((chatInfo[CHAT_ID], chatInfo[CREDITOR_ID], chatInfo[DEBTOR_ID]))

	return balance

def updateBalance(update, chatInfo):
	BotDataBase().createBalance((chatInfo[CHAT_ID], chatInfo[CREDITOR_ID], chatInfo[DEBTOR_ID], 0))
	BotDataBase().updateBalance((float(update.message.text) * chatInfo[CHAT_STATE], chatInfo[CHAT_ID], chatInfo[CREDITOR_ID], chatInfo[DEBTOR_ID]))

def sendMessageTagging(bot, update, message, force):
	bot.send_message(
		chat_id = update.message.chat_id, 
		text = message,
		reply_markup = ForceReply(force, True),
		reply_to_message_id = update.message.message_id, 
		parse_mode = ParseMode.HTML
	)

def loanStart(bot, update):
	getChat(int(update.message.chat_id))

	BotDataBase().updateChatState((1, int(update.message.chat_id)))
	
	requestCreditor(bot, update)

	return RECEIVER

def paymentStart(bot, update):
	getChat(int(update.message.chat_id))

	BotDataBase().updateChatState((-1, int(update.message.chat_id)))

	requestCreditor(bot, update)

	return RECEIVER

def requestCreditor(bot, update):
	sendMessageTagging(bot, update, "quem deu o dinheiro?", True)

	#debug begin
	chat = getChat(int(update.message.chat_id))
	print("------------ DEBUG 1 ------------")
	print(chat[CHAT_ID])
	print(chat[CREDITOR_ID])
	print(chat[DEBTOR_ID])
	#end debug

def requestDebtor(bot, update):
	BotDataBase().updateChatCreditor((str(update.message.text), update.message.chat_id))
	
	#debug begin
	chat = getChat(int(update.message.chat_id))
	print("------------ DEBUG 2 ------------")
	print(chat[CHAT_ID])
	print(chat[CREDITOR_ID])
	print(chat[DEBTOR_ID])
	#end debug


	sendMessageTagging(bot, update, "quem recebeu?", True)

	return AMOUNT
 
def requestAmount(bot, update):
	BotDataBase().updateChatDebtor((str(update.message.text), update.message.chat_id))
	
	#debug begin
	chat = getChat(int(update.message.chat_id))
	print("------------ DEBUG 3 ------------")
	print(chat[CHAT_ID])
	print(chat[CREDITOR_ID])
	print(chat[DEBTOR_ID])
	#end debug

	sendMessageTagging(bot, update, "qual o valor?", True)

	return REGISTER

def registerTransaction(bot, update):
	chatInfo = getChat(int(update.message.chat_id)	)

	if(chatInfo[1] == LOAN):
		message = "<b>Empréstimo registrado!</b>💰"
	else:
		message = "<b>Pagamento registrado!</b>💰"

	updateBalance(update, chatInfo)

	message += "\nCredor: " + chatInfo[CREDITOR_ID] + \
			   "\nCaloteiro: " + chatInfo[DEBTOR_ID] + \
			   "\n<i>Valor: R$" + str(update.message.text) + \
			   '\n\n</i>"Aceita vale-refeição?"' \
			   "\n<i>- Julius</i>"

	BotDataBase().getAll()

	sendMessageTagging(bot, update, message, False)

def balanceOverview(bot, update):	
	db = BotDataBase()
	chatBalance = db.overview((int(update.message.chat_id), ))

	nDebtor = 1
	debtor = ""
	
	message = "<b>Balanço de dívidas</b>💰\n"

	for transaction in chatBalance:
		if(transaction[2] != debtor):
			debtor = transaction[2]
			message += "\n" + str(nDebtor) + ". " + debtor + " deve:\n"
			nDebtor += 1

		message += "para " + transaction[1] + " R$" + str(transaction[3]) + "\n"

	sendMessageTagging(bot, update, message, False)
