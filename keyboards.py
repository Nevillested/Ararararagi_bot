from telebot import types
import my_cfg
import queries_to_bd
import datetime
import calendar
import common_methods
import random

#метод для создания инлайн-клавиатуры. На вход получает словарь из пары "ид кнопки-название кнопки" и количество кнопок в строке, а на выходе отдает саму клавиатуру
def create_inline_kb(dict_of_buttons, cnt_object_in_row):
    reply_to = types.InlineKeyboardMarkup(row_width = cnt_object_in_row)
    row = []
    for i in dict_of_buttons:
        current_button = types.InlineKeyboardButton(text = i, callback_data = dict_of_buttons[i])
        row.append(current_button)
        if len(row) == cnt_object_in_row:
            reply_to.add(*row)
            row = []
    reply_to.add(*row)
    return reply_to

############################# клавиатура основного меню #############################
def main_menu(chat_id):
    text = 'Главное меню'
    cnt_object_in_row = 3
    dict_of_buttons = {"Шинобу" : "1", "Музыка" : "2", "Подписки" : "3", "Напоминалки" : "4", "Шифрование" : "5", "Японский" : "6", "Донат" : "7", "Речь ⇄ текст" : "8", "Еще" : "9"}
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return text, reply_to

############################# клавиатуры Шинобу #############################
#главное меню Шинобу
def shinobu_main():
    text = 'Shinobu is the best girl'
    cnt_object_in_row = 2
    dict_of_buttons = {"Дай пикчу!" : "1/1", "Дай стикер!": "1/2", "Назад" : "1/3"}
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return text, reply_to

#клавиатура получения пикчи Шинобу
def shinobu_pic():
    text = 'Получите пикчу лучшей девочки'
    cnt_object_in_row = 2
    dict_of_buttons = {"Еще!" : "1/1/1", "Назад": "1/1/2"}
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return text, reply_to

#клавиатура получения стикера Шинобу
def shinobu_stick():
    text = 'Получите стикер лучшей девочки'
    cnt_object_in_row = 2
    dict_of_buttons = {"Еще!" : "1/2/1", "Назад": "1/2/2"}
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return text, reply_to

############################# клавиатуры музыки #############################
#клавиатура первого символа исполнителя
def music_abc():
    text = 'Выбери символ, с которого начинается название исполнителя'
    cnt_object_in_row = 5
    dict_of_buttons = queries_to_bd.get_abc_dict()
    sorted_dict_of_buttons = dict(sorted(dict_of_buttons.items(), key=lambda item: item[0]))
    sorted_dict_of_buttons["Назад"] = "2/back_5/"
    reply_to = create_inline_kb(sorted_dict_of_buttons, cnt_object_in_row)
    return text, reply_to

#клавитура исполнителей, начинающихся с определенного символа
def music_performers(first_char_id):
    text = 'Выбери исполнителя'
    cnt_object_in_row = 3
    dict_of_buttons = queries_to_bd.get_performer_dict(first_char_id)
    sorted_dict_of_buttons = dict(sorted(dict_of_buttons.items(), key=lambda item: item[0]))
    sorted_dict_of_buttons["Назад"] = "2/back_4/"
    reply_to = create_inline_kb(sorted_dict_of_buttons, cnt_object_in_row)
    return text, reply_to

#клавиатура альбомов исполнителя
def music_albums(performer_id):
    text = 'Выбери альбом'
    cnt_object_in_row = 3
    dict_of_buttons = queries_to_bd.get_albums_dict(performer_id)
    sorted_dict_of_buttons = dict(sorted(dict_of_buttons.items(), key=lambda item: item[0]))
    sorted_dict_of_buttons["Назад"] = "2/back_3/" + performer_id
    reply_to = create_inline_kb(sorted_dict_of_buttons, cnt_object_in_row)
    return text, reply_to

#клавиатура песен в альбоме
def music_songs_in_album(album_id):
    text = 'Выбери песню'
    cnt_object_in_row = 3
    dict_of_buttons = queries_to_bd.get_songs_in_album_dict(album_id)
    sorted_dict_of_buttons = dict(sorted(dict_of_buttons.items(), key=lambda item: item[0]))
    sorted_dict_of_buttons["Назад"] = "2/back_2/" + album_id
    reply_to = create_inline_kb(sorted_dict_of_buttons, cnt_object_in_row)
    return text, reply_to

