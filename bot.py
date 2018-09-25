try:
    from telegram import ForceReply, ChatAction, ReplyKeyboardMarkup, ParseMode, InlineKeyboardButton, \
        InlineKeyboardMarkup
    from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
    import firebase_admin
    from firebase_admin import credentials
    from firebase_admin import firestore
except KeyboardInterrupt:
    print("\n\nStopping...")
    raise SystemExit

except:
    print("[!] Requirements are not installed.")
    raise SystemExit

EXIT, RECEIVER, AMOUNT, REGISTER = range(-1, 3)


import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate("caloteirobot-firebase-adminsdk-pi4uq-52a2cefe95.json")
firebase_admin.initialize_app(cred)

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text="Olá, eu sou o caloteiroBot")

def replyMessageTagging(bot, update, message, replyMarkup):
    bot.send_message(
        chat_id=update.message.chat_id,
        text=message,
        reply_markup=replyMarkup,
        reply_to_message_id=update.message.message_id,
        parse_mode=ParseMode.HTML
    )

def sendMessageTagging(bot, update, message, replyMarkup):
    bot.send_message(
        chat_id=update.message.chat_id,
        text=message,
        reply_markup=replyMarkup,
        parse_mode=ParseMode.HTML
    )

def loanStart(bot, update):
    db = firestore.client()
    doc_ref = db.collection("chats").document(str(update.message.chat_id))
    doc_ref.set({
        'id': int(update.message.chat_id),
        'state': 1,
        'currentCreditor': None,
        'currentDebtor': None,
        'currentAmount': None
    })

    replyMessageTagging(bot, update, "quem deu o dinheiro?", ForceReply(True, True))

    return RECEIVER

def paymentStart(bot, update):
    db = firestore.client()
    doc_ref = db.collection("chats").document(str(update.message.chat_id))
    doc_ref.update({
        'id': int(update.message.chat_id),
        'state': 2,
        'currentCreditor': None,
        'currentDebtor': None,
        'currentAmount': None
    })

    replyMessageTagging(bot, update, "quem deu o dinheiro?", ForceReply(True, True))

    return RECEIVER

def receiveCreditor(bot, update):
    db = firestore.client()
    doc_ref = db.collection("chats").document(str(update.message.chat_id))
    doc_ref.update({
        'currentCreditor': str(update.message.text)
    })

    replyMessageTagging(bot, update, "quem recebeu?", ForceReply(True, True))

    return AMOUNT

def receiveDebtor(bot, update):
    db = firestore.client()
    doc_ref = db.collection("chats").document(str(update.message.chat_id))
    doc_ref.update({
        'currentDebtor': str(update.message.text)
    })

    replyMessageTagging(bot, update, "qual o valor?", ForceReply(True, True))

    return REGISTER

