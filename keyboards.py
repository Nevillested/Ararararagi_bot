from telebot import types
import my_cfg
import queries_to_bd

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

#клавиатура основного меню
def main_menu(chat_id):
    text = 'Главное меню'
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

#клавиатура основного меню музыки (первый символ исполнителя)
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