#получает последнее меню
def music_menu_last(flg_success_size, song_id):
    if flg_success_size == 1:
        text = "Держи"
    elif flg_success_size == 0:
        text = "Соре, файл весит больше 50 мб, телега не позволяет ботам отправлять такие файлы."
    reply_to = create_inline_kb({"Назад" : "2/back_1/" + song_id}, 1)
    return text, reply_to

############################# клавиатуры подписок #############################
#клавиатура основного меню подписок
def subscriptions_main():
    text = 'Подписки на рассылки'
    cnt_object_in_row = 2
    dict_of_buttons = queries_to_bd.get_dict_of_full_subs()
    dict_of_buttons["Назад"] = "3/back_main"
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return text, reply_to

#клавиатура статуса подписки и предложением включить или выключит подписку
def subscriptions_cur_status(activity_flg, subscription_id):
    cnt_object_in_row = 1
    text = ''
    dict_of_buttons = {}
    if activity_flg == 1:
        text = 'Подписка активна, отключить?'
        dict_of_buttons["Да, отключить"] = "3/turn_off/" + subscription_id
    else:
        text = 'Подписка не активна, включить?'
        dict_of_buttons["Да, включить"] = "3/turn_on/" + subscription_id
    dict_of_buttons["Назад"] = "3/back_subs"
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return text, reply_to

#клавиатура с результатом выключения или включения подписки и возвратом на основное меню подписок
def subscription_result(activity_flg):
    cnt_object_in_row = 1
    text = ''
    dict_of_buttons = {"Назад к списку подписок" : "3"}
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    if activity_flg == 1:
        text = 'Подписка включена'
    elif activity_flg == 0:
        text = 'Подписка отключена'
    return text, reply_to

############################# клавиатуры напоминалок #############################

#клавиатура основного меню напоминалок
def notifications_main():
    text = 'Управление напоминалками'
    cnt_object_in_row = 1
    dict_of_buttons = {"Все имеющиеся напоминалки" : "4/1", "Новая напоминалка" : "4/2", "Назад" : "4/3"}
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return text, reply_to

#клавиатура с текущими напоминалками пользователя
def notifications_current(chat_id):
    text = 'Все имеющиеся напоминалки'
    cnt_object_in_row = 1
    dict_of_buttons = queries_to_bd.get_current_notifications(chat_id)
    dict_of_buttons["Назад"] = "4/1/back"
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return text, reply_to

#Меню редактирования напоминалки
def notification_edit(notification_id):
    notification_desc = queries_to_bd.get_notification_desc(notification_id)
    text = 'Редактирование напоминалки\n' + notification_desc
    cnt_object_in_row = 3
    dict_of_buttons = {"Год" : "4/edit/year_num/" + str(notification_id), "Месяц" : "4/edit/month_num/" + str(notification_id), "День" : "4/edit/day_num/" + str(notification_id), "Час" : "4/edit/hour_num/" + str(notification_id), "Минута" : "4/edit/min_num/" + str(notification_id), "Частота повтора" : "4/edit/repeat_interval/" + str(notification_id),"Вкл/выкл" : "4/edit/activity/" + str(notification_id), "Удалить" : "4/edit/delete/" + str(notification_id), "Назад к напоминалкам" : "4"}
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return text, reply_to

#клавиатура выбора года старта напоминалки
def notif_years(notification_id):
    text = 'Год напоминалки'
    cnt_object_in_row = 3
    current_year = datetime.datetime.now().year
    keyboard_dict = {}
    for i in range(10):
        dict_key = '4/set/year_num/' + str(current_year + i) + '/' + notification_id
        dict_value = str(current_year + i)
        keyboard_dict[dict_value] = dict_key
    keyboard_dict["Назад"] = "4/1/" + notification_id
    reply_to = create_inline_kb(keyboard_dict, cnt_object_in_row)
    return text, reply_to

