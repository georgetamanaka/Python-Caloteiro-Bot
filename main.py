import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler, Filters
import bot

EXIT, RECEIVER, AMOUNT, REGISTER = range(-1, 3)


def main():
    updater = Updater(token='510827284:AAGMbXJrrZG-hZyzdvf7Tnrbx-XxGcT22-c')
    dispatcher = updater.dispatcher

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    updater.dispatcher.add_handler(CallbackQueryHandler(bot.cancel))
    dispatcher.add_handler(CommandHandler('balanco', bot.balanceOverview))
    dispatcher.add_handler(CommandHandler('estatisticas', bot.myStats))
    dispatcher.add_handler(CommandHandler('medevem', bot.myCredits))
    dispatcher.add_handler(CommandHandler('devopara', bot.myDebts))


    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler('emprestimo', bot.loanStart),
                          CommandHandler('pagamento', bot.paymentStart)],

            states={
                RECEIVER: [MessageHandler([Filters.text], bot.receiveCreditor)],

                AMOUNT: [MessageHandler([Filters.text], bot.receiveDebtor)],

                REGISTER: [MessageHandler([Filters.text], bot.registerTransaction)]
            },

            fallbacks=[CommandHandler('exit', exit)],
            allow_reentry=True
        )
    )

    updater.start_polling()
    updater.idle()
    #dispatcher.add_handler(CommandHandler('stats', bot.stats))


if __name__ == '__main__':
    main()