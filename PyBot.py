import cleaning_chat
import simple_message_cases
import callback_query_cases
import inline_query_cases
import scheduler
import common_methods
import queries_to_bd
import threading
import inspect
import telebot
import my_cfg
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
    #try:
    
        print(f"Пришло сообщение от: {message.from_user.username}\nТип сообщения: {str(message.content_type)}\nТекст сообщения: {message.text}\n")
        
        #проверяет есть ли такой пользователь (chat_id) в бд
        user_check = queries_to_bd.check_user(message.chat.id)
        
        #проверяет отправлял ли бот этому пользователю сообщения
        msg_check = queries_to_bd.check_msg(message.chat.id)
            
        #проверяет пользователя в бд, если есть-обновляет данные, если нет-добавляет данные
        queries_to_bd.update_user(message)
        
        #если такой пользователь есть, то...
        if user_check > 0 and msg_check > 0:
            
            #подчищаем последнее активное меню
            cleaning_chat.main(MypyBot, message.chat.id)
        
        #сохраняет входящее сообщение
        queries_to_bd.save_simple_message(message)
        
        #уходим в кейсы всевозможных простых сообщений
        simple_message_cases.main(MypyBot, message)
        
    #except Exception as e:
        #print(f'В {str(inspect.stack()[0][3])} произошла ошибка: \n' + str(e))
    
#хэндлер нажатий на кнопки
@MypyBot.callback_query_handler(func=lambda call: True)
def start_callback_query(call):
    #try:
        
        print(f"{call.from_user.username} нажал кнопку {call.data}.\n")
            
        #подчищаем последнее активное меню
        cleaning_chat.main(MypyBot, call.message.chat.id, call.message.message_id)
        
        #сохраняем инфо о нажатой пользователем кнопке
        queries_to_bd.save_callback_query(call)
        
        #уходим в кейсы всевозможных кнопок
        callback_query_cases.case_main(call, MypyBot)
        
    #except Exception as e:
        #print(f'В {str(inspect.stack()[0][3])} произошла ошибка: \n' + str(e))

#хэндлер редактирования сообщений
@MypyBot.edited_message_handler(content_types="text")
def start_edited_message(message):
    #try:
        print(f"Пользователь {message.from_user.username} отредактировал сообщение.\n")
        
        #добавляет новую версию сообщения
        queries_to_bd.insert_new_smiple_message_ver(message)
            
    #except Exception as e:
        #print(f'В {str(inspect.stack()[0][3])} произошла ошибка: \n' + str(e))

#хэндер ивентов инлайн-запросов
@MypyBot.inline_handler(lambda query: len(query.query) > 0)
def start_inline(call):
    #try:
        print(f"{call.from_user.username} сделал inline зарос: {call.query}.\n")

        #метод обработки всех инлайн запросов
        inline_query_cases.main(MypyBot, call)

    #except Exception as e:
        #print(f'В {str(inspect.stack()[0][3])} произошла ошибка: \n' + str(e))
        
#шедулер
def scheduler_main():
    while True:
        #try:
        scheduler.main(MypyBot)
        time.sleep(60)
        #except Exception as e:
            #print(f'В {str(inspect.stack()[0][3])} произошла ошибка: \n' + str(e))

child_thread = threading.Thread(target=scheduler_main)
child_thread.start()
MypyBot.polling(none_stop=True)