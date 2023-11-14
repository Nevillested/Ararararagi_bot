import cleaning_chat
import simple_message_cases
import callback_query_cases
import inline_query_cases
import scheduler
import common_methods
import queries_to_bd
import threading
import telebot
import my_cfg
import time
import traceback

#на этапе запуска бота подготовим данные для кнопок музыки, тк самой музыки очень много
common_methods.prepare_music_data()

MypyBot = telebot.TeleBot(my_cfg.telegram_token)

CONTENT_TYPES = ["text", "audio", "document", "photo", "sticker", "video", "video_note", "voice", "location", "contact", "pinned_message"]

@MypyBot.message_handler(content_types=CONTENT_TYPES)
def start_message(message):

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
    queries_to_bd.save_data(message.chat.id, message.message_id, message.content_type, msg_txt = message.text)

    #уходим в кейсы всевозможных простых сообщений
    simple_message_cases.main(MypyBot, message)

#хэндлер нажатий на кнопки
@MypyBot.callback_query_handler(func=lambda call: True)
def start_callback_query(call):

    print(f"{call.from_user.username} нажал кнопку {call.data}.\n")

    #подчищаем последнее активное меню
    cleaning_chat.main(MypyBot, call.message.chat.id, call.message.message_id)

    #сохраняем инфо о нажатой пользователем кнопке
    queries_to_bd.save_data(call.message.chat.id, call.message.message_id, 'button', btn_id = call.data)

    #уходим в кейсы всевозможных кнопок
    callback_query_cases.case_main(call, MypyBot)

#хэндлер редактирования сообщений
@MypyBot.edited_message_handler(content_types="text")
def start_edited_message(message):

    print(f"Пользователь {message.from_user.username} отредактировал сообщение.\n")

    #добавляет новую версию сообщения
    queries_to_bd.insert_new_msg_ver(message)

#хэндер ивентов инлайн-запросов
@MypyBot.inline_handler(lambda query: len(query.query) > 0)
def start_inline(call):

    print(f"{call.from_user.username} сделал inline зарос: {call.query}.\n")

    #метод обработки всех инлайн запросов
    inline_query_cases.main(MypyBot, call)

#шедулер
def scheduler_main():
    while True:
        try:
            scheduler.main(MypyBot)
            time.sleep(60)

        except:

            print('Произошла ошибка, логируемся.')
            queries_to_bd.save_error(str(traceback.format_exc()))
            time.sleep(5)

#запускаем шедулер
child_thread = threading.Thread(target=scheduler_main)

child_thread.start()

#могут быть ошибки связи с сервером, поэтому бот будет перезапускаться каждый раз при ошибках
def start_bot():
    while True:

        #try:
            print('Запуск бота')
            MypyBot.polling()

        #except:

            #print('Произошла ошибка, логируемся.')
            #queries_to_bd.save_error(str(traceback.format_exc()))
            #time.sleep(5)

#запускаем бота
start_bot()