#клавиатура выбора месяца старта напоминалки
def notif_months(notification_id):
    selected_year = queries_to_bd.get_value_from_notification(notification_id, 'year_num')
    text = ''
    keyboard_dict = {}
    cnt_object_in_row = 4
    dict_month = {"1":"Январь","2":"Февраль","3":"Март","4":"Апрель","5":"Май","6":"Июнь","7":"Июль","8":"Август","9":"Сентябрь","10":"Октябрь","11":"Ноябрь","12":"Декабрь"}
    if selected_year == 'None':
        text = 'Сначала надо выбрать год'
    else:
        text = 'Месяц напоминалки'
        current_month = datetime.datetime.now().month
        if str(datetime.datetime.now().year) == selected_year:
            for item in dict_month:
                if int(item) >= int(current_month):
                    dict_key = '4/set/month_num/' + str(item) + '/' + notification_id
                    dict_value = dict_month[item]
                    keyboard_dict[dict_value] = dict_key
        else:
            for item in dict_month:
                dict_key = '4/set/month_num/' + str(item) + '/' + notification_id
                dict_value = dict_month[item]
                keyboard_dict[dict_value] = dict_key
    keyboard_dict["Назад"] = "4/1/" + notification_id
    reply_to = create_inline_kb(keyboard_dict, cnt_object_in_row)
    return text, reply_to

#клавиатура выбора дня старта напоминалки
def notif_days(notification_id):
    selected_year = queries_to_bd.get_value_from_notification(notification_id, 'year_num')
    selected_month = queries_to_bd.get_value_from_notification(notification_id, 'month_num')
    text = ''
    keyboard_dict = {}
    cnt_object_in_row = 4
    if selected_month == 'None':
        text = 'Сначала надо выбрать месяц'
    else:
        text = 'День напоминалки'
        current_year = str(datetime.datetime.now().year)
        current_month = str(datetime.datetime.now().month)
        day_start = 1
        day_end = calendar.monthrange(int(selected_year), int(selected_month))[1]
        if current_year == selected_year and current_month == selected_month:
            day_start = datetime.datetime.now().day

        for i in range(int(day_start), int(day_end) + 1):
            dict_key = '4/set/day_num/' + str(i) + '/' + notification_id
            dict_value = str(i)
            keyboard_dict[dict_value] = dict_key
    keyboard_dict["Назад"] = "4/1/" + notification_id
    reply_to = create_inline_kb(keyboard_dict, cnt_object_in_row)
    return text, reply_to

#клавиатура выбора часа старта напоминалки
def notif_hours(notification_id):
    selected_year = queries_to_bd.get_value_from_notification(notification_id, 'year_num')
    selected_month = queries_to_bd.get_value_from_notification(notification_id, 'month_num')
    selected_day = queries_to_bd.get_value_from_notification(notification_id, 'day_num')
    text = ''
    keyboard_dict = {}
    cnt_object_in_row = 4
    if selected_day == 'None':
        text = 'Сначала надо выбрать день'
    else:
        text = 'Час напоминалки'
        current_year = str(datetime.datetime.now().year)
        current_month = str(datetime.datetime.now().month)
        current_day = str(datetime.datetime.now().day)
        hour_start = 0
        if current_year == selected_year and current_month == selected_month and current_day == selected_day:
            hour_start = datetime.datetime.now().hour

        for i in range(int(hour_start), 24):
            dict_key = '4/set/hour_num/' + str(i) + '/' + notification_id
            dict_value = str(i)
            keyboard_dict[dict_value] = dict_key
    keyboard_dict["Назад"] = "4/1/" + notification_id
    reply_to = create_inline_kb(keyboard_dict, cnt_object_in_row)
    return text, reply_to

#клавиатура выбора часа старта напоминалки
def notif_minutes(notification_id):
    selected_year = queries_to_bd.get_value_from_notification(notification_id, 'year_num')
    selected_month = queries_to_bd.get_value_from_notification(notification_id, 'month_num')
    selected_day = queries_to_bd.get_value_from_notification(notification_id, 'day_num')
    selected_hour = queries_to_bd.get_value_from_notification(notification_id, 'hour_num')
    text = ''
    keyboard_dict = {}
    cnt_object_in_row = 4
    if selected_day == 'None':
        text = 'Сначала надо выбрать час'
    else:
        text = 'Минута напоминалки'
        current_year = str(datetime.datetime.now().year)
        current_month = str(datetime.datetime.now().month)
        current_day = str(datetime.datetime.now().day)
        current_hour = str(datetime.datetime.now().hour)
        min_start = 0
        if current_year == selected_year and current_month == selected_month and current_day == selected_day and current_hour == selected_hour:
            min_start = datetime.datetime.now().minute
        for i in range(min_start, 60):
            dict_key = '4/set/minute_num/' + str(i) + '/' + notification_id
            dict_value = str(i)
            keyboard_dict[dict_value] = dict_key
    keyboard_dict["Назад"] = "4/1/" + notification_id
    reply_to = create_inline_kb(keyboard_dict, cnt_object_in_row)
    return text, reply_to

