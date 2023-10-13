import queries_to_bd
import traceback
import queries_to_bd

#это метод, спецаильно созданный, чтобы быстро подчищать старое менюшки. Так как по некоторым кейсам в меню может происходить долго операция (например отправка фото, 4-5 сек), то
#чтобы пользователь не кликал несколько раз по кнопке и не забивал очередь в телеге, то сразу же после события - нажатия кнопки или присланного какого-то сообщения, мы сразу же удаляем
#прошлую информацию.
def main(bot, chat_id, msg_id = None):

    chat_id = str(chat_id)
    last_msg_id = None
    array_msg_id = []

    if msg_id == None:

        #получает msg_id последнего отправленного ему сообщения с меню
        array_msg_id = queries_to_bd.get_menu_msg_id(chat_id)

    else:
        array_msg_id.append(msg_id)

    #если есть какие-то активные меню, то...

    if len(array_msg_id) != 0:

        for msg in array_msg_id:

            if msg != -1:
                try:
                    #...пытается их удалить
                    bot.delete_message(chat_id = chat_id, message_id = msg)
                    queries_to_bd.set_msg_menu_as_inactive(msg)

                except:

                    try:
                        #может не получится удалить, тк прошло больше 48 часов, в таком случае, редактируем их
                        bot.edit_message_text(chat_id = chat_id, message_id = msg, text = 'Потрачено')
                        queries_to_bd.set_msg_menu_as_inactive(msg)

                    except:
                        queries_to_bd.save_error(str(traceback.format_exc()))
