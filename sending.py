import queries_to_bd

#это метод, через который мы будем отправлять все сообщения. Слишком много отправок разбросано по файлам, поэтому унифицируем это дело
def main(bot, chat_id, msg_id, text_data = None, photo_data = None, poll_data = None, audio_data = None, invoice_data = None, sticker_data = None, document_data = None):

    ####################### блок сброса меню в чате с пользователем #######################

    #проверяем есть ли с чатом открытые менюхи
    msg_list = queries_to_bd.get_msg_of_open_menu(chat_id)

    #если уже есть открытые меню...
    if len(msg_list) != 0:

        #проходится по всем msg_id этих меню
        for msg in msg_list:

            try:
                #и пытается их удалить
                bot.delete_message(chat_id = chat_id, message_id = msg)

            except:

                try:
                    #может не получится удалить, тк прошло больше 48 часов, в таком случае, редактируем их
                    bot.edit_message_text(chat_id = chat_id, message_id = msg, text = 'Потрачено')

                except:
                    print('Не удалось удалить или отредактировать msg_id: ' + str(msg) + ' chat_id: ' + str(chat_id))

    #обновляем, что нет активных меню в текущий момент
    queries_to_bd.close_old_opening_menu(chat_id)

    ####################### блок отправки #######################

    #задаем по умолчанию
    msg_id_outcome = msg_id

    #отправка стикера
    if sticker_data != None:

        #отправляем стикер
        bot.send_sticker(chat_id, sticker = open(sticker_data, "rb"))

        #инкрементируем msg_id, тк мы только что отправли msg
        msg_id_outcome += 1

        #сохраняем, что отправили
        queries_to_bd.save_outcome_data(chat_id, msg_id_outcome, 'sticker', sticker_data, 0, 0)

    #отправка фото
    if photo_data != None:

        #вытаскиваем данные
        photo_url = photo_data[0]
        photo_spoiler = photo_data[1]
        photo_caption = photo_data[2]
        photo_parse_mode = photo_data[3]

        #отправляем фото
        bot.send_photo(chat_id, photo = photo_url, has_spoiler = photo_spoiler, caption = photo_caption, parse_mode = photo_parse_mode)

        #инкрементируем msg_id, тк мы только что отправли msg
        msg_id_outcome += 1

        #сохраняем, что отправили
        queries_to_bd.save_outcome_data(chat_id, msg_id_outcome, 'photo', photo_url, 0, 0)

    #отправка музыки
    if audio_data != None:

        #отправляем сообщение, чтобы подождал мальца, тк файл весит много
        bot.send_message(chat_id, 'Сейчас прилетит, погоди')

        #инкрементируем msg_id, тк мы только что отправли msg
        msg_id_outcome += 1

        #сохраняем, что отправили
        queries_to_bd.save_outcome_data(chat_id, msg_id_outcome, 'text', 'Сейчас прилетит, погоди', 0, 0)

        #отправляем аудио-файл
        bot.send_audio(chat_id, audio=open(audio_data, 'rb'))

        #инкрементируем msg_id, тк мы только что отправли msg
        msg_id_outcome += 1

        #сохраняем, что отправили
        queries_to_bd.save_outcome_data(chat_id, msg_id_outcome, 'audio', audio_data, 0, 0)

    #отправка квиза
    if poll_data != None:

        #вытаскиваем данные
        poll_text = poll_data[0]
        poll_options = poll_data[1]
        poll_correct_option_id = poll_data[2]

        #отправляем квиз
        bot.send_poll(chat_id, poll_text, options = poll_options, correct_option_id  = poll_correct_option_id, type = 'quiz')

        #инкрементируем msg_id, тк мы только что отправли msg
        msg_id_outcome += 1

        #сохраняем, что отправили
        queries_to_bd.save_outcome_data(chat_id, msg_id_outcome, 'poll', poll_text, 0, 0)

    #отправка инвойсов на оплату
    if invoice_data != None:

        #отправляет данные для платежа
        bot.send_invoice(chat_id                = invoice_data[0],
                         title                  = invoice_data[1],
                         description            = invoice_data[2],
                         invoice_payload        = invoice_data[3],
                         provider_token         = invoice_data[4],
                         currency               = invoice_data[5],
                         prices                 = invoice_data[6],
                         photo_url              = invoice_data[7],
                         photo_height           = invoice_data[8],
                         photo_width            = invoice_data[9],
                         photo_size             = invoice_data[10],
                         is_flexible            = invoice_data[11],
                         start_parameter        = invoice_data[12],
                         max_tip_amount         = invoice_data[13],
                         suggested_tip_amounts  = invoice_data[14],
                         need_email             = invoice_data[15],
                         send_email_to_provider = invoice_data[16],
                         provider_data          = invoice_data[17])


        #инкрементируем msg_id, тк мы только что отправли msg
        msg_id_outcome += 1

        #сохраняем, что отправили
        queries_to_bd.save_outcome_data(chat_id, msg_id_outcome, 'invoice', invoice_data[1], 0, 0)

    #отправка документов
    if document_data != None:

        #оптравляем документ
        bot.send_document(chat_id, document = open(document_data, 'rb'))

        #инкрементируем msg_id, тк мы только что отправли msg
        msg_id_outcome += 1

        #сохраняем, что отправили
        queries_to_bd.save_outcome_data(chat_id, msg_id_outcome, 'menu', document_data, 0, 0)

    #отправка обычного текста
    if text_data != None:

        #вытаскиваем данные
        text_out = text_data[0]
        reply_markup_out = text_data[1]
        parse_mode_out = text_data[2]
        flg_need_response_out = text_data[3]

        #отправляем текст
        bot.send_message(chat_id, text_out, reply_markup = reply_markup_out, parse_mode = parse_mode_out)

        #инкрементируем msg_id, тк мы только что отправли msg
        msg_id_outcome += 1

        #сохраняем, что отправили
        queries_to_bd.save_outcome_data(chat_id, msg_id_outcome, 'menu', text_out, 1, flg_need_response_out)