def registerTransaction(bot, update):
    db = firestore.client()
    doc_ref = db.collection("chats").document(str(update.message.chat_id))
    currentDebtInfo = doc_ref.get().to_dict()
    currentCreditor = currentDebtInfo['currentCreditor']
    currentDebtor = currentDebtInfo['currentDebtor']
    currentState = currentDebtInfo['state']

    try:
        currentAmount = float(str(update.message.text).replace(",", "."))

        if(currentAmount <= 0):
            message = "Valor inválido. Tente novamente. <i>Qual o valor da dívida?</i>"
            replyMessageTagging(bot, update, message, ForceReply(True, True))

            return REGISTER
    except:
        message = "Valor inválido. Tente novamente. <i>Qual o valor da dívida?</i>"
        replyMessageTagging(bot, update, message, ForceReply(True, True))

        return REGISTER

    users_collec_ref = db.collection("chats").document(str(update.message.chat_id)).collection("users")
    creditor_doc_ref = users_collec_ref.document(currentCreditor)
    debtor_doc_ref = users_collec_ref.document(currentDebtor)

    try:
        creditorInfo = creditor_doc_ref.get().to_dict()
        debtorInfo = debtor_doc_ref.get().to_dict()

        creditor_doc_ref.set({
            'historicBorrow': creditorInfo['historicBorrow'],
            'historicLend': creditorInfo['historicLend'] + currentAmount,
            'borrowCount': creditorInfo['borrowCount'],
            'lendCount': creditorInfo['lendCount'] + 1
        })

        debtor_doc_ref.set({
            'historicLend': debtorInfo['historicLend'],
            'historicBorrow': debtorInfo['historicBorrow'] + currentAmount,
            'borrowCount': debtorInfo['borrowCount'] + 1,
            'lendCount': debtorInfo['lendCount']
        })

    except:
        creditor_doc_ref.set({
            'historicBorrow': 0,
            'historicLend': currentAmount,
            'borrowCount': 0,
            'lendCount': 1
        })

        debtor_doc_ref.set({
            'historicLend': 0,
            'historicBorrow': currentAmount,
            'borrowCount': 1,
            'lendCount': 0
        })


    doc_ref.update({
        'currentAmount': currentAmount
    })

    documentName = currentCreditor + "->" + currentDebtor
    debts_ref = db.collection("chats").document(str(update.message.chat_id)).collection("debts").document(documentName)

    if (currentState == 1):
        message = "<b>Empréstimo registrado!</b>💰"

    else:
        message = "<b>Pagamento registrado!</b>💰"
        currentAmount *= -1

    try:
        achiveDebtInfo = debts_ref.get().to_dict()
        newDebtAmount = currentAmount + achiveDebtInfo["amount"]

        if(newDebtAmount < 0):
            message = "Pagamento superior à dívida. Tente novamente. <i>Qual o valor da dívida?</i>"
            replyMessageTagging(bot, update, message, ForceReply(True, True))

            return REGISTER
    except:
        newDebtAmount = currentAmount


    debts_ref.set({
        'creditor': currentCreditor,
        'debtor': currentDebtor,
        'amount': newDebtAmount
    })


    message += "\nCredor: " + currentCreditor + \
               "\nCaloteiro: " + currentDebtor + \
               "\n<i>Valor</i>: R$" + str(abs(round(currentAmount, 2))) + \
               "\n<i>Total</i>: R$" + str(round(newDebtAmount, 2))

    keyboard = [[InlineKeyboardButton("Cancelar", callback_data='1')]]

    sendMessageTagging(bot, update, message, InlineKeyboardMarkup(keyboard))

def cancel(bot, update):
    query = update.callback_query
    option = int(query.data)

    if (option == 1):
        callerUsername = "@" + str(query.from_user.username)

        db = firestore.client()
        doc_ref = db.collection("chats").document(str(query.message.chat_id))
        currentDebtInfo = doc_ref.get().to_dict()

        currentCreditor = currentDebtInfo['currentCreditor']
        currentDebtor = currentDebtInfo['currentDebtor']
        currentAmount = currentDebtInfo['currentAmount']
        currentState = currentDebtInfo['state']

        if(currentCreditor == callerUsername):
            message = "Operação cancelada."

            documentName = currentCreditor + "->" + currentDebtor
            debts_ref = db.collection("chats").document(str(query.message.chat_id)).collection("debts").document(documentName)
            achiveDebtInfo = debts_ref.get().to_dict()

            newDebtAmount = 0

            if(currentState == 1):
                newDebtAmount = achiveDebtInfo["amount"] - currentAmount
            else:
                newDebtAmount = achiveDebtInfo["amount"] + currentAmount

            debts_ref.update({
                'amount': newDebtAmount
            })

            doc_ref.update({
                'currentCreditor': None,
                'currentDebtor': None,
                'currentAmount': None
            })

        else:
            message = callerUsername + ", você não é o credor desta transação, já cancelou ou tempo de cancelamento expirou."

        replyMessageTagging(bot, update.callback_query, message, ForceReply(False, True))

