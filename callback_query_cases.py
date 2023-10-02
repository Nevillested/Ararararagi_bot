from telebot import types

#возвращает id следущего по очередь меню и строку из оставшихся меню
def get_current_menu(button_data):
    menu_id = ''
    remain_menu = ''
    if button_data.count('/') > 0:
        menu_id, remain_menu = button_data.split('/', 1)
    else:
        menu_id = button_data
    return menu_id, remain_menu

#точка входа главного меню
def case_main(call, bot):
    current_btn_name = call.data
    current_chat_id = call.message.chat.id
    current_message_id = call.message.message_id
    current_result_text = ''
    current_reply_markup = types.InlineKeyboardMarkup()

    #получаем текущий id меню и оставшиеся id меню
    (current_menu_id, remain_menu) = get_current_menu(current_btn_name)

    if current_menu_id == '1':
        (current_result_text, current_reply_markup) = shinobu(remain_menu)
    elif current_menu_id == '2':
        (current_result_text, current_reply_markup) = music(remain_menu)
    elif current_menu_id == '3':
        (current_result_text, current_reply_markup) = subscriptions(remain_menu)
    elif current_menu_id == '4':
        (current_result_text, current_reply_markup) = notifications(remain_menu)
    elif current_menu_id == '5':
        (current_result_text, current_reply_markup) = encrypting(remain_menu)
    elif current_menu_id == '6':
        (current_result_text, current_reply_markup) = japanese(remain_menu)
    elif current_menu_id == '7':
        (current_result_text, current_reply_markup) = donat(remain_menu)
    elif current_menu_id == '8':
        (current_result_text, current_reply_markup) = something(remain_menu)
    else:
        current_result_text = 'Нажата какая-то кнопка'

    bot.edit_message_text(chat_id = current_chat_id, message_id = current_message_id, text = current_result_text, reply_markup = current_reply_markup)

#меню с Шинобу
def shinobu(remain_menu):
    reply_markup = keyboards.()
    text = 'Shinobu is the best girl'
    return text, reply_markup

#меню с музыкой
def music(remain_menu):
    reply_markup = keyboards.()
    text = 'Музыка'
    return text, reply_markup

#меню с подписками
def subscriptions(remain_menu):
    reply_markup = keyboards.()
    text = 'Подписки'
    return text, reply_markup

#меню с напоминалками
def notifications(remain_menu):
    reply_markup = keyboards.()
    text = 'Напоминалки'
    return text, reply_markup

#меню с шифрованием
def encrypting(remain_menu):
    reply_markup = keyboards.()
    text = 'Шифрование и дешифрование текста'
    return text, reply_markup

#меню с изучением японского
def japanese(remain_menu):
    reply_markup = keyboards.()
    text = 'Изучаем японский'
    return text, reply_markup

#меню с донатом
def donat(remain_menu):
    reply_markup = tkeyboards.()
    text = 'Донат изобретателю велосипеда'
    return text, reply_markup

#меню с оставшимися полезностями
def something(remain_menu):
    reply_markup = keyboards.()
    text = 'Полезности'
    return text, reply_markup