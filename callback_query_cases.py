from telebot import types
import keyboards
import queries_to_bd

#точка входа главного меню, корень всех ветвлений
def case_main(call, bot):
    current_btn_name = call.data
    current_chat_id = call.message.chat.id
    current_message_id = call.message.message_id
    current_result_text = ''
    current_reply_markup = types.InlineKeyboardMarkup()

    #каждый базовый ID описан в методе создания основной клавиатуры - keyboards.main_menu. Каждая ветка меню раскидана по методам для удобства написания кода. Чтобы тупо не запутаться в if-elif
    if current_btn_name.startswith('1'):
        (current_result_text, current_reply_markup) = shinobu(current_chat_id, current_btn_name)
    elif current_btn_name.startswith('2'):
        (current_result_text, current_reply_markup) = music(current_chat_id, current_btn_name)
    elif current_btn_name.startswith('3'):
        (current_result_text, current_reply_markup) = subscriptions(current_chat_id, current_btn_name)
    elif current_btn_name.startswith('4'):
        (current_result_text, current_reply_markup) = notifications(current_chat_id, current_btn_name)
    elif current_btn_name.startswith('5'):
        (current_result_text, current_reply_markup) = encrypting(current_chat_id, current_btn_name)
    elif current_btn_name.startswith('6'):
        (current_result_text, current_reply_markup) = japanese(current_chat_id, current_btn_name)
    elif current_btn_name.startswith('7'):
        (current_result_text, current_reply_markup) = donat(current_chat_id, current_btn_name)
    elif current_btn_name.startswith('8'):
        (current_result_text, current_reply_markup) = something(current_chat_id, current_btn_name)
    elif current_btn_name.startswith('9'):
        (current_result_text, current_reply_markup) = admin(current_chat_id, current_btn_name)
    else:
        current_result_text = 'Нажата какая-то кнопка'

    queries_to_bd.save_outcome_data(current_chat_id, current_message_id, current_result_text)

    bot.edit_message_text(chat_id = current_chat_id, message_id = current_message_id, text = current_result_text, reply_markup = current_reply_markup)

#ветка кнопок с Шинобу
def shinobu(chat_id, btn_data):
    text = ''
    reply_markup = types.InlineKeyboardMarkup()

    if btn_data == '1':
        (text, reply_markup) = keyboards.shinobu_main()
    elif btn_data == '1/1':
        (text, reply_markup) = keyboards.shinobu_pic()
    elif btn_data == '1/1/1':
        (text, reply_markup) = keyboards.shinobu_pic()
        text = queries_to_bd.get_last_bot_text_menu(chat_id)
    elif btn_data == '1/1/2':
        (text, reply_markup) = keyboards.shinobu_main()
    elif btn_data == '1/2':
        (text, reply_markup) = keyboards.shinobu_stick()
    elif btn_data == '1/2/1':
        (text, reply_markup) = keyboards.shinobu_stick()
        text = queries_to_bd.get_last_bot_text_menu(chat_id)
    elif btn_data == '1/2/2':
        (text, reply_markup) = keyboards.shinobu_main()
    elif btn_data == '1/3':
        (text, reply_markup) = keyboards.main_menu(chat_id)
    return text, reply_markup

#ветка кнопок с музыкой
def music(chat_id, btn_data):
    (text, reply_markup) = keyboards.music_main()
    return text, reply_markup

#ветка кнопок с подписками
def subscriptions(chat_id, btn_data):
    (text, reply_markup) = keyboards.subscriptions_main()
    return text, reply_markup

#ветка кнопок с напоминалками
def notifications(chat_id, btn_data):
    (text, reply_markup) = keyboards.notifications_main()
    return text, reply_markup

#ветка кнопок с шифрованием
def encrypting(chat_id, btn_data):
    (text, reply_markup) = keyboards.encrypting_main()
    return text, reply_markup

#ветка кнопок с изучением японского
def japanese(chat_id, btn_data):
    (text, reply_markup) = keyboards.japanese_main()
    return text, reply_markup

#ветка кнопок с донатом
def donat(chat_id, btn_data):
    (text, reply_markup) = keyboards.donat_main()
    return text, reply_markup

#ветка кнопок с оставшимися полезностями
def something(chat_id, btn_data):
    (text, reply_markup) = keyboards.something_main()
    return text, reply_markup

#ветка кнопок админки
def admin(chat_id, btn_data):
    (text, reply_markup) = keyboards.admin_main()
    return text, reply_markup