from telebot import types
import keyboards
import queries_to_bd
import common_methods
import os
from telebot.types import LabeledPrice
import my_cfg

#точка входа главного меню, корень всех ветвлений
def case_main(call, bot):
    current_btn_name = call.data
    current_chat_id = call.message.chat.id
    msg_id_income = call.message.message_id
    msg_id_outcome = msg_id_income + 1
    current_result_text = ''
    current_reply_markup = types.InlineKeyboardMarkup()
    flg_need_response = 0

    #каждый базовый ID описан в методе создания основной клавиатуры - keyboards.main_menu. Каждая ветка меню раскидана по методам для удобства написания кода. Чтобы тупо не запутаться в if-elif
    if current_btn_name.startswith('1'):
        (current_result_text, current_reply_markup, msg_id_outcome) = shinobu(bot, current_chat_id, msg_id_outcome, current_btn_name)
    elif current_btn_name.startswith('2'):
        (current_result_text, current_reply_markup, msg_id_outcome) = music(bot, current_chat_id, current_btn_name, msg_id_outcome)
    elif current_btn_name.startswith('3'):
        (current_result_text, current_reply_markup) = subscriptions(bot, current_chat_id, current_btn_name)
    elif current_btn_name.startswith('4'):
        (current_result_text, current_reply_markup, flg_need_response) = notifications(bot, current_chat_id, current_btn_name)
    elif current_btn_name.startswith('5'):
        (current_result_text, current_reply_markup, flg_need_response) = crypting(bot, current_chat_id, current_btn_name)
    elif current_btn_name.startswith('6'):
        (current_result_text, current_reply_markup, flg_need_response, msg_id_outcome) = japanese(bot, current_chat_id, current_btn_name, msg_id_outcome)
    elif current_btn_name.startswith('7'):
        (current_result_text, current_reply_markup, msg_id_outcome) = donat(bot, current_chat_id, current_btn_name, msg_id_outcome)
    elif current_btn_name.startswith('8'):
        (current_result_text, current_reply_markup) = something(bot, current_chat_id, current_btn_name)

    #чтобы у нас меню всегда оставалось внизу, пытаемся удалить старое меню (может не получиться, тк прошло 48 часов со с его отправки). Если не получается - просто редактируем его.
    try:
        bot.delete_message(chat_id = current_chat_id, message_id = msg_id_income)
    except:
        bot.edit_message_text(chat_id = current_chat_id, message_id = msg_id_income, text = 'Потрачено')

    #обновляем, что нет активных меню в текущий момент
    queries_to_bd.close_old_opening_menu(current_chat_id)

    #отправляем новое меню
    bot.send_message(current_chat_id, current_result_text, reply_markup = current_reply_markup)

    #сохраняем данные по последнему, новому, отправленному, активному меню.
    queries_to_bd.save_outcome_data(current_chat_id, msg_id_outcome, 'button text', current_result_text, 1, flg_need_response)

    #бесполезное действие, но пусть будет, как напоминание. Если происходит отправка чего-то, например фото, стикера, аудио - неважно. После любой отправки обязательно надо инкрементировать переменную msg_id_outcome
    msg_id_outcome = msg_id_outcome + 1