def balanceOverview(bot, update):
    db = firestore.client()
    users_docs = db.collection("chats").document(str(update.message.chat_id)).collection("users").get()
    debts_ref = db.collection("chats").document(str(update.message.chat_id)).collection("debts")

    message = "<i>BALANÇO FINANCEIRO</i>\n"
    nDebtor = 1

    for doc in users_docs:
        current_docs = debts_ref.where('debtor', '==', str(doc.id)).get()
        current_docs_size = 0

        for cdoc in current_docs:
            if(current_docs_size == 0):
                message += "\n" + str(nDebtor) + ". " + str(doc.id) + " deve:\n"
                nDebtor += 1

            debtInfo = cdoc.to_dict()
            message += "para " + debtInfo['creditor'] + " R$" + str(round(debtInfo['amount'], 2)) + "\n"

            current_docs_size += 1


    sendMessageTagging(bot, update, message, ForceReply(False, True))


def myStats(bot, update):
    if (update.message.chat.username != None):
        username = "@" + str(update.message.chat.username)
    else:
        username = "@" + str(update.message.from_user.username)

    db = firestore.client()
    users_docs = db.collection("chats").document(str(update.message.chat_id)).collection("users").document(username).get().to_dict()

    if(users_docs["lendCount"] != 0):
        averageLend = round(users_docs["historicLend"]/users_docs["lendCount"], 2)
    else:
        averageLend = 0

    if (users_docs["borrowCount"] != 0):
        averageBorrow = round(users_docs["historicBorrow"] / users_docs["borrowCount"], 2)
    else:
        averageBorrow = 0

    message = "<i>ESTATÍSTICAS PARA</i>\n" + username + ":\n" + \
        "\n<b>Já emprestou</b>: R$" + str(users_docs["historicLend"]) + \
        "\n<b>Já pegou</b>: R$" + str(users_docs["historicBorrow"]) + \
        "\n\n<b>Empresta</b>: R$" + str(averageLend) + "<i>*</i>"\
        "\n<b>Pega</b>: R$" + str(averageBorrow) + "<i>*</i>" + \
        "\n\n<i>* Valores médios</i>"

    sendMessageTagging(bot, update, message, ForceReply(False, True))

def myCredits(bot, update):
    if(update.message.chat.username != None):
        username = "@" + str(update.message.chat.username)
    else:
        username = "@" + str(update.message.from_user.username)

    message = "São estes que te devem, " + username + ":\n\n"

    db = firestore.client()
    credits = db.collection("chats").document(str(update.message.chat_id)).collection("debts").where('creditor', '==', username).get()
    totalCredits = 0
    count = 1

    for doc in credits:
        credit = doc.to_dict()

        message += str(count) + ". " + credit["debtor"] + ": R$" + str(credit["amount"]) + "\n"

        totalCredits += credit["amount"]

        count += 1

    message += "\nTotal: R$" + str(totalCredits)

    if (count == 1):
        sendMessageTagging(bot, update, "<i>Você não possui créditos.</i>", ForceReply(False, True))
    else:
        sendMessageTagging(bot, update, message, ForceReply(False, True))


def myDebts(bot, update):
    if (update.message.chat.username != None):
        username = "@" + str(update.message.chat.username)
    else:
        username = "@" + str(update.message.from_user.username)

    message = "Aos quais você deve, " + username + ":\n\n"

    db = firestore.client()
    debts = db.collection("chats").document(str(update.message.chat_id)).collection("debts").where('debtor', '==',
                                                                                                     username).get()
    totalDebts = 0
    count = 1

    for doc in debts:
        credit = doc.to_dict()

        message += str(count) + ". " + debts["creditor"] + ": R$" + str(credit["amount"]) + "\n"

        totalDebts += credit["amount"]

        count += 1

    message += "\nTotal: R$" + str(totalDebts)

    if(count == 1):
        sendMessageTagging(bot, update, "<i>Você não possui débitos.</i>", ForceReply(False, True))
    else:
        sendMessageTagging(bot, update, message, ForceReply(False, True))