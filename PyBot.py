import telebot
import my_cfg
import inspect
import queries_to_bd
import keyboards
import callback_query_cases
import common_methods

#на этапе запуска бота подготовим данные для кнопок музыки, тк самой музыки очень много
common_methods.prepare_music_data()

MypyBot = telebot.TeleBot(my_cfg.telegram_token, parse_mode = None)

CONTENT_TYPES = ["text", "audio", "document", "photo", "sticker", "video", "video_note", "voice", "location", "contact",
                 "new_chat_members", "left_chat_member", "new_chat_title", "new_chat_photo", "delete_chat_photo",
                 "group_chat_created", "supergroup_chat_created", "channel_chat_created", "migrate_to_chat_id",
                 "migrate_from_chat_id", "pinned_message"]

#хэндер простых сообщений   
@MypyBot.message_handler(content_types=CONTENT_TYPES)
def start_message(message):
    #try:
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
                
                #...закрывает их
                for msg in msg_list:
                    
                    MypyBot.edit_message_text(chat_id = message.chat.id, message_id = msg, text = 'Потрачено')
                    
                #запоминает в бд, что закрыл их
                queries_to_bd.close_old_opening_menu(message.chat.id, msg_list)
                
            #получает основное меню
            (text_out, reply_markup_out) = keyboards.main_menu(message.chat.id)
            
            #отправляет основное меню
            MypyBot.send_message(message.chat.id, text_out, reply_markup = reply_markup_out, parse_mode = 'MarkdownV2')
            
            #сохраняет данные
            queries_to_bd.save_outcome_data(message.chat.id, message.message_id, 'menu', text_out, 1)
            
        else:
            text_out = '``` Для вызова меню используйте команду /menu ```'
            
            MypyBot.send_message(message.chat.id, text_out, parse_mode = 'MarkdownV2')
            
            #сохраняет данные
            queries_to_bd.save_outcome_data(message.chat.id, message.message_id, 'text', text_out)
            
    #except Exception as e:
        #print(f'В {str(inspect.stack()[0][3])} произошла ошибка: \n' + str(e))

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
    #try:
        
        print(f"{call.from_user.username} нажал кнопку {call.data}.\n")
        
        callback_query_cases.case_main(call, MypyBot)
        
    #except Exception as e:
        #print(f'В {str(inspect.stack()[0][3])} произошла ошибка: \n' + str(e))

MypyBot.polling(none_stop=True)