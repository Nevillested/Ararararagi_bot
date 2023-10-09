import telebot
import my_cfg
import inspect
import queries_to_bd
import keyboards
import callback_query_cases
import common_methods
import send_scheduler
import datetime
import threading
import time

#на этапе запуска бота подготовим данные для кнопок музыки, тк самой музыки очень много
common_methods.prepare_music_data()

MypyBot = telebot.TeleBot(my_cfg.telegram_token)

CONTENT_TYPES = ["text", "audio", "document", "photo", "sticker", "video", "video_note", "voice", "location", "contact",
                 "new_chat_members", "left_chat_member", "new_chat_title", "new_chat_photo", "delete_chat_photo",
                 "group_chat_created", "supergroup_chat_created", "channel_chat_created", "migrate_to_chat_id",
                 "migrate_from_chat_id", "pinned_message"]

#хэндер простых сообщений   
@MypyBot.message_handler(content_types=CONTENT_TYPES)
def start_message(message):
    try:
        print(f"Пришло сообщение от: {message.from_user.username}\nТип сообщения: {str(message.content_type)}\nТекст сообщения: {message.text}\n")
            
        #проверяет пользователя в бд, если есть-обновляет данные, если нет-добавляет данные
        queries_to_bd.check_user(message)
        
        #сохраняет входящее сообщение
        queries_to_bd.save_simple_message(message)
        
        if message.text.lower() in ["/start","/help","/menu"]:
            
            #проверяет есть ли уже с пользователем открытое меню
            msg_list = queries_to_bd.get_msg_of_open_menu(message.chat.id)
            
            #если уже есть открытые меню...
            if len(msg_list) != 0:
                
                #проходится по всем msg_id этих меню
                for msg in msg_list:
                    
                    try:
                        #и пытается их удалить
                        MypyBot.delete_message(chat_id = message.chat.id, message_id = msg)
                        
                    except:
                    
                        #может не получится удалить, тк прошло больше 48 часов, в таком случае, редактируем их
                        MypyBot.edit_message_text(chat_id = message.chat.id, message_id = msg, text = 'Потрачено')
                    
                #обновляем, что нет активных меню в текущий момент
                queries_to_bd.close_old_opening_menu(message.chat.id)
                
            #получает основное меню
            (text_out, reply_markup_out) = keyboards.main_menu(message.chat.id)
            
            #отправляет основное меню
            MypyBot.send_message(message.chat.id, text_out, reply_markup = reply_markup_out, parse_mode = 'MarkdownV2')
            
            #сохраняет данные
            queries_to_bd.save_outcome_data(message.chat.id, message.message_id + 1, 'menu', text_out, 1, 0)
            
        else:
            #проверяем, задал ли бот вопрос пользователю, на который он обязательно должен ответить текстом в чате
            flg_need_response = queries_to_bd.check_need_response_flg(message.chat.id)
            
            #если на последнее меню бота нужно обязательно ответить текстовым сообщением, то...
            if flg_need_response == 1:
                
                #проверяем о чем вообще шла речь, для этого заберем ID последней нажатой кнопки и заодно msg_id, в рамках которого будем редачить сообщение
                (what_is_current_context, cur_message_id) = queries_to_bd.get_last_pressed_button(message.chat.id)
                
                current_result_text = ''
                current_reply_markup = telebot.types.InlineKeyboardMarkup()
                current_parsemod = ''
                
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
                        
                        
                #чтобы у нас меню всегда оставалось внизу, надо удалить старое меню
                MypyBot.delete_message(chat_id = message.chat.id, message_id = cur_message_id)

                #обновляем, что нет активных меню в текущий момент
                queries_to_bd.close_old_opening_menu(message.chat.id)
    
                #и отправить новое меню
                MypyBot.send_message(message.chat.id, current_result_text, reply_markup = current_reply_markup, parse_mode = current_parsemod)  
                                      
                #сохраняем уходящие данные
                queries_to_bd.save_outcome_data(message.chat.id, cur_message_id + 1, 'button text', current_result_text, 1, 0)
                
            #иначе заглушка
            else:
                
                current_result_text = '``` Для вызова меню используйте команду /menu ```'
                
                MypyBot.send_message(message.chat.id, current_result_text , parse_mode = 'MarkdownV2')
                
                queries_to_bd.save_outcome_data(message.chat.id, message.message_id + 1, 'text', current_result_text, 0, 0)
            
    except Exception as e:
        print(f'В {str(inspect.stack()[0][3])} произошла ошибка: \n' + str(e))

#хэндлер редактирования сообщений
@MypyBot.edited_message_handler(content_types="text")
def catch_edit_msg(message):
    try:
        print(f"Пользователь {message.from_user.username} отредактировал сообщение.\n")
        
        #добавляет новую версию сообщения
        queries_to_bd.insert_new_smiple_message_ver(message)
            
    except Exception as e:
        print(f'В {str(inspect.stack()[0][3])} произошла ошибка: \n' + str(e))
    
#хэндлер нажатий на кнопки
@MypyBot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        
        print(f"{call.from_user.username} нажал кнопку {call.data}.\n")
        
        #сохраняем инфо о нажатой пользователем кнопке
        queries_to_bd.save_callback_query(call)
        
        #уходим в кейсы всевозможных кнопок
        callback_query_cases.case_main(call, MypyBot)
        
    except Exception as e:
        print(f'В {str(inspect.stack()[0][3])} произошла ошибка: \n' + str(e))

#шедулер
def scheduler():
    while True:
        try:
            send_scheduler.main(MypyBot)
            time.sleep(60)
        except Exception as e:
            print(f'В {str(inspect.stack()[0][3])} произошла ошибка: \n' + str(e))

child_thread = threading.Thread(target=scheduler)
child_thread.start()
MypyBot.polling(none_stop=True)