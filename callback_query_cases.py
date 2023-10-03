from telebot import types
import keyboards
import queries_to_bd
import common_methods
import os

#точка входа главного меню, корень всех ветвлений
def case_main(call, bot):
    current_btn_name = call.data
    current_chat_id = call.message.chat.id
    current_message_id = call.message.message_id
    current_result_text = ''
    current_reply_markup = types.InlineKeyboardMarkup()

    #каждый базовый ID описан в методе создания основной клавиатуры - keyboards.main_menu. Каждая ветка меню раскидана по методам для удобства написания кода. Чтобы тупо не запутаться в if-elif
    if current_btn_name.startswith('1'):
        (current_result_text, current_reply_markup) = shinobu(bot, current_chat_id, current_message_id, current_btn_name)
    elif current_btn_name.startswith('2'):
        (current_result_text, current_reply_markup) = music(bot, current_chat_id, current_btn_name)
    elif current_btn_name.startswith('3'):
        (current_result_text, current_reply_markup) = subscriptions(bot, current_chat_id, current_btn_name)
    elif current_btn_name.startswith('4'):
        (current_result_text, current_reply_markup) = notifications(bot, current_chat_id, current_btn_name)
    elif current_btn_name.startswith('5'):
        (current_result_text, current_reply_markup) = encrypting(bot, current_chat_id, current_btn_name)
    elif current_btn_name.startswith('6'):
        (current_result_text, current_reply_markup) = japanese(bot, current_chat_id, current_btn_name)
    elif current_btn_name.startswith('7'):
        (current_result_text, current_reply_markup) = donat(bot, current_chat_id, current_btn_name)
    elif current_btn_name.startswith('8'):
        (current_result_text, current_reply_markup) = something(bot, current_chat_id, current_btn_name)
    elif current_btn_name.startswith('9'):
        (current_result_text, current_reply_markup) = admin(bot, current_chat_id, current_btn_name)
    else:
        current_result_text = 'Нажата какая-то кнопка'

    queries_to_bd.save_outcome_data(current_chat_id, current_message_id, 'button text', current_result_text)

    bot.edit_message_text(chat_id = current_chat_id, message_id = current_message_id, text = current_result_text, reply_markup = current_reply_markup)

#ветка кнопок с Шинобу
def shinobu(bot, chat_id, msg_id, btn_data):
    text = ''
    reply_markup = types.InlineKeyboardMarkup()

    #кнопка, открывающая основное меню Шинобу
    if btn_data == '1':
        (text, reply_markup) = keyboards.shinobu_main()
    #кнопка, открывающая меню с отправкой пикчи с Шинобу
    elif btn_data == '1/1':
        (text, reply_markup) = keyboards.shinobu_pic()
        common_methods.send_shinobu_pic(bot, chat_id, msg_id)
    #кнопка, заново генерирующая тоже меню, где находится, но меняет текст самого меню (чтобы телеграм не давал ошибку) и отправляющая повторно пикчу
    elif btn_data == '1/1/1':
        (text, reply_markup) = keyboards.shinobu_pic()
        text = queries_to_bd.get_last_bot_text_menu(chat_id)
        common_methods.send_shinobu_pic(bot, chat_id, msg_id)
    #кнопка, возвращающая на основное меню Шинобу из меню пикчи с Шинобу
    elif btn_data == '1/1/2':
        (text, reply_markup) = keyboards.shinobu_main()
    #кнопка, открывающая меню с отправкой стикера с Шинобу
    elif btn_data == '1/2':
        (text, reply_markup) = keyboards.shinobu_stick()
        common_methods.send_shinobu_stick(bot, chat_id, msg_id)
    #кнопка, заново генерирующая тоже меню, где находится, но меняет текст самого меню (чтобы телеграм не давал ошибку) и отправляющая повторно стикер
    elif btn_data == '1/2/1':
        (text, reply_markup) = keyboards.shinobu_stick()
        text = queries_to_bd.get_last_bot_text_menu(chat_id)
        common_methods.send_shinobu_stick(bot, chat_id, msg_id)
    #кнопка, возвращающая на основное меню Шинобу из меню стикера с Шинобу
    elif btn_data == '1/2/2':
        (text, reply_markup) = keyboards.shinobu_main()
    #кнопка, возвращающая из основного меню с Шинобу в главное меню
    elif btn_data == '1/3':
        (text, reply_markup) = keyboards.main_menu(chat_id)
    return text, reply_markup

