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
import sending
import simple_message_cases

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
        
        #уходим в кейсы всевозможных простых сообщений
        simple_message_cases.main(MypyBot, message)
        
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

#хэндлер редактирования сообщений
@MypyBot.edited_message_handler(content_types="text")
def catch_edit_msg(message):
    try:
        print(f"Пользователь {message.from_user.username} отредактировал сообщение.\n")
        
        #добавляет новую версию сообщения
        queries_to_bd.insert_new_smiple_message_ver(message)
            
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