#ветка кнопок с Шинобу
def shinobu(bot, chat_id, msg_id_outcome, btn_data):
    text = ''
    reply_markup = types.InlineKeyboardMarkup()
    #кнопка, открывающая основное меню Шинобу
    if btn_data == '1':
        (text, reply_markup) = keyboards.shinobu_main()
    #кнопка, открывающая меню с отправкой пикчи с Шинобу
    elif btn_data == '1/1':
        (text, reply_markup) = keyboards.shinobu_pic()
        msg_id_outcome = common_methods.send_shinobu_pic(bot, chat_id, msg_id_outcome)
    #кнопка, заново генерирующая тоже меню, где находится, но меняет текст самого меню (чтобы телеграм не давал ошибку) и отправляющая повторно пикчу
    elif btn_data == '1/1/1':
        (text, reply_markup) = keyboards.shinobu_pic()
        text = queries_to_bd.get_last_bot_text_menu(chat_id)
        msg_id_outcome = common_methods.send_shinobu_pic(bot, chat_id, msg_id_outcome)
    #кнопка, возвращающая на основное меню Шинобу из меню пикчи с Шинобу
    elif btn_data == '1/1/2':
        (text, reply_markup) = keyboards.shinobu_main()
    #кнопка, открывающая меню с отправкой стикера с Шинобу
    elif btn_data == '1/2':
        (text, reply_markup) = keyboards.shinobu_stick()
        msg_id_outcome = common_methods.send_shinobu_stick(bot, chat_id, msg_id_outcome)
    #кнопка, заново генерирующая тоже меню, где находится, но меняет текст самого меню (чтобы телеграм не давал ошибку) и отправляющая повторно стикер
    elif btn_data == '1/2/1':
        (text, reply_markup) = keyboards.shinobu_stick()
        text = queries_to_bd.get_last_bot_text_menu(chat_id)
        msg_id_outcome = common_methods.send_shinobu_stick(bot, chat_id, msg_id_outcome)
    #кнопка, возвращающая на основное меню Шинобу из меню стикера с Шинобу
    elif btn_data == '1/2/2':
        (text, reply_markup) = keyboards.shinobu_main()
    #кнопка, возвращающая из основного меню с Шинобу в главное меню
    elif btn_data == '1/3':
        (text, reply_markup) = keyboards.main_menu(chat_id)
    return text, reply_markup, msg_id_outcome

#ветка кнопок с музыкой
def music(bot, chat_id, btn_data, msg_id_outcome):
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
            queries_to_bd.save_outcome_data(chat_id, msg_id_outcome, 'audio', full_song_path, 0, 0)
            msg_id_outcome = msg_id_outcome + 1
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
    return text, reply_markup, msg_id_outcome

#ветка кнопок с подписками
def subscriptions(bot, chat_id, btn_data):
    text = ''
    reply_markup = types.InlineKeyboardMarkup()
    #кнопка, выдающая главное меню со всеми подписками
    if btn_data == "3":
        (text, reply_markup) = keyboards.subscriptions_main()
    #кнопка, проверяющая есть ли у юзера эта подписка и выдающая ему меню с активацией или дезактивацией этой подписки
    elif btn_data.startswith("3/main_subs_"):
        subscription_id = btn_data.replace("3/main_subs_","")
        active_subs_flg = -1
        #проверяем в бд, подписывался ли пользователь когда-нибудь вообще на эту подписку
        exist_subs_flg = queries_to_bd.check_subs_of_user_by_subs_id(subscription_id, chat_id)
        #если не подписывался никогда еще, то добавляем в таблицу с пользовательскими подписками со статусом 0
        if exist_subs_flg == 0:
            queries_to_bd.add_to_subscriptions(chat_id, subscription_id)
        #проверяем активна ли она сейчас
        active_subs_flg = queries_to_bd.get_status_of_subscription(subscription_id, chat_id)
        #создаем клавиатуру со статусом подписки и предложением отключить ее или включить
        (text, reply_markup) = keyboards.subscriptions_cur_status(active_subs_flg, subscription_id)
    #кнопка выдающая результат включения подписки
    elif btn_data.startswith("3/turn"):
        status = -1
        subscription_id = -1
        if btn_data.startswith("3/turn_on/"):
            subscription_id = btn_data.replace("3/turn_on/","")
            status = 1
        elif btn_data.startswith("3/turn_off/"):
            subscription_id = btn_data.replace("3/turn_off/","")
            status = 0
        #включаем/ выключаем подписку
        queries_to_bd.update_subscription(chat_id, subscription_id, status)
        #отдаем клавиатуру
        (text, reply_markup) = keyboards.subscription_result(status)
    #кнопка, возвращающая в основное меню подписок
    elif btn_data == "3/back_subs":
        (text, reply_markup) = keyboards.subscriptions_main()
    #кнопка, возвращающая в главное меню
    elif btn_data == "3/back_main":
        (text, reply_markup) = keyboards.main_menu(chat_id)
    return text, reply_markup


