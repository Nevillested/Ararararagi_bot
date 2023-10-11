import keyboards
import common_methods
import queries_to_bd
import datetime
import sending

def main(MypyBot):
        cur_date_time = datetime.datetime.now()

        list_users_notifications = queries_to_bd.get_notifications_data()

        list_users_subscriptions = queries_to_bd.get_subscriptions_data()

        #сначала разбираемся с напоминалками пользователей
        if len(list_users_notifications) != 0:

            #прогоняем все напоминалки, которые забрали
            for row in list_users_notifications:

                notification_id = row[0]

                notification_text = "Ты просил напомнить:\n" + row[1]

                notification_chat_id = row[2]

                last_msg_id = queries_to_bd.get_last_msg_id()

                text_data = (notification_text, None, None, 0)

                sending.main(MypyBot, notification_chat_id, last_msg_id, text_data, None, None, None, None, None)

                queries_to_bd.update_notification_next_start(notification_id)

        #теперь разбираемся с рассылками
        if len(list_users_subscriptions) != 0:

            #прогоняем все рассылки, которые забрали
            for row in list_users_subscriptions:

                subscription_chat_id = row[0]

                subscription_id = row[1]

                #если это рассылка Шинобу - то она отправляется раз в час. в 00 минут
                if str(subscription_id) == '1' and cur_date_time.minute == 00:

                    #получаем рандомный url пикчи с Шинобу
                    url_of_result_image = common_methods.get_shinobu_pic()

                    last_msg_id = queries_to_bd.get_last_msg_id()

                    photo_data = (url_of_result_image, True, 'Это ежечасная рассылка лучшей девочки')

                    sending.main(MypyBot, subscription_chat_id, last_msg_id, None, photo_data, None, None, None, None)

                #все остальные рассылки отправляются в 22:00
                elif cur_date_time.hour == 20 and cur_date_time.minute == 00:

                    text = None

                    #запрашиваем данные для рассылки поздравлений с международным праздником
                    if str(subscription_id) == '2':

                        text = queries_to_bd.get_current_holiday()

                        text_data = (text, None, None, 0)

                        last_msg_id = queries_to_bd.get_last_msg_id()

                        #если текст подписки не пустой (а он может быть пустым, например из-за того, что сегодня нет международного праздника
                        if text != None:
                            sending.main(MypyBot, notification_chat_id, last_msg_id, text_data, None, None, None, None, None)

                    #запрашиваем данные для рассылки комплимента
                    elif str(subscription_id) == '3':

                        #получает рандомный комплмент
                        text = queries_to_bd.get_random_compliment()

                        text_data = (text, None, None, 0)

                        last_msg_id = queries_to_bd.get_last_msg_id()

                        sending.main(MypyBot, notification_chat_id, last_msg_id, text_data, None, None, None, None, None)

