try:
	from telegram import ForceReply, ChatAction, ReplyKeyboardMarkup, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
	from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
	from dbhelper import BotDataBase
	import ArgumentException

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
	database = BotDataBase()	
	database.createBalance((chatInfo[CHAT_ID], 
							chatInfo[CREDITOR_ID], 
							chatInfo[DEBTOR_ID], 0))

	balance = database.readBalance((chatInfo[CHAT_ID], 
									chatInfo[CREDITOR_ID], 
									chatInfo[DEBTOR_ID]))

	return balance

def updateBalance(chatInfo, callbackFlag):
	balance = getBalance(chatInfo)
	database = BotDataBase() 

	amount = callbackFlag * chatInfo[CASH_AMT]

	database.createBalance((chatInfo[CHAT_ID], 
							chatInfo[CREDITOR_ID], 
							chatInfo[DEBTOR_ID], 0))
	
	
	#update transactions statistics for creditor
	database.createUser((chatInfo[CREDITOR_ID], 0, 0))
	
	userStats = database.readUser((chatInfo[CREDITOR_ID], ))
	
	database.updateUserCredits((userStats[1] + amount, chatInfo[CREDITOR_ID]))

	#update transactions statistics for debtor
	database.createUser((chatInfo[DEBTOR_ID], 0, 0))
	
	userStats = database.readUser((chatInfo[DEBTOR_ID], ))
	
	database.updateUserDebts((userStats[1] + amount, chatInfo[DEBTOR_ID]))

	#calculates new debt depending on the operation: LOAN = CHATSTATE = 1, PAYMENT = -1
	newDebt = balance[3] + chatInfo[CASH_AMT] * chatInfo[CHAT_STATE]

	if(newDebt < 0):
		return True
	elif(newDebt == 0):
		BotDataBase().deleteBalance((chatInfo[CHAT_ID], chatInfo[CREDITOR_ID], chatInfo[DEBTOR_ID]))
	else:
		BotDataBase().updateBalance((newDebt, chatInfo[CHAT_ID], chatInfo[CREDITOR_ID], chatInfo[DEBTOR_ID]))

	return False

def replyMessageTagging(bot, update, message, replyMarkup):
	bot.send_message(
		chat_id = update.message.chat_id, 
		text = message,
		reply_markup = replyMarkup,
		reply_to_message_id = update.message.message_id, 
		parse_mode = ParseMode.HTML
	)

def sendMessageTagging(bot, update, message, replyMarkup):
	bot.send_message(
		chat_id = update.message.chat_id, 
		text = message,
		reply_markup = replyMarkup,
		parse_mode = ParseMode.HTML
	)

def loanStart(bot, update):
	getChat(int(update.message.chat_id))
	BotDataBase().updateChatState((1, int(update.message.chat_id)))
	
	args = ArgumentException.checa_entrada(str(update.message.text), 1)

	if(args != -1):
		database = BotDataBase() 
		database.updateChatCreditor((args[0], update.message.chat_id))
		database.updateChatDebtor((args[1], update.message.chat_id))
		database.updateChatAmount((args[2], update.message.chat_id))

		registerTransaction(bot, update)

		return EXIT
	else:
		requestCreditor(bot, update)
		return RECEIVER

def paymentStart(bot, update):
	getChat(int(update.message.chat_id))
	BotDataBase().updateChatState((-1, int(update.message.chat_id)))
	requestCreditor(bot, update)

	return RECEIVER

def requestCreditor(bot, update):
	replyMessageTagging(bot, update, "quem deu o dinheiro?", ForceReply(True, True))

def requestDebtor(bot, update):
	BotDataBase().updateChatCreditor((str(update.message.text), update.message.chat_id))
	replyMessageTagging(bot, update, "quem recebeu?", ForceReply(True, True))

	return AMOUNT
 
def requestAmount(bot, update):
	BotDataBase().updateChatDebtor((str(update.message.text), update.message.chat_id))
	replyMessageTagging(bot, update, "qual o valor?", ForceReply(True, True))

	return REGISTER

def setValue(bot, update):
	database = BotDataBase()
	database.updateChatAmount((float(update.message.text), int(update.message.chat_id)))
	registerTransaction(bot, update)