#ветка кнопок с напоминалками
def notifications(bot, chat_id, btn_data):
    text = ''
    reply_markup = types.InlineKeyboardMarkup()
    flg_need_response = 0

    #кнопка выдающая основное меню напоминалок
    if btn_data == '4':
        (text, reply_markup) = keyboards.notifications_main()
    #ветка с текущими напоминалками
    elif btn_data.startswith("4/1"):
        #кнопка выдающая текущие напоминалки
        if btn_data == '4/1':
            (text, reply_markup) = keyboards.notifications_current(chat_id)
        #кнопка возвращающая в основное меню напоминалок
        elif btn_data == '4/1/back':
            (text, reply_markup) = keyboards.notifications_main()
        #все остальные кнопки - это сами напомоминалки
        else:
            notification_id = (btn_data.split('/'))[-1]
            (text, reply_markup) = keyboards.notification_edit(notification_id)
    #кнопка, выдающая создание новой напоминалки
    elif btn_data == '4/2':
        text = 'Окей, что напомнить?'
        reply_markup = keyboards.create_inline_kb({"Назад" : "4"}, 1)
        flg_need_response = 1
    #меню редактирование напоминалки
    elif btn_data.startswith("4/edit/"):
        notification_id = (btn_data.split('/'))[-1]
        edited_value = (btn_data.split('/'))[-2]
        if edited_value == "year_num":
            (text, reply_markup) = keyboards.notif_years(notification_id)
        elif edited_value == "month_num":
            (text, reply_markup) = keyboards.notif_months(notification_id)
        elif edited_value == "day_num":
            (text, reply_markup) = keyboards.notif_days(notification_id)
        elif edited_value == "hour_num":
            (text, reply_markup) = keyboards.notif_hours(notification_id)
        elif edited_value == "min_num":
            (text, reply_markup) = keyboards.notif_minutes(notification_id)
        elif edited_value == "repeat_interval":
            (text, reply_markup) = keyboards.notif_repeat_interval(notification_id)
        elif edited_value == "activity":
            (text, reply_markup) = keyboards.notif_turn_on_off(notification_id)
    #ветка с установлением ключевых знаечний напоминалки
    elif btn_data.startswith("4/set/"):
        notification_id = (btn_data.split('/'))[-1]
        target_value = (btn_data.split('/'))[-2]
        target_field = (btn_data.split('/'))[-3]
        repeat_flag = None
        if target_field == "year_num":
            text = 'Год установлен'
        elif target_field == "month_num":
            text = 'Месяц установлен'
        elif target_field == "day_num":
            text = 'День установлен'
        elif target_field == "hour_num":
            text = 'Час установлен'
        elif target_field == "minute_num":
            text = 'Минута установлена'
        elif target_field in ["every_year_flg", "every_month_flg", "every_week_flg", "every_day_flg", "every_hour_flg", "every_minute_flg", "repeat_flg"]:
            queries_to_bd.notification_reset_repeat(notification_id)
            text = 'Периодичность установлена'
            if target_field == "repeat_flg":
                repeat_flag = 0
            else:
                repeat_flag = 1
        elif target_field == "activity_flg":
            if target_value == '1':
                text = 'Включено'
            elif target_value == '0':
                text = 'Отключено'
        reply_markup = keyboards.create_inline_kb({"Назад" : "4/1/" + notification_id}, 1)
        queries_to_bd.update_notfications(notification_id, target_field, target_value, repeat_flag)
    #кнопка, возвращающая в главное меню
    elif btn_data == '4/3':
        (text, reply_markup) = keyboards.main_menu(chat_id)
    return text, reply_markup, flg_need_response

#ветка кнопок с шифрованием
def crypting(bot, chat_id, btn_data):
    flg_need_response = 0
    text = ''
    reply_markup = types.InlineKeyboardMarkup()
    #кнопка, возвращающая выбор языка
    if btn_data == '5':
        (text, reply_markup) = keyboards.crypting_lang()
    #кнопка, возвращающая на главное меню
    elif btn_data == '5/back/0':
        (text, reply_markup) = keyboards.main_menu(chat_id)
    #кнопка, возвращающая на выбор языка
    elif btn_data == '5/back/1':
        (text, reply_markup) = keyboards.crypting_lang()
    #кнопка, возвращающая тип операции
    elif btn_data.startswith("5/1/") or btn_data.startswith("5/back/2/"):
        lang_code = (btn_data.split('/'))[-1]
        (text, reply_markup) = keyboards.crypting_operation(lang_code)
    #кнопка, возвращающая ключ сдвига
    elif btn_data.startswith("5/2/"):
        operation_type = (btn_data.split('/'))[-1]
        lang_code = (btn_data.split('/'))[-2]
        (text, reply_markup) = keyboards.crypting_key(lang_code, operation_type)
    #кнопка, возвращающая предложение пользователю ввести текст
    elif btn_data.startswith("5/3/"):
        flg_need_response = 1
        operation_type = (btn_data.split('/'))[-1]
        lang_code = (btn_data.split('/'))[-2]
        (text, reply_markup) = keyboards.crypting_text(lang_code, operation_type)
    return text, reply_markup, flg_need_response


