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
    cnt_object_in_row = 3
    dict_of_buttons = {"Шинобу" : "1", "Музыка" : "2", "Подписки" : "3", "Напоминалки" : "4", "Шифрование" : "5", "Японский" : "6", "Донат" : "7", "Еще" : "8"}
    if str(chat_id) == str(my_cfg.chat_id_onwer):
        dict_of_buttons["Админка"] = 9
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return reply_to