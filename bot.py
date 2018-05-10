try:
	from telegram import ForceReply, ChatAction, ReplyKeyboardMarkup, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
	from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
	from dbhelper import BotDataBase

except KeyboardInterrupt:
	print ("\n\nStopping...")
	raise SystemExit

except:
	print("[!] Requirements are not installed... Please run the 'setup.py' script first.")
	raise SystemExit

CHAT_ID, CHAT_STATE, CREDITOR_ID, DEBTOR_ID, CASH_AMT = range(5)
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

def updateBalance(chatInfo):
	balance = getBalance(chatInfo)
	BotDataBase().createBalance((chatInfo[CHAT_ID], chatInfo[CREDITOR_ID], chatInfo[DEBTOR_ID], 0))
	
	newDebt = balance[3] + chatInfo[CASH_AMT] * chatInfo[CHAT_STATE]

	if(newDebt < 0):
		return True
	elif(newDebt == 0):
		BotDataBase().deleteBalance((chatInfo[CHAT_ID], chatInfo[CREDITOR_ID], chatInfo[DEBTOR_ID]))
	else:
		BotDataBase().updateBalance((newDebt, chatInfo[CHAT_ID], chatInfo[CREDITOR_ID], chatInfo[DEBTOR_ID]))

	return False

def sendMessageTagging(bot, update, message, replyMarkup):
	bot.send_message(
		chat_id = update.message.chat_id, 
		text = message,
		reply_markup = replyMarkup,
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
	sendMessageTagging(bot, update, "quem deu o dinheiro?", ForceReply(True, True))

def requestDebtor(bot, update):
	BotDataBase().updateChatCreditor((str(update.message.text), update.message.chat_id))
	sendMessageTagging(bot, update, "quem recebeu?", ForceReply(True, True))

	return AMOUNT
 
def requestAmount(bot, update):
	BotDataBase().updateChatDebtor((str(update.message.text), update.message.chat_id))
	sendMessageTagging(bot, update, "qual o valor?", ForceReply(True, True))

	return REGISTER

def registerTransaction(bot, update):
	BotDataBase().updateChatAmount((float(update.message.text), int(update.message.chat_id)))
	chatInfo = getChat(int(update.message.chat_id)	)

	if(chatInfo[1] == LOAN):
		message = "<b>Empréstimo registrado!</b>💰"
	else:
		message = "<b>Pagamento registrado!</b>💰"

	if(updateBalance(chatInfo)):
		message = "Pagamento superior à dívida. Tente novamente. <i>Qual o valor da dívida?</i>"
		sendMessageTagging(bot, update, message, ForceReply(True, True))
		
		return AMOUNT

	balance = getBalance(chatInfo)

	message += "\nCredor: " + chatInfo[CREDITOR_ID] + \
			   "\nCaloteiro: " + chatInfo[DEBTOR_ID] + \
			   "\n<i>Valor</i>: R$" + str(update.message.text) + \
			   "\n<i>Total</i>: R$" + str(balance[3]) + \
			   '\n\n"Aceita vale-refeição?"' \
			   "\n<i>- Julius</i>"

	keyboard = [[InlineKeyboardButton("Cancelar", callback_data='1')]]

	sendMessageTagging(bot, update, message, InlineKeyboardMarkup(keyboard))


def cancel(bot, update):
	chatInfo = getChat(int(update.callback_query.message.chat_id))
	chatInfo = (chatInfo[0], chatInfo[1] * -1, chatInfo[2], chatInfo[3], chatInfo[4])
	updateBalance(chatInfo)

	sendMessageTagging(bot, update.callback_query, "Operação cancelada.", ForceReply(False, True))

def balanceOverview(bot, update):
	chatBalance = BotDataBase().overview((int(update.message.chat_id), ))

	nDebtor = 1
	debtor = ""
	
	message = "<b>Balanço de dívidas</b>💰\n"

	for transaction in chatBalance:
		if(transaction[2] != debtor):
			debtor = transaction[2]
			message += "\n" + str(nDebtor) + ". " + debtor + " deve:\n"
			nDebtor += 1

		message += "para " + transaction[1] + " R$" + str(transaction[3]) + "\n"

	sendMessageTagging(bot, update, message, ForceReply(False, True))
