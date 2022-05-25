import time
from handlers import helper, i_history, calendar
from loader import bot
from models import Users


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.from_user.id,
                     'Здравствуйте! Прекрасный день чтобы найти идеальный отель для Вашего ТУРбо отдыха!')
    time.sleep(0.5)
    helper(message)


@bot.message_handler(commands=['lowprice'])
def low_price(message):
    user = Users.get_user(message.chat.id)
    user.command = message.text
    calendar(message.chat.id, message)



@bot.message_handler(commands=['highprice'])
def high_price(message):
    user = Users.get_user(message.chat.id)
    user.command = message.text
    calendar(message.chat.id, message)


@bot.message_handler(commands=['bestdeal'])
def best_deal(message):
    user = Users.get_user(message.chat.id)
    user.command = message.text
    calendar(message.chat.id, message)


@bot.message_handler(commands=['history'])
def history(message):
    i_history(message)


@bot.message_handler(commands=['help'])
def send_help(message):
    helper(message)


bot.polling(none_stop=True)