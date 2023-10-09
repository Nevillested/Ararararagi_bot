import keyboards
import common_methods
import queries_to_bd
import datetime

def main(MypyBot):
        cur_date_time = datetime.datetime.now()

        list_users_notifications = queries_to_bd.get_notifications_data()

        list_users_subscriptions = queries_to_bd.get_subscriptions_data()

        #сначала разбираемся с напоминалками пользователей
        if len(list_users_notifications) != 0:

            #прогоняем все напоминалки, которые забрали
            for row in list_users_notifications:

                notification_id = row[0]

                notification_text = "Ты просил напоминть:\n'" + row[1] + "'"

                notification_chat_id = row[2]

                try:

                    MypyBot.send_message(notification_chat_id, notification_text)

                except Exception as e:

                    print('Не отправлено сообщение этому пользователю: ' + str(notification_chat_id) + '. Текст ошибки:\n' + str(e))

                queries_to_bd.update_notification_next_start(notification_id)

        #теперь разбираемся с рассылками
        if len(list_users_subscriptions) != 0:

            #прогоняем все рассылки, которые забрали
            for row in list_users_subscriptions:

                chat_id = row[0]

                subscription_id = row[1]

                #если это рассылка Шинобу - то она отправляется раз в час. в 00 минут
                if str(subscription_id) == '1' and cur_date_time.minute == 00:

                    #получаем рандомный url пикчи с Шинобу
                    url_of_result_image = common_methods.get_shinobu_pic()

                    try:

                        #отправляем ее
                        MypyBot.send_photo(chat_id, photo = url_of_result_image, has_spoiler = True, caption = 'Это ежечасная рассылка лучшей девочки')

                    except Exception as e:

                        print('Не отправлено сообщение этому пользователю: ' + str(chat_id) + '. Текст ошибки:\n' + str(e))

                #все остальные рассылки отправляются в 22:00
                elif cur_date_time.hour == 19 and cur_date_time.minute == 00:

                    text = ''

                    #запрашиваем данные для рассылки поздравлений с международным праздником
                    if str(subscription_id) == '2':

                        text = 'Это рассылка международных праздников'

                    #запрашиваем данные для рассылки комплимента
                    elif str(subscription_id) == '3':

                        text = 'Это рассылка комплиментов'

                    try:

                        MypyBot.send_message(chat_id, text)

                    except Exception as e:

                        print('Не отправлено сообщение этому пользователю: ' + str(chat_id) + '. Текст ошибки:\n' + str(e))