#клавиатура с выбором периодичности повтора
def notif_repeat_interval(notification_id):
    text = 'Периодичность повтора'
    cnt_object_in_row = 3
    keyboard_dict = {"Ежегодно" : "4/set/every_year_flg/1/" + str(notification_id),
                     "Ежемесячно" : "4/set/every_month_flg/1/" + str(notification_id),
                     "Еженедельно" : "4/set/every_week_flg/1/" + str(notification_id),
                     "Ежедневно" : "4/set/every_day_flg/1/" + str(notification_id),
                     "Ежечасно" : "4/set/every_hour_flg/1/" + str(notification_id),
                     "Ежеминутно" : "4/set/every_minute_flg/1/" + str(notification_id),
                     "Не повторять" : "4/set/repeat_flg/0/" + str(notification_id)
                    }
    keyboard_dict["Назад"] = "4/1/" + notification_id
    reply_to = create_inline_kb(keyboard_dict, cnt_object_in_row)
    return text, reply_to

#выдает клавиатуру со статусом напоминалки и предложением включить или выключить ее
def notif_turn_on_off(notification_id):
    text = ''
    cnt_object_in_row = 3
    keyboard_dict = {}
    selected_year = queries_to_bd.get_value_from_notification(notification_id, 'year_num')
    selected_month = queries_to_bd.get_value_from_notification(notification_id, 'month_num')
    selected_day = queries_to_bd.get_value_from_notification(notification_id, 'day_num')
    selected_hour = queries_to_bd.get_value_from_notification(notification_id, 'hour_num')
    selected_minute = queries_to_bd.get_value_from_notification(notification_id, 'minute_num')
    selected_repeat_flg = queries_to_bd.get_value_from_notification(notification_id, 'repeat_flg')
    if str(selected_year) == 'None' or  str(selected_month) == 'None' or  str(selected_day) == 'None' or  str(selected_hour) == 'None' or  str(selected_minute) == 'None' or  str(selected_repeat_flg) == 'None':
        if str(selected_year) == 'None':
            text = 'Необходимо указать год!'
        if str(selected_month) == 'None':
            text = 'Необходимо указать месяц!'
        if str(selected_day) == 'None':
            text = 'Необходимо указать день!'
        if str(selected_hour) == 'None':
            text = 'Необходимо указать час!'
        if str(selected_minute) == 'None':
            text = 'Необходимо указать минуту!'
        if str(selected_repeat_flg) == 'None':
            text = 'Необходимо указать периодичность повтора!'
    else:
        status = queries_to_bd.get_status_of_notification(notification_id)
        if status == '0':
            text = 'На текущий момент напоминалка выключена.\nВключить?'
            keyboard_dict = {"Да, включить" : "4/set/activity_flg/1/" + str(notification_id)}
        elif status == '1':
            text = 'На текущий момент напоминалка включена.\nОтключить?'
            keyboard_dict = {"Да, выключить" : "4/set/activity_flg/0/" + str(notification_id)}
    keyboard_dict["Назад"] = "4/1/" + notification_id
    reply_to = create_inline_kb(keyboard_dict, cnt_object_in_row)
    return text, reply_to

def notif_delete(notification_id):
    text = 'Удалить напоминалку?'
    cnt_object_in_row = 1
    keyboard_dict = {"Да, удалить" : "4/delete/" + str(notification_id), "Назад" : "4/1/" + str(notification_id)}
    reply_to = create_inline_kb(keyboard_dict, cnt_object_in_row)
    return text, reply_to

############################# клавиатуры с шифрованием и дешифрованием #############################

#выбора языка
def crypting_lang():
    text = 'Выбери язык'
    cnt_object_in_row = 2
    dict_of_buttons = {"Русский" : "5/1/RU", "English" : "5/1/EN", "Назад" : "5/back/0"}
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return text, reply_to

#выбор типа операции
def crypting_operation(lang_code):
    text = 'Шифрование / дешифрование текста. Язык - ' + lang_code
    cnt_object_in_row = 2
    dict_of_buttons = {"Зашифровать" : "5/2/" + lang_code + "/encrypt", "Расшифровать" : "5/2/" + lang_code + "/decrypt", "Назад" : "5/back/1"}
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return text, reply_to