#ветка кнопок с изучением японского
def japanese(bot, chat_id, btn_data, msg_id_outcome):
    flg_need_response = 0
    text = ''
    reply_markup = types.InlineKeyboardMarkup()
    #кнопка, возвращающая основное меню по изучению Японского
    if btn_data == '6':
        (text, reply_markup) = keyboards.japanese_main()
    #кнопка возвращающая в главное меню
    elif btn_data == '6/back/0':
        (text, reply_markup) = keyboards.main_menu(chat_id)
    #кнопка возвращающая в основное меню по изучению Японского
    elif btn_data == '6/back/1':
        (text, reply_markup) = keyboards.japanese_main()
    #кнопка, возвращающая на выбор меню с квизами по кандзи - по номеру урока или все кандзи
    elif btn_data == '6/back/2':
        (text, reply_markup) = keyboards.japanese_kanji_quiz_main()
    #кнопка, возвращающая на выбор номера десятка кандзи
    elif btn_data == '6/back/3':
        (text, reply_markup) = keyboards.japanese_kanji_quiz_certain()
    #меню с квизами по кандзи
    elif btn_data == '6/1':
        (text, reply_markup) = keyboards.japanese_kanji_quiz_main()
    #меню с квизами по кандзи по номеру десятка
    elif btn_data == '6/1/1':
        (text, reply_markup) = keyboards.japanese_kanji_quiz_certain()
    #кнпока, по нажатии после которой бот выдает квиз и спрашивает, нужно ли еще
    elif btn_data.startswith('6/1/1/'):
        decade_number = (btn_data.split('/'))[-1]
        (text, reply_markup) = keyboards.last_japanese_menu_by_certain_kani(decade_number)
        msg_id_outcome = common_methods.send_kanji_quiz_by(bot, chat_id, decade_number, msg_id_outcome)
    #Квиз со всеми имеющимися кандзи
    elif btn_data == '6/1/2':
        (text, reply_markup) = keyboards.last_japanese_menu_by_full_kani()
        msg_id_outcome = common_methods.send_kanji_quiz_by(bot, chat_id, None, msg_id_outcome)
    #кнпока "еще" - квиз со всеми имеющимися кандзи
    elif btn_data == '6/1/2/1':
        (text, reply_markup) = keyboards.last_japanese_menu_by_full_kani()
        text = queries_to_bd.get_last_bot_text_menu(chat_id)
        msg_id_outcome = common_methods.send_kanji_quiz_by(bot, chat_id, None, msg_id_outcome)
    #кнопка "еще" после получения квиза с кандзи по номеру определенного десятка
    elif btn_data.startswith('6/1/3/'):
        decade_number = (btn_data.split('/'))[-1]
        (text, reply_markup) = keyboards.last_japanese_menu_by_certain_kani(decade_number)
        text = queries_to_bd.get_last_bot_text_menu(chat_id)
        msg_id_outcome = common_methods.send_kanji_quiz_by(bot, chat_id, decade_number, msg_id_outcome)
    #меню с словарем пройденных слов
    elif btn_data == '6/2':
        (text, reply_markup) = keyboards.japanese_my_dict()
    #Ищем в нашем словаре слова
    elif btn_data == '6/2/1' or btn_data == '6/2/2' or btn_data == '6/2/3':
        flg_need_response = 1
        (text, reply_markup) = keyboards.japanese_search_in_my_dict()
    #меню с словарем warodai
    elif btn_data == '6/3':
        (text, reply_markup) = keyboards.japanese_warodai_dict()
    #Ищем словаре warodai слова
    elif btn_data == '6/3/1' or btn_data == '6/3/2':
        flg_need_response = 1
        (text, reply_markup) = keyboards.japanese_search_in_warodai_dict()
    return text, reply_markup, flg_need_response, msg_id_outcome

