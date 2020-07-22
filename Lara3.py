from telegram.ext import MessageHandler, Filters
from telegram.ext import CommandHandler
import logging
from telegram.ext import Updater
import telegram
bot = telegram.Bot(token='1190164594:AAG3HWiPHY-6xmJvoPqt58vYKrvogZUnUjQ')
updater = Updater(
    token='1190164594:AAG3HWiPHY-6xmJvoPqt58vYKrvogZUnUjQ', use_context=True)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def start(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="Hey, how are you?")


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)


def echo(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="Lara is cute<3")


echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)

updater.start_polling()
