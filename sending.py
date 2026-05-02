import queries_to_bd
import common_methods
from telebot.apihelper import ApiTelegramException

#это метод, через который мы будем отправлять все сообщения. Слишком много отправок разбросано по файлам, поэтому унифицируем это дело
def main(bot, chat_id, text_data = None, photo_data = None, poll_data = None, audio_data = None, invoice_data = None, sticker_data = None, document_data = None):

    #задаем по умолчанию
    msg_id_outcome = queries_to_bd.get_last_msg_id()

    l_flg_sent = 0

    #отправка стикера
    if sticker_data != None:

        #отправляем стикер (пробуем отправить - вдруг мы в блоке)
        try:
            bot.send_sticker(chat_id, sticker = open(sticker_data, "rb"))
            l_flg_sent = 1
        except:
            l_flg_sent = 0

        if l_flg_sent == 1:
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

        #отправляем фото (пробуем отправить - вдруг мы в блоке)
        try:
            bot.send_photo(chat_id, photo = photo_url, has_spoiler = photo_spoiler, caption = photo_caption, parse_mode = photo_parse_mode)
            l_flg_sent = 1
        except:
            l_flg_sent = 0

        if l_flg_sent == 1:
            #инкрементируем msg_id, тк мы только что отправли msg
            msg_id_outcome += 1

            #сохраняем, что отправили
            queries_to_bd.save_outcome_data(chat_id, msg_id_outcome, 'photo', photo_url, 0, 0)

    #отправка музыки
    if audio_data != None:

        #ловля ошибок, вдруг бот в блоке
        try:
            #отправляем сообщение, чтобы подождал мальца, тк иногад файл весит много
            msg_txt = 'Сейчас прилетит, погоди'

            bot.send_message(chat_id, msg_txt)

            #инкрементируем msg_id, тк мы только что отправли msg
            msg_id_outcome += 1

            #сохраняем, что отправили
            queries_to_bd.save_outcome_data(chat_id, msg_id_outcome, 'text', msg_txt, 0, 0)
        except:
            None

        #вытаскиваем тип аудио
        audio_type = audio_data[0]

        #вытаскиваем директорию аудио
        audio_path = audio_data[1]

        #если это войс, то...
        if audio_type == 'voice':

            #ловля ошибок, вдруг бот в блоке
            try:

                #пытаемся отправить войс, но по настройкам приватности, они могут быть запрещены у пользователя
                try:

                    bot.send_voice(chat_id, open(audio_path, 'rb'))
                    
                    msg_type = 'audio voice'

                    msg_txt = audio_path

                except ApiTelegramException as e:

                    msg_type = 'text'

                    if "VOICE_MESSAGES_FORBIDDEN" in e.result_json.get("description", ""):

                        msg_txt = "Вам запрещены голосовые сообщения 😔"

                        bot.send_message(chat_id, msg_txt)

                    else:

                        msg_txt = "Что-то пошло не так. Я пока не понял, но пойму."

                        bot.send_message(chat_id, msg_txt)

                msg_id_outcome += 1

                queries_to_bd.save_outcome_data(chat_id, msg_id_outcome, msg_type, msg_txt, 0, 0)

            except:
                None

        #если это песня, то...
        if audio_type == 'song':

            audio_tg_file_id = audio_data[2]
            audio_performer = audio_data[3]
            audio_album = audio_data[4]
            audio_song = audio_data[5]

            #Сначала попробуем отправить по file_id:
            if audio_tg_file_id != None:

                #ловля ошибок, если вдруг бот в блоке
                try:
                    #отправляем через метод send_audio...
                    bot.send_audio(chat_id, audio_tg_file_id)

                    #инкрементируем msg_id, тк мы только что отправли msg
                    msg_id_outcome += 1

                    #сохраняем, что отправили
                    queries_to_bd.save_outcome_data(chat_id, msg_id_outcome, 'audio voice', audio_path, 0, 0)

                except:
                    None

            #если file_id еще нету, создадим его
            else:

                #ловля ошибок, если вдруг бот в блоке
                try:

                    #сначала попробуем отправить методом send_audio
                    try:

                        audio_duration = common_methods.get_duration_song(audio_path)
    
                        with open(audio_path, "rb") as f:
                            msg = bot.send_audio(chat_id, f, title = audio_song, performer = audio_performer, duration = audio_duration, timeout = 300)
    
                        tg_file_id = msg.audio.file_id

                    #методом send_audio не всегда получается, поэтому в исключительных случаях - пробуем через send_document
                    except:

                        with open(audio_path, 'rb') as f:
                            msg = bot.send_document(chat_id, document=f, timeout = 300)

                        tg_file_id = msg.document.file_id

                    queries_to_bd.update_music_file_id(audio_path, tg_file_id)

                    #инкрементируем msg_id, тк мы только что отправли msg
                    msg_id_outcome += 1

                    #сохраняем, что отправили
                    queries_to_bd.save_outcome_data(chat_id, msg_id_outcome, 'audio voice', audio_path, 0, 0)


                except:
                    None

    #отправка квиза
    if poll_data != None:

        #вытаскиваем данные
        poll_text = poll_data[0]
        poll_options = poll_data[1]
        poll_correct_option_id = poll_data[2]

        #отправляем квиз (пробуем отправить - вдруг мы в блоке)
        try:
            bot.send_poll(chat_id, poll_text, options = poll_options, correct_option_id  = poll_correct_option_id, type = 'quiz')
            l_flg_sent = 1
        except:
            l_flg_sent = 0

        if l_flg_sent == 1:
            #инкрементируем msg_id, тк мы только что отправли msg
            msg_id_outcome += 1

            #сохраняем, что отправили
            queries_to_bd.save_outcome_data(chat_id, msg_id_outcome, 'poll', poll_text, 0, 0)

    #отправка инвойсов на оплату
    if invoice_data != None:

        #отправляет данные для платежа (пробуем отправить - вдруг мы в блоке)
        try:
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
            l_flg_sent = 1
        except:
            l_flg_sent = 0

        if l_flg_sent == 1:
            #инкрементируем msg_id, тк мы только что отправли msg
            msg_id_outcome += 1

            #сохраняем, что отправили
            queries_to_bd.save_outcome_data(chat_id, msg_id_outcome, 'invoice', invoice_data[1], 0, 0)

    #отправка документов
    if document_data != None:

        #отправляем документ (пробуем отправить - вдруг мы в блоке)
        try:
            bot.send_document(chat_id, document = open(document_data, 'rb'))
            l_flg_sent = 1
        except:
            l_flg_sent = 0

        if l_flg_sent == 1:
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
        flg_active_menu_message = text_data[4]

        #отправляем текст (пробуем отправить - вдруг мы в блоке)
        try:
            bot.send_message(chat_id, text_out, reply_markup = reply_markup_out, parse_mode = parse_mode_out)
            l_flg_sent = 1
        except:
            l_flg_sent = 0

        if l_flg_sent == 1:
            #инкрементируем msg_id, тк мы только что отправли msg
            msg_id_outcome += 1

            #сохраняем, что отправили
            queries_to_bd.save_outcome_data(chat_id, msg_id_outcome, 'menu', text_out, flg_active_menu_message, flg_need_response_out)