#ветка кнопок с донатом
def donat(bot, chat_id, btn_data, msg_id_outcome):
    text = ''
    reply_markup = types.InlineKeyboardMarkup()

    #основное меню доната
    if btn_data == "7":
        (text, reply_markup) = keyboards.donat_main()
    #возвращает в главное меню
    elif btn_data == "7/back/0":
        (text, reply_markup) = keyboards.main_menu(chat_id)

    #кнопка, возвращающая инвойс
    elif btn_data in ["7/1","7/2","7/3","7/4"]:
        (text, reply_markup) = keyboards.donat_invoice()

        title_out = ''
        description_out = ''
        photo_url_out = ''
        prices_out = -1

        title_out = None
        description_out = None
        invoice_payload_out = 'Shut up and take my money!'
        currency_out = 'RUB'
        prices_out = None
        photo_url_out = None
        start_parameter_out = 'payment_start'
        max_tip_amount_out = None
        suggested_tip_amounts_out = None

        if btn_data == "7/1":
            title_out = 'owner = one love'
            description_out = 'Потому что я такой хорошенький'
            photo_url_out = None #'https://i.ibb.co/H7Zv0qp/1.jpg'
            prices_out = 10000

        elif btn_data == "7/2":
            title_out = 'Денег нет, но ты держись'
            description_out = 'Не помирай плз, держи 150р'
            photo_url_out = None #'https://i.ibb.co/DrR4mpk/2.jpg'
            prices_out = 15000

        elif btn_data == "7/3":
            title_out = 'Бот - это святое'
            description_out = 'Ты только представь свою жизнь без этого бота. Ага, и я о том же, расчехляй кошель'
            photo_url_out = None #'https://i.ibb.co/6v1DT1d/3.jpg'
            prices_out = 20000

        elif btn_data == "7/4":
            title_out = 'ka-ka'
            description_out = 'Шинобу - лучшая девочка, ты это понимаешь?\nПоэтому давай, расчехляй свой кошель и без лишних вопросов скидывайся на кошерные фигурки.\nВсе скидываются, и ты скидывайся, давай, не ломайся\n(тут могла быть ваша пассивно-агрессивная реклама)'
            photo_url_out = None #'https://i.ibb.co/3vqH491/ga4wtboduxm-0-Rf5-U-1-1.jpg'#'https://i.ibb.co/pbQLhks/123123-0-Rf5-U.jpg'
            prices_out = 100000

        #отправляет данные для платежа
        bot.send_invoice(chat_id               = chat_id,
                         title                 = title_out,
                         description           = description_out,
                         invoice_payload       = 'Shut up and take my money!',
                         provider_token        = my_cfg.provider_token,
                         currency              = 'RUB',
                         prices                = [LabeledPrice(label='Выворачивай карманы, к оплате: ', amount= prices_out )],
                         photo_url             = photo_url_out,
                         photo_height          = 512,
                         photo_width           = 512,
                         photo_size            = 512,
                         is_flexible           = False,
                         start_parameter       = 'payment_start',
                         max_tip_amount        = None,
                         suggested_tip_amounts = None,
                         need_email            = True,
                         send_email_to_provider= True,
                         provider_data         = '''{
                                                     "receipt": {"customer": {"email": "ararararagi.payments@gmail.com"},
                                                                 "items": [
                                                                           {"description": "'''+description_out+'''",
                                                                            "quantity": "1",
                                                                            "amount": {"value": "'''+str(prices_out/100)+'''", "currency": "'''+currency_out+'''"},
                                                                            "vat_code": "1"}
                                                                          ]
                                                             }
                                                    }'''
                        )

        #сохраняем ушедшую инфу
        queries_to_bd.save_outcome_data(chat_id, msg_id_outcome, 'invoice', description_out, 0, 0)

        #инкрементируем обязательно msg_id
        msg_id_outcome = msg_id_outcome + 1

    return text, reply_markup, msg_id_outcome

#ветка кнопок с оставшимися полезностями
def something(bot, chat_id, btn_data):
    (text, reply_markup) = keyboards.something_main()
    return text, reply_markup