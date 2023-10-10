import sending
import queries_to_bd
import keyboards
import telebot

#основной метод проверки входящих сообщений
def main(bot, message):

    text_data = ()
    current_result_text = None
    current_reply_markup = telebot.types.InlineKeyboardMarkup()
    current_parsemod = None

    #проверяем, задал ли бот вопрос пользователю, на который он обязательно должен ответить текстом в чате
    flg_need_response = queries_to_bd.check_need_response_flg(message.chat.id)

    #если бот ждем ответа от пользователя в виде текстового сообщения, то
    if flg_need_response == 1:

        #проверяем о чем вообще шла речь, для этого заберем ID последней нажатой кнопки и заодно msg_id, в рамках которого будем редачить сообщение
        (what_is_current_context, cur_message_id) = queries_to_bd.get_last_pressed_button(message.chat.id)


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

        #если последняя нажатая кнопка относится к меню с ID = 6, то это изучение японского. В японском может быть только 2 варианта ввода текста - это поиск слова в моем личном словаре и с в словаре warudai
        elif what_is_current_context.startswith("6"):

            #поиск по моему словарю
            if what_is_current_context.startswith("6/2/"):

                kanji_search = None
                kana_search = None
                rus_search = None

                #получаем id типа поиска. 1 = по кадзи, 2 = по кане, 3 = по русскому переводу
                search_id = (what_is_current_context.split('/'))[-1]

                if search_id == '1':
                    kanji_search = message.text
                elif search_id == '2':
                    kana_search = message.text
                elif search_id == '3':
                    rus_search = message.text

                #отправляем на поиск перевода
                (current_result_text, current_reply_markup) = keyboards.japanese_my_dict_translate(kanji_search, kana_search, rus_search)

            #поиск по словарю warodai
            elif what_is_current_context.startswith("6/3/"):

                jap_text = None
                rus_text = None

                #получаем id типа поиска. 1 = по японской писанине, 3 = по русской писанине
                search_id = (what_is_current_context.split('/'))[-1]

                if search_id == '1':
                    jap_text = message.text
                elif search_id == '2':
                    rus_text = message.text

                #отправляем на поиск перевода
                (current_result_text, current_reply_markup) = keyboards.japanese_warodai_dict_translate(jap_text, rus_text)



    #в противном случае, бот не ждет ответа от пользователя в виде сообщения и поэтому отдает по умолчанию основную клавиатуру
    else:

        #получает данные основной клавиатуры
        (current_result_text, current_reply_markup) = keyboards.main_menu(message.chat.id)


    #собираем текстовые данные
    text_data = (current_result_text, current_reply_markup, current_parsemod, 0)

    #отправляем все в единый метод отправки
    sending.main(bot, message.chat.id, message.message_id, text_data = text_data)