#выбор ключа сдвига
def crypting_key(lang_code, operation_type):
    cnt_object_in_row = 5
    text = ''
    if operation_type == "encrypt":
        text = 'Выбери ключ для шифрования'
    elif operation_type == "decrypt":
        text = 'Выбери ключ для дешифрования'
    dict_of_buttons = {}
    for i in range(1, 20):
        dict_of_buttons[i] = "5/3/" + str(i) + "/"+ lang_code + "/" + operation_type

    dict_of_buttons["Назад"] = "5/back/2/" + lang_code

    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return text, reply_to

#предложение пользователю ввести текст для шифровки или дешифровки
def crypting_text(lang_code, operation_type):
    reply_to = types.InlineKeyboardMarkup()
    text = ''
    if lang_code == 'RU' and operation_type == "encrypt":
        text = 'Введи текст на русском языке, который хочешь зашифровать\nПринимаются только символы и русские буквы'
    elif lang_code == 'RU' and operation_type == "decrypt":
        text = 'Введи текст на русском языке, который хочешь расшифровать\nПринимаются только символы и русские буквы'
    elif lang_code == 'EN' and operation_type == "encrypt":
        text = 'Введи текст на английском языке, который хочешь зашифровать\nПринимаются только символы и английские буквы'
    elif lang_code == 'EN' and operation_type == "decrypt":
        text = 'Введи текст на английском языке, который хочешь расшифровать\nПринимаются только символы и английские буквы'
    reply_to = create_inline_kb({"Назад" : "5/back/2/" + lang_code}, 1)
    return text, reply_to

#сама шифровка или дешифровка текста
def crypting_result(operation_type, lang_code, key, text_to_oper):
    reply_to = types.InlineKeyboardMarkup()
    text_out = common_methods.encrypting_decrypting(operation_type, lang_code, key, text_to_oper)
    reply_to = create_inline_kb({"Назад" : "5/back/2/" + lang_code}, 1)
    return text_out, reply_to

############################# клавиатуры с изучением японского #############################

#клавиатура с сообщением и кнопками, что японский теперь в другом боте
def jap_main():
    text = 'Изучение японского теперь вынесено в отдельного бота\n@jlpt_quiz_bot'
    cnt_object_in_row = 1
    dict_of_buttons = {"Назад":"6/1"}
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return text, reply_to

############################# клавиатуры с донатом #############################

#клавиатура основного меню доната
def donat_main():
    text = 'Донат изобретателю велосипеда'
    cnt_object_in_row = 1
    dict_of_buttons = {"Потому что я такой хорошенький - 100р" : "7/1", "На тяжелую жизнь бездомного разработчика - 150р" : "7/2", "На развитие бота, чтобы он делал вашу жизнь лучше - 200р" : "7/3", "На фигурки с лучшей девочкой ~~~р" : "7/4", "Назад" : "7/back/0"}
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return text, reply_to

#клавиатура последнего меню доната
def donat_invoice():
    text = 'Плоти.'
    cnt_object_in_row = 1
    dict_of_buttons = {"Назад":"7"}
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return text, reply_to

############################# клавиатуры с конвертацией текста в речь и наоборот #############################

#возвращает выбор языка (основная клавиатура)
def text_speech_lang():
    text = 'Меню преобразования войса в текст и наоборот\nВыбери язык'
    cnt_object_in_row = 2
    dict_of_buttons = {"RU" : "8/1", "EN" : "8/2"}
    dict_of_buttons["Назад"] = "8/back/0"
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return text, reply_to

#возвращает выбор типа операции
def text_speech_operation_type(btn_data):
    text = 'Что собираемся преобразовывать?'
    cnt_object_in_row = 2
    dict_of_buttons = {"Текст в войс" : btn_data + "/1", "Войс в текст" : btn_data + "/2"}
    dict_of_buttons["Назад"] = "8/back/1"
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return text, reply_to

#возвращает предложение прислать текст, который будет преобразован в войс
def text_speech_send_me_text(btn_data):
    lang_id = (btn_data.split('/'))[-2]
    lang = None
    if lang_id == '1':
        lang = 'русском'
    elif lang_id == '2':
        lang = 'английском'
    text = 'А теперь пришли текст на ' + lang + ' языке, который должен быть преобразован в войс'
    cnt_object_in_row = 1
    dict_of_buttons = {"Назад" : (btn_data)[:(btn_data.rfind('/'))]} #обрезает в строке все, что находится после последнего символа '/', включая его
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return text, reply_to

