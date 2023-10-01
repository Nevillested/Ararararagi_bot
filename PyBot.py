import telebot
import my_cfg
import inspect
import queries_to_bd
import keyboards

MypyBot = telebot.TeleBot(my_cfg.telegram_token, parse_mode = None)

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
        
        #отправляет основное меню
        if message.text.lower() in ["/start","/help","/restart","/menu"]:
            MypyBot.send_message(message.chat.id, 'Меню', reply_markup = keyboards.main_menu())
        else:            
            MypyBot.send_message(message.chat.id, 'Для вызова меню используйте команду /menu')
            
    except Exception as e:
        print(f'В {str(inspect.stack()[0][3])} произошла ошибка: \n' + str(e))

#хэндлер редактирования сообщений
@MypyBot.edited_message_handler(content_types="text")
def catch_edit_msg(message):
    try:
        print(f"Пользователь {message.from_user.username} отредактировал сообщение.\n")
        
        #добавляет новую версию сообщения
        queries_to_bd.insert_new_message_ver(message)
            
    except Exception as e:
        print(f'В {str(inspect.stack()[0][3])} произошла ошибка: \n' + str(e))
    
#хэндлер нажатий на кнопки
@MypyBot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        
        print(f"{call.from_user.username} нажал кнопку {call.data}.\n")
        
    except Exception as e:
        print(f'В {str(inspect.stack()[0][3])} произошла ошибка: \n' + str(e))

MypyBot.polling(none_stop=True)