#ветка кнопок с музыкой
def music(bot, chat_id, btn_data):
    text = ''
    reply_markup = types.InlineKeyboardMarkup()

    #кнопка, открывающая меню со всеми исполнителями, сгруппированных по первому символу
    if btn_data == '2':
        (text, reply_markup) = keyboards.music_abc()
    #кнопка, открывающая меню с исполнителями, которые начинаются с одного символа
    elif btn_data.startswith('2/1'):
        (text, reply_markup) = keyboards.music_performers(btn_data)
    #кнопка, открывающая меню с альбомами исполнителя
    elif btn_data.startswith('2/2'):
        (text, reply_markup) = keyboards.music_albums(btn_data)
    #кнопка, открывающая меню с песнями альбома
    elif btn_data.startswith('2/3'):
        (text, reply_markup) = keyboards.music_songs_in_album(btn_data)
    #кнопка, открывающая последнее меню, которое отправляет песню и предлагает вернуться назад
    elif btn_data.startswith('2/4'):
        full_song_path = queries_to_bd.get_song_path(btn_data)
        file_size = (os.stat(full_song_path)).st_size / (1024 * 1024)
        flag_success_size = -1
        if file_size < 50:
            flag_success_size = 1
            bot.send_audio(chat_id, audio=open(full_song_path, 'rb'))
        else:
            flag_success_size = 0
        (text, reply_markup) = keyboards.music_menu_last(flag_success_size, btn_data)
    #кнопка, возвращающая на меню с песнями альбома
    elif btn_data.startswith("2/back_1/"):
        song_id = btn_data.replace("2/back_1/","")
        album_id = queries_to_bd.get_album_id_by_song_id(song_id)
        (text, reply_markup) = keyboards.music_songs_in_album(album_id)
    #кнопка, возвращающая на меню с альбомами исполнителя
    elif btn_data.startswith("2/back_2/"):
        performer_id = queries_to_bd.get_performer_id_by_album_id(btn_data.replace("2/back_2/",""))
        (text, reply_markup) = keyboards.music_albums(performer_id)
    #кнопка, возвращающая на меню с исполнителями, которые начинаются с одного символа
    elif btn_data.startswith("2/back_3/"):
        performer_id = btn_data.replace("2/back_3/","")
        fist_char_performer_id = queries_to_bd.get_first_char_preformer_id_by_performer_id(performer_id)
        (text, reply_markup) = keyboards.music_performers(fist_char_performer_id)
    #кнопка, возвращающая на меню со всеми исполнителями, сгруппированных по первому символу
    elif btn_data.startswith("2/back_4/"):
        (text, reply_markup) = keyboards.music_abc()
    #кнопка, возвращающая на главное меню
    elif btn_data.startswith("2/back_5/"):
        (text, reply_markup) = keyboards.main_menu(chat_id)

    return text, reply_markup

#ветка кнопок с подписками
def subscriptions(bot, chat_id, btn_data):
    (text, reply_markup) = keyboards.subscriptions_main()
    return text, reply_markup

#ветка кнопок с напоминалками
def notifications(bot, chat_id, btn_data):
    (text, reply_markup) = keyboards.notifications_main()
    return text, reply_markup

#ветка кнопок с шифрованием
def encrypting(bot, chat_id, btn_data):
    (text, reply_markup) = keyboards.encrypting_main()
    return text, reply_markup

#ветка кнопок с изучением японского
def japanese(bot, chat_id, btn_data):
    (text, reply_markup) = keyboards.japanese_main()
    return text, reply_markup

#ветка кнопок с донатом
def donat(bot, chat_id, btn_data):
    (text, reply_markup) = keyboards.donat_main()
    return text, reply_markup

#ветка кнопок с оставшимися полезностями
def something(bot, chat_id, btn_data):
    (text, reply_markup) = keyboards.something_main()
    return text, reply_markup

#ветка кнопок админки
def admin(bot, chat_id, btn_data):
    (text, reply_markup) = keyboards.admin_main()
    return text, reply_markup