#возвращает предложение прислать аудио, который будет преобразован в текст
def text_speech_send_me_voice(btn_data):
    lang_id = (btn_data.split('/'))[-2]
    lang = None
    if lang_id == '1':
        lang = 'русском'
    elif lang_id == '2':
        lang = 'английском'
    text = 'А теперь пришли войс на ' + lang + ' языке, который должен быть преобразован в текст'
    cnt_object_in_row = 1
    dict_of_buttons = {"Назад" : (btn_data)[:(btn_data.rfind('/'))]} #обрезает в строке все, что находится после последнего символа '/', включая его
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return text, reply_to

#последнее меню по ветке распознавания войса в текст
def text_speech_result_text(recognized_text, lang_code):
    text = 'Результат распознавания текста в войсе:\n"' + recognized_text + '"'
    cnt_object_in_row = 1
    dict_of_buttons = {"Назад" : "8/" + str(lang_code)}
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return text, reply_to

#последнее меню по ветке преобразования текста в войс
def text_speech_result_voice(input_user_text, lang_code):
    text = 'Лови результат преобразования в войс твоего текста:\n"' + input_user_text + '"'
    cnt_object_in_row = 1
    dict_of_buttons = {"Назад" : "8/" + str(lang_code)}
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return text, reply_to

############################# клавиатуры с оставшимися полезностями #############################

#клавиатура основного меню с оставшимися полезностями
def something_main():
    text = 'Полезности'
    cnt_object_in_row = 2
    dict_of_buttons = {"Анекдоты" : "9/1", "Погода" : "9/2", "QR-код" : "9/3", "Рандомное решение (да/нет)" : "9/4", "Назад" : "9/back/0"}
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return text, reply_to

#клавиатура с анекдотом
def jokes(btn_data, chat_id):
    new_text = queries_to_bd.get_random_joke()
    old_text = queries_to_bd.get_last_bot_text_menu(chat_id)

    #если была нажата кнопка "еще", нужно проверить, что старый анекдот не равен текущему игенерировать до тех пор, пока не будет новый
    if btn_data == "9/1/1":
        while True:
            if new_text != old_text:
                break
            new_text = queries_to_bd.get_random_joke()

    cnt_object_in_row = 1
    dict_of_buttons = {"Еще!" : "9/1/1", "Назад" : "9"}
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return new_text, reply_to

#клавиатура с погодой
def weather():
    text = 'Погода на сегодня. Пришли название города'
    cnt_object_in_row = 1
    dict_of_buttons = {"Назад" : "9"}
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return text, reply_to

#клавиатура с результатом погоды
def weather_last_menu(city_name):
    text = city_name + '\n' + common_methods.current_weather(city_name)
    cnt_object_in_row = 1
    dict_of_buttons = {"Назад" : "9/2"}
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return text, reply_to

#клавиатура с предложением создать QR-кодом
def qr_code():
    text = 'Введи текст, который мы поместим в QR-код'
    cnt_object_in_row = 1
    dict_of_buttons = {"Назад" : "9"}
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return text, reply_to

#клавиатура с результатом создания QR-кода
def qr_code_result(user_text):
    text = 'Мы зашифровали в QR-код:\n"'+ user_text +'"'
    cnt_object_in_row = 1
    dict_of_buttons = {"Назад" : "9/3"}
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return text, reply_to

#клавиатура с предложением ввести тег для получение пикчи
def get_pic_by_teg_main():
    text = 'Окей, напиши в чат, что ищем'
    cnt_object_in_row = 1
    dict_of_buttons = {"Назад" : "9"}
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return text, reply_to

#клавиатура с результатом пикчи с реактора
def get_pic_by_teg_result():
    text = 'Держи'
    cnt_object_in_row = 1
    dict_of_buttons = {"Назад" : "9/4"}
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return text, reply_to

#клавиатура с рандомным ответом
def get_random(btn_data, chat_id):
    old_text = queries_to_bd.get_last_bot_text_menu(chat_id)
    new_text = None

    if random.randint(0,9) < 5:
        new_text = "Да!"
    else:
        new_text = "Нет!"

    #если была нажата кнопка "еще", нужно проверить, что старый ответ не равен текущему. Если равен - надо мальца видоизменить
    if btn_data == "9/5/1":
        if new_text == old_text:
            new_text += '!'

    cnt_object_in_row = 2
    dict_of_buttons = {"Еще разок!" : "9/5/1", "Назад" : "9"}
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return new_text, reply_to


