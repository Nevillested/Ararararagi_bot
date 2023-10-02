from telebot import types
import my_cfg

#метод для создания инлайн-клавиатуры. На вход получает словарь из пары "ид кнопки-название кнопки" и количество кнопок в строке, а на выходе отдает саму клавиатуру
def create_inline_kb(dict_of_buttons, cnt_object_in_row):
    reply_to = types.InlineKeyboardMarkup()
    row = []
    for i in dict_of_buttons:
        current_button = types.InlineKeyboardButton(text = i, callback_data = dict_of_buttons[i])
        row.append(current_button)
        if len(row) == cnt_object_in_row:
            reply_to.add(*row)
            row = []
    reply_to.add(*row)
    return reply_to

#клавиатура основного меню
def main_menu(chat_id):
    text = ' *Главное меню* '
    cnt_object_in_row = 3
    dict_of_buttons = {"Шинобу" : "1", "Музыка" : "2", "Подписки" : "3", "Напоминалки" : "4", "Шифрование" : "5", "Японский" : "6", "Донат" : "7", "Еще" : "8"}
    if str(chat_id) == str(my_cfg.chat_id_onwer):
        dict_of_buttons["Админка"] = 9
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return text, reply_to

#клавиатура основного меню Шинобу
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

#клавиатура основного меню музыки
def music_main():
    text = 'Музыка. Выбери букву, с которой начинается исполнитель'
    cnt_object_in_row = 0
    dict_of_buttons = {}
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return text, reply_to

#клавиатура основного меню подписок
def subscriptions_main():
    text = 'Управление подписками'
    cnt_object_in_row = 0
    dict_of_buttons = {}
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return text, reply_to

#клавиатура основного меню напоминалок
def notifications_main():
    text = 'Управление напоминалками'
    cnt_object_in_row = 0
    dict_of_buttons = {}
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return text, reply_to

#клавиатура основного меню шифрования / дешифрования
def encrypting_main():
    text = 'Шифрование / дешифрование текста'
    cnt_object_in_row = 0
    dict_of_buttons = {}
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return text, reply_to

#клавиатура основного меню изучения японского
def japanese_main():
    text = 'Изучаем японский'
    cnt_object_in_row = 0
    dict_of_buttons = {}
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return text, reply_to

#клавиатура основного меню доната
def donat_main():
    text = 'Донат изобретателю велосипеда'
    cnt_object_in_row = 0
    dict_of_buttons = {}
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return text, reply_to

#клавиатура основного меню с оставшимися полезностями
def something_main():
    text = 'Полезности'
    cnt_object_in_row = 0
    dict_of_buttons = {}
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return text, reply_to

#клавиатура основного меню админки
def admin_main():
    text = 'Админка'
    cnt_object_in_row = 0
    dict_of_buttons = {}
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return text, reply_to
