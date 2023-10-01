from telebot import types


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

def main_menu():
    cnt_object_in_row = 3
    dict_of_buttons = {"Первая кнопка" : "1", "Вторая кнопка" : "2", "Третья кнопка" : "3", "Четвертая кнопка" : "4", "Пятая кнопка" : "5", "Шестая кнопка" : "6", "Седьмая кнопка" : "7", "Восьмая кнопка" : "8", "Девятая кнопка" : "9","Десятая кнопка" : "10" }
    reply_to = create_inline_kb(dict_of_buttons, cnt_object_in_row)
    return reply_to