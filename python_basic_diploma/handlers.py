from loader import bot, calendar_1_callback, my_calendar
from rapidapi import result, photos, get_city_id
import telebot
from models import User, Users, db
import re
from telebot import types
from telebot.types import CallbackQuery, ReplyKeyboardRemove
import datetime


@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_1_callback.prefix))
def callback_inline(call: CallbackQuery):
    user = Users.get_user(call.from_user.id)
    name, action, year, month, day = call.data.split(calendar_1_callback.sep)
    date = my_calendar.calendar_query_handler(
        bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
    )
    if action == "DAY":
        if user.i == 0:
            user.start_of_trip = date
            text = 'Дата заселения: {}'.format(date.strftime('%d.%m.%Y'))
        elif user.i == 1:
            user.end_of_trip = date
            text = 'Дата выселения: {}'.format(date.strftime('%d.%m.%Y'))
        bot.send_message(
            chat_id=call.from_user.id,
            text=text,
            reply_markup=ReplyKeyboardRemove(),
        )
        user.i += 1
        calendar(call.from_user.id)
    elif action == "CANCEL":
        bot.send_message(
            chat_id=call.from_user.id,
            text="Этап выбора дат отменен.",
            reply_markup=ReplyKeyboardRemove(),
        )
        user.i = 2
        calendar(call.from_user.id)


def calendar(message_chat_id, *args):
    user = Users.get_user(message_chat_id)
    now = datetime.datetime.now()
    if not user.i:
        user.i = 0
        if not user.message:
            user.message = args[0]
        bot.send_message(
            message_chat_id,
            "Выберете дату заселения:"
            "\n(Нажмите кнопку \'Cancel\', чтобы пропустить этап выбора дат.)",
            reply_markup=my_calendar.create_calendar(
                name=calendar_1_callback.prefix,
                year=now.year,
                month=now.month
            )
        )
    elif user.i == 1:
        calendar_2(message_chat_id)
    elif user.i == 2:
        if user.end_of_trip:
            delta = user.end_of_trip - user.start_of_trip
            user.days_sum = int(delta.days)
        choose_city(user.command, user.message)


def calendar_2(message_chat_id):
    now = datetime.datetime.now()
    bot.send_message(
        message_chat_id,
        "Выберете дату выселения:"
        "\n(Нажмите кнопку \'Cancel\', чтобы отменить этап выбора дат.)",
        reply_markup=my_calendar.create_calendar(
            name=calendar_1_callback.prefix,
            year=now.year,
            month=now.month
        )
    )


def input_validation(message, step):
    if step == 1 or step == 3:
        if message.text.isdigit():
            return message.text
        else:
            if step == 1:
                bot.send_message(message.chat.id, 'Ошибка ввода! Пожалуйста, введите еще раз количество отелей, '
                                                  'которые необходимо вывести в результате\n'
                                                  '(не больше 8).')
                bot.register_next_step_handler(message, photos_quest)
            else:
                bot.send_message(message.chat.id, 'Ошибка ввода! Пожалуйста, введите еще раз количество фотографий, '
                                                  'для каждого отеля\n'
                                                  '(не больше 8).')
                bot.register_next_step_handler(message, general_process)
    elif step == 2:
        if message.text.lower() == 'да' or message.text.lower() == 'нет':
            return message.text
        else:
            bot.send_message(message.chat.id, 'Ошибка ввода! Пожалуйста, введите еще раз:\n'
                                              'хотите ли вы загрузить и вывести '
                                              'фотографии для каждого отеля\n(“Да/Нет”)?')
            bot.register_next_step_handler(message, photos_count)
    elif step == 4:
        search = re.findall(r'\b\d+\b[-]\b\d+\b', message.text)
        min_and_max_price = re.findall(r'\d+', message.text)
        if len(search) > 0 and message.text == search[0] and min_and_max_price[0] <= min_and_max_price[1]:
            return message.text
        else:
            bot.send_message(message.chat.id, 'Ошибка ввода! Пожалуйста, введите еще раз '
                                              'диапазон стоимости отеля за ночь в рублях, '
                                              'который вас интересует, через тире без пробелов.\n'
                                              '(От-До)\n'
                                              '(Например: 0-5000)')
            bot.register_next_step_handler(message, center_distance_range)
    elif step == 5:
        search = re.findall(r'\b\d+\b[,.]\b\d+\b', message.text)
        if len(search) > 0 and message.text == search[0] or message.text.isdigit():
            if ',' in message.text:
                return message.text.replace(',', '.')
            else:
                return message.text
        else:
            bot.send_message(message.chat.id, 'Ошибка ввода! Пожалуйста, введите еще раз '
                                              'максимально допустимую удалённость '
                                              'отеля от центра города, в километрах\n(Например: 10 или 0.8)')
            bot.register_next_step_handler(message, hotels_count)


