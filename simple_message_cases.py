import sending
import queries_to_bd
import keyboards
import telebot
import common_methods

#основной метод проверки входящих сообщений
def main(bot, message):

    text_data = None
    audio_data = None
    document_data = None
    current_result_text = None
    current_reply_markup = telebot.types.InlineKeyboardMarkup()
    current_parsemod = None
    photo_data = None
    poll_data = None
    invoice_data = None
    sticker_data = None

    #проверяем, задал ли бот вопрос пользователю, на который он обязательно должен ответить текстом в чате
    flg_need_response = queries_to_bd.check_need_response_flg(message.chat.id)

    #если бот ждет ответа от пользователя в виде текстового сообщения, то
    if flg_need_response == 1:

        #проверяем о чем вообще шла речь, для этого заберем ID последней нажатой кнопки и заодно msg_id, в рамках которого будем редачить сообщение
        what_is_current_context = queries_to_bd.get_last_pressed_button(message.chat.id)

        #проверка, что пользователь прислал текст
        if message.content_type == 'text':

            #если последняя нажатая кнопка относится к меню с ID = 4, то это напоминалки. В напоминалках только в 1 месте требуется, чтобы пользователь дал ответ текстом - это при вводе информации, что же нужно напомнить
            if what_is_current_context.startswith("4"):

                #создает в таблице запись о напоминалке
                queries_to_bd.create_new_notification(message.chat.id, message.text)

                #забирает ID созданной записи (напоминалки)
                notification_id = queries_to_bd.get_last_notification_id(message.chat.id)

                #забираем клавиатуру для редактирования напоминалки
                (current_result_text, current_reply_markup) = keyboards.notification_edit(notification_id)

            #если последняя нажатая кнопка относится к меню с ID = 5, то это шифрование/дешифрование
            elif what_is_current_context.startswith("5"):

                #вытаскиваем тип операции
                operation_type = (what_is_current_context.split('/'))[-1]

                #вытаскиваем язык
                lang_code = (what_is_current_context.split('/'))[-2]

                #вытаскиваем ключ
                key = (what_is_current_context.split('/'))[-3]

                #отправляем на шифровку/дешифровку
                (current_result_text, current_reply_markup) = keyboards.crypting_result(operation_type, lang_code, key, message.text)

                current_parsemod = 'MarkdownV2'

            #текстовые данные ожидаются от пользователя по ветке 8 только в случае преобразования текста в войс
            elif what_is_current_context in ["8/1/1", "8/2/1"]:

                #вытаскиваем язык. 1 - русский, 2 - английский
                lang_code = (what_is_current_context.split('/'))[-2]

                #получаем путь, по которому лежит аудиофайл
                audio_data = common_methods.convert_text_to_speech(str(message.chat.id), message.text, lang_code)

                #получает последнее меню по ветке распознавания войса в текст
                (current_result_text, current_reply_markup) = keyboards.text_speech_result_voice(message.text, lang_code)

            #текстовые данные ожидаются от пользователя по ветке 9/2 только в случае получения названия города для погоды
            elif what_is_current_context == "9/2":

                #получает последнее меню по ветке распознавания войса в текст
                (current_result_text, current_reply_markup) = keyboards.weather_last_menu(message.text)

            #текстовые данные ожидаются от пользователя по ветке 9/3 только в случае получения текста, который будем помещен в QR-код
            elif what_is_current_context == "9/3":

                #получает последнее меню по ветке распознавания войса в текст
                (current_result_text, current_reply_markup) = keyboards.qr_code_result(message.text)

                document_data = common_methods.create_qr_code(message.text, str(message.chat.id))

            #текстовые данные ожидаются от пользователя по ветке 9/4 только в случае получения от пользователя тегов, по которым будем искать пикчу на реакторе
            elif what_is_current_context == "9/4":

                #получает последнее меню по ветке получения пикчи по тегу
                (current_result_text, current_reply_markup) = keyboards.get_pic_by_teg_result()

                #получает адрес изображения, спойлер и подпись к нему
                photo_data = common_methods.get_pic_by_teg(message.text)

            #если тип контента не подходит ни к одному из вариантов, которые ждет бот - сообщаем юзеру об этом
            else:
                current_result_text = 'Ты прислал не тот тип контента который нужен. Поздравляю тебя, начинай заново\n/menu'

        #проверка, что пользователь прислал войс
        elif message.content_type == 'voice':

            #если последняя нажатая кнопка относится к меню с ID = 8, то это это преобразование войса в текст. Либо на русском языке, либо на английском другого не дано
            if what_is_current_context in ["8/1/2", "8/2/2"]:

                #вытаскиваем язык. 1 - русский, 2 - английский
                lang_code = (what_is_current_context.split('/'))[-2]

                #получаем инфо о войсе
                file_info = bot.get_file(message.voice.file_id)

                #скачиваем войс
                downloaded_file = bot.download_file(file_info.file_path)

                file_path = 'assets/temp/convert_speech_to_text/' + str(message.chat.id)  +'.ogg'

                #записываем войс на диск
                with open(file_path, 'wb') as new_file:
                    new_file.write(downloaded_file)

                #отправляем на преобразование в текст и получаем результат
                text = common_methods.convert_speech_to_text(lang_code, file_path)

                #получает последнее меню по ветке распознавания войса в текст
                (current_result_text, current_reply_markup) = keyboards.text_speech_result_text(text, lang_code)

            #если тип контента не подходит ни к одному из вариантов, которые ждет бот - сообщаем юзеру об этом
            else:
                current_result_text = 'Ты прислал не тот тип контента который нужен. Поздравляю тебя умник, начинай заново\n/menu'

    #в противном случае, бот не ждет ответа от пользователя в виде сообщения и поэтому отдает по умолчанию основную клавиатуру
    else:

        #получает данные основной клавиатуры
        (current_result_text, current_reply_markup) = keyboards.main_menu(message.chat.id)


    #собираем текстовые данные
    text_data = (current_result_text, current_reply_markup, current_parsemod, 0, 1)

    #отправляем все в единый метод отправки
    sending.main(bot, message.chat.id, text_data, photo_data, poll_data, audio_data, invoice_data, sticker_data, document_data)