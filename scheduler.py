import keyboards
import common_methods
import queries_to_bd
import datetime
import sending
import cleaning_chat
import random

def main(MypyBot):

    cur_date_time = datetime.datetime.now()

    list_users_notifications = queries_to_bd.get_notifications_data()

    list_users_subscriptions = queries_to_bd.get_subscriptions_data()

    #сначала разбираемся с напоминалками пользователей
    if len(list_users_notifications) != 0:

        #прогоняем все напоминалки, которые забрали
        for row in list_users_notifications:

            #вытаскиваем ID напоминалки
            notification_id = row[0]

            #создаем текст напоминалки
            notification_text = "Ты просил напомнить:\n" + row[1]

            #вытаскиваем chat_id, куда отправим напоминалку
            notification_chat_id = row[2]

            #подчищаем старые активные меню
            cleaning_chat.main(MypyBot, notification_chat_id)

            #создаем список данных для текста
            text_data = (notification_text, None, None, 0, 0)

            #отправляем
            sending.main(MypyBot, notification_chat_id, text_data, None, None, None, None, None)

    #теперь разбираемся с подписками
    if len(list_users_subscriptions) != 0:

        #прогоняем все подписки, которые забрали
        for row in list_users_subscriptions:

            #вытаскиваем chat_id, куда отправим данные подписки
            subscription_chat_id = row[0]

            #вытаскиваем ID подписки
            subscription_id = row[1]

            #если это подписка с Шинобу - то она отправляется раз в час. в 00 минут
            if str(subscription_id) == '1' and cur_date_time.minute == 0:

                #подчищаем старые активные меню
                cleaning_chat.main(MypyBot, subscription_chat_id)

                #получаем рандомный url пикчи с Шинобу
                url_of_result_image = common_methods.get_url_data_pic(is_single_pic = 1, tag = 'oshino_shinobu', page = random.randint(1, 200))

                #создаем список данных для иозбражения
                photo_data = (url_of_result_image, True, 'Ежечасная рассылка лучшей девочки <3', None)

                #отправляем
                sending.main(MypyBot, subscription_chat_id, None, photo_data, None, None, None, None)

            #если это подписка на международные праздники - то она отправляется в 22:00
            elif cur_date_time.hour == 22 and cur_date_time.minute == 0 and str(subscription_id) == '2':

                #получаем сегодняшний праздник
                holiday_name = queries_to_bd.get_current_holiday()

                #если сегодня есть праздник...
                if holiday_name != None:

                    #подчищаем старые активные меню
                    cleaning_chat.main(MypyBot, subscription_chat_id)

                    #формируем текст поздравления с праздником
                    text_data = ('Сегодня ' + holiday_name.lower() + '\nС праздничком:)', None, None, 0, 0)

                    #и отправляем его
                    sending.main(MypyBot, subscription_chat_id, text_data, None, None, None, None, None)

            #если это подписка на комплименты - то она отправляется в 22:00
            elif cur_date_time.hour == 22 and cur_date_time.minute == 0 and str(subscription_id) == '3':

                #подчищаем старые активные меню
                cleaning_chat.main(MypyBot, subscription_chat_id)

                #формируем текстовые данные для комплимента
                text_data = (queries_to_bd.get_random_compliment(), None, None, 0, 0)

                #и отправляем его
                sending.main(MypyBot, subscription_chat_id, text_data, None, None, None, None, None)

    queries_to_bd.update_notification_next_start()