def key_continue(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('Продолжить')
    bot.send_message(message.chat.id, 'Нажмите кнопку \"Продолжить\"\
                                       для дальнейшей работы с ботом.',
                     reply_markup=keyboard)
    bot.register_next_step_handler(message, helper)


def choose_city(command, message):
    if command == "/lowprice":
        end, i = 'дешевые отели', 0
    elif command == "/highprice":
        end, i = 'дорогие отели', 0
    else:
        end, i = 'оптимальные предложения', 1

    bot.send_message(message.chat.id,  'Пожалуйста, введите город, '
                                       'в котором нужно поискать самые {}:\n(К сожалению города России не доступны '
                                       'для поиска. Приносим свои извинения.)'.format(end))
    if i == 0:
        bot.register_next_step_handler(message, hotels_count)
    else:
        bot.register_next_step_handler(message, price_range)


def hotels_count(message):
    user = Users.get_user(message.chat.id)
    if user.city is None:
        user.city = message.text
        bot.send_message(message.chat.id, 'Пожалуйста, введите количество отелей, '
                                          'которые необходимо вывести в результате\n'
                                          '(не больше 8).')
        bot.register_next_step_handler(message, photos_quest)
    else:
        user.distance_from_center_max = input_validation(message, 5)
        if user.distance_from_center_max:
            bot.send_message(message.chat.id, 'Пожалуйста, введите количество отелей, '
                                              'которые необходимо вывести в результате\n'
                                              '(не больше 8).')
            bot.register_next_step_handler(message, photos_quest)



def photos_quest(message):
    user = Users.get_user(message.chat.id)
    user.hotels_count = input_validation(message, 1)
    if user.hotels_count:
        bot.send_message(message.chat.id, 'Хотите ли вы загрузить и вывести '
                                          'фотографии для каждого отеля\n(“Да/Нет”)?')
        bot.register_next_step_handler(message, photos_count)


def photos_count(message):
    user = Users.get_user(message.chat.id)
    user.load_image = input_validation(message, 2)
    if user.load_image:
        if message.text.lower() == 'да':
            bot.send_message(message.chat.id, 'Пожалуйста, введите количество фотографий для каждого отеля\n'
                                              '(не больше 5).')
            bot.register_next_step_handler(message, general_process)
        else:
            general_process(message)


def price_range(message):
    user = Users.get_user(message.chat.id)
    user.city = message.text
    bot.send_message(message.chat.id, 'Пожалуйста, введите диапазон стоимости отеля за ночь в рублях, '
                                      'который вас интересует, через тире без пробелов.\n'
                                      '(От-До)\n'
                                      '(Например: 0-5000)')
    bot.register_next_step_handler(message, center_distance_range)


def center_distance_range(message):
    user = Users.get_user(message.chat.id)
    range_price = input_validation(message, 4)
    if range_price:
        user.price_min = re.findall(r'\d+', message.text)[0]
        user.price_max = re.findall(r'\d+', message.text)[1]
        bot.send_message(message.chat.id, 'Пожалуйста, введите максимально допустимую удалённость '
                                          'отеля от центра города, в километрах\n(Например: 10 или 0.8)')
        bot.register_next_step_handler(message, hotels_count)


def city_definition(user, message):
    id_city = get_city_id(user.city)
    if id_city:
        return id_city
    else:
        cleaner(message)
        bot.send_message(message.chat.id, 'Извините, возникла ошибка при определении города. '
                                          '(Города из России в данный момент, к сожалению, недоступны)')
        key_continue(message)


def check_results(user, id_city, message):
    i_result = result(user, id_city)
    if i_result != '404' and i_result:
        return i_result
    else:
        if i_result == '404':
            bot.send_message(message.chat.id, 'Извините, но отелей, в этом ценовом диапазоне\
                                               и с указанной '
                                              'удаленностью от центра, не обнаружено.')
        else:
            bot.send_message(message.chat.id, 'Извините, возникла ошибка при загрузке результатов.')
        cleaner(message)
        key_continue(message)


def check_distance(distance, user, message):
    if float('.'.join(re.findall(r'\d+', distance))) > float(user.distance_from_center_max):
        bot.send_message(message.chat.id, 'Больше отелей, с указанной '
                                          'удаленностью от центра, не обнаружено.')
        return 'Break'
    else:
        return None


def check_price(message, user, hotel_counter, len_res):
    if hotel_counter == len_res and len_res < int(user.hotels_count):
        bot.send_message(message.chat.id, 'Больше отелей, в указанной '
                                          'ценовой категории, не обнаружено.')


def check_address(i_elem):
    try:
        address = i_elem['address']['streetAddress']
    except KeyError:
        address = 'Адрес не указан'
    return address


def attach_photos(i_elem, user, message):
    photo_links = list()
    photo_counter = 1
    photos_info = photos(i_elem['id'])
    if photos_info:
        for i_value in photos_info:
            photo_links.append(i_value['baseUrl'].replace('{size}', 'w'))
            if photo_counter == int(user.load_image_count):
                break
            photo_counter += 1
        if int(user.load_image_count) == 1:
            return photo_links[0]
        else:
            return photo_links
    else:
        cleaner(message)
        bot.send_message(message.chat.id, 'Извините, возникла ошибка при загрузке фотографий.')
        key_continue(message)


def get_distance(i_elem, user, message):
    try:
        distance = [i_dist['distance'] for i_dist in i_elem['landmarks'] if i_dist['label'] ==
                    'Центр города'][0]

        if user.distance_from_center_max:
            if check_distance(distance, user, message):
                return 'Break'
    except IndexError:
        distance = 'Не указано.'
    return distance


def get_price(i_elem):
    try:
        price = i_elem['ratePlan']['price']['current']
    except KeyError:
        price = 'Цена не указана.'
    return price


def get_photo(i_elem, user, message):
    i_photos = attach_photos(i_elem, user, message)
    if int(user.load_image_count) == 1:
        bot.send_photo(message.chat.id, i_photos)
    else:
        try:
            bot.send_media_group(message.chat.id, [types.InputMediaPhoto(i_url) for i_url in i_photos])
        except BaseException:
            bot.send_message(message.chat.id, 'Извините, но к данному отелю не получилось сгруппировать фотографии.')


def get_sum_price(user, price):
    if user.days_sum:
        try:
            price_one_day = int(''.join(re.findall(r'\d+', price)))
            price_sum = str(user.days_sum * price_one_day)
            if len(price_sum) > 3:
                price_sum = '{},{}'.format(price_sum[:-3], price_sum[-3:])
            return '\nСуммарная стоимость: {} RUB'.format(price_sum)
        except ValueError:
            return '\nСуммарная стоимость: Не может быть посчитана, так как цена у отеля не указана.'
    else:
        return ''


def table_entry(message, user):
    with db:
        User.create(id=message.chat.id,
                    command=user.command,
                    date_time=datetime.datetime.now().strftime("%d.%m.%Y - %H:%M"),
                    results=user.hotels)


def general_process(message):
    user = Users.get_user(message.chat.id)
    if user.load_image.lower() == 'да':
        user.load_image_count = input_validation(message, 3)
    else:
        user.load_image_count = 'None'
    if user.load_image_count:
        bot.send_message(message.chat.id, 'Подождите...')
        id_city = city_definition(user, message)

        if id_city:
            user.hotels = str()

            hotel_counter = 0

            i_result = check_results(user, id_city, message)

            if i_result:
                for i_elem in i_result:

                    distance = get_distance(i_elem, user, message)
                    if distance == 'Break':
                        break

                    address = check_address(i_elem)

                    price = get_price(i_elem)

                    price_sum = get_sum_price(user, price)

                    res = 'Название отеля: {}\nАдрес отеля: {}' \
                          '\nРасстояние от центра: {}'\
                          '\nСтоимость отеля за ночь: {}' \
                          '{}' \
                          '\nСсылка на отель: https://ru.hotels.com/ho{}\n'.format(i_elem['name'],
                                                                                   address, distance,
                                                                                   price, price_sum,
                                                                                   i_elem['id'])

                    if user.load_image.lower() == 'да':
                        res += 'Ожидайте загрузку фотографий\n(в отдельном сообщении)...'
                        bot.send_message(message.chat.id, res)
                        get_photo(i_elem, user, message)
                    else:
                        bot.send_message(message.chat.id, res)


                    user.hotels += '{},\n'.format(i_elem['name'])

                    hotel_counter += 1

                    if user.command == '/bestdeal':
                        check_price(message, user, hotel_counter, len(i_result))

                    if hotel_counter == int(user.hotels_count):
                        break

                table_entry(message, user)
                cleaner(message)
                key_continue(message)


def helper(message):
    bot.send_message(message.chat.id, """\
Пожалуйста, введите одну из предложенных команд:\n
/lowprice - Узнать топ самых дешёвых отелей в городе.\n
/highprice - Узнать топ самых дорогих отелей в городе.\n
/bestdeal - Узнать топ отелей, наиболее подходящих по цене и расположению от центра.\n
/history - Узнать историю поиска отелей.\n
/help - Узнать список доступных команд БОТу.\
""")


def cleaner(message):
    Users.del_user(message.chat.id)


def i_history(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('Продолжить')
    info = (User.
            select().
            where(message.chat.id == User.id))
    is_on = False
    for i_table_line in info:
        is_on = True
        mess = '{} была выполнена команда: {}\nРезультаты поиска:\n{}'.format(
                i_table_line.date_time, i_table_line.command, i_table_line.results)
        bot.send_message(message.from_user.id, mess)
    if not is_on:
        bot.send_message(message.from_user.id, 'Вы еще ничего не искали.')
    key_continue(message)