def registerTransaction(bot, update):
	chatInfo = getChat(int(update.message.chat_id)	)
	mutualDebt = database.readBalance((chatInfo[CHAT_ID], chatInfo[DEBTOR_ID], chatInfo[CREDITOR_ID]))

	if(chatInfo[CHAT_STATE] == LOAN and mutualDebt != None):
		message = "⚠<i>DÍVIDAS BILATERAIS</i>\n" + \
				  "Existe o registro do seguinte débto:" + \
				  "\nCredor: " + mutualDebt[1] + \
				  "\nCaloteiro: " + mutualDebt[2] + \
				  "\n<i>Valor</i>: R$" + str(round(mutualDebt[3], 2))

		if(chatInfo[CASH_AMT] < mutualDebt[3]):
			newValue = mutualDebt[3] - chatInfo[CASH_AMT]

			message += "\n\nDeseja alterar o valor do débto acima para:" + \
				  	   "\n<i>Valor</i>: R$" + str(round(newValue, 2) ) + \
				  	   "\n<i>e não registrar o empréstimo atual?</i>"

			keyboard = [[InlineKeyboardButton("Alterar", callback_data='1'), InlineKeyboardButton("Ignorar", callback_data='2')]]
		
		elif(chatInfo[CASH_AMT] > mutualDebt[3]):
			message += "\n\nDeseja modificar o empréstimo atual para:" + \
					   "\nCredor: " + mutualDebt[1] + \
				  	   "\nCaloteiro: " + mutualDebt[2] + \
				  	   "\n<i>Valor</i>: R$" + str(round(newValue, 2) ) + \
				  	   "\n<i>e zerar o débto antigo?</i>"

			keyboard = [[InlineKeyboardButton("Alterar", callback_data='1'), InlineKeyboardButton("Ignorar", callback_data='2')]]

	else:
		if(chatInfo[CHAT_STATE] == LOAN):
			message = "<b>Empréstimo registrado!</b>💰"
		else:
			message = "<b>Pagamento registrado!</b>💰"

		if(updateBalance(chatInfo, 1)):
			message = "Pagamento superior à dívida. Tente novamente. <i>Qual o valor da dívida?</i>"
			replyMessageTagging(bot, update, message, ForceReply(True, True))
			
			return AMOUNT

		balance = getBalance(chatInfo)

		message += "\nCredor: " + chatInfo[CREDITOR_ID] + \
				   "\nCaloteiro: " + chatInfo[DEBTOR_ID] + \
				   "\n<i>Valor</i>: R$" + str(round(chatInfo[CASH_AMT], 2)) + \
				   "\n<i>Total</i>: R$" + str(balance[3]) + \
				   '\n\n"Aceita vale-refeição?"' \
				   "\n<i>- Julius</i>"

		keyboard = [[InlineKeyboardButton("Cancelar", callback_data='1')]]

	sendMessageTagging(bot, update, message, InlineKeyboardMarkup(keyboard))


def cancel(bot, update):
	callerUsername = "@" + str(update.callback_query.from_user.username)
	
	chatInfo = getChat(int(update.callback_query.message.chat_id))
	
	chatInfo = (chatInfo[CHAT_ID], 
				chatInfo[CHAT_STATE] * -1, 
				chatInfo[CREDITOR_ID], 
				chatInfo[DEBTOR_ID], 
				chatInfo[CASH_AMT])
	
	if(chatInfo[CREDITOR_ID] == callerUsername):
		updateBalance(chatInfo, -1)
		message = "Operação cancelada."
	
	else:
		message = callerUsername + ", você não é o credor desta transação ou o tempo de cancelamento expirou."

	replyMessageTagging(bot, update.callback_query, message, ForceReply(False, True))

def stats(bot, update):
	
	database = BotDataBase()
	username = "@" + str(update.message.from_user.username)
	userStats = database.readUser((username, ))

	if(userStats == None):
		message = "Você ainda não possui estatísticas."
	else:
		message = username + ":" + \
				  "\n\nemprestou:\n✅ R$" + str(format(userStats[1], ".2f")) + \
				  "\n\npegou emprestado:\n🅾 R$" + str(format(userStats[2], ".2f"))

	sendMessageTagging(bot, update, message, ForceReply(False, False))

def balanceOverview(bot, update):
	chatBalance = BotDataBase().overview((int(update.message.chat_id), ))

	nDebtor = 1
	debtor = ""
	
	message = "<i>BALANÇO FINANCEIRO</i>\n"

	for transaction in chatBalance:
		if(transaction[2] != debtor):
			debtor = transaction[2]
			message += "\n" + str(nDebtor) + ". " + debtor + " deve:\n"
			nDebtor += 1

		message += "para " + transaction[1] + " R$" + str(round(transaction[3],2)) + "\n"

	sendMessageTagging(bot, update, message, ForceReply(False, True))
