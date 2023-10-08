import my_cfg
import psycopg2

conn = psycopg2.connect(my_cfg.pg_sql_con_string)
conn.autocommit = True
cur = conn.cursor()

#проверяет пользователя в бд, если есть-обновляет данные, если нет-добавляет данные
def check_user(data_from_message):
    chat_id = str(data_from_message.chat.id)
    first_name = ''
    username = ''
    last_name = ''
    if data_from_message.from_user.first_name == None:
        first_name = "Null"
    else:
        first_name = "'" + (data_from_message.from_user.first_name).replace("'",'"') + "'"
    if data_from_message.from_user.username == None:
        username = "Null"
    else:
        username = "'" + (data_from_message.from_user.username).replace("'",'"') + "'"
    if data_from_message.from_user.last_name == None:
        last_name = "Null"
    else:
        last_name = "'" + (data_from_message.from_user.last_name).replace("'",'"') + "'"
    language_code = "'" + str(data_from_message.from_user.language_code) + "'"
    is_premium = "'" + str(data_from_message.from_user.is_premium) + "'"
    is_bot = "'" + str(data_from_message.from_user.is_bot) + "'"
    cur.execute("""
    MERGE INTO arabot.users u
    USING (SELECT """ + chat_id + """        AS chat_id,
                  """ + first_name + """     AS first_name,
                  """ + username + """       AS username,
                  """ + last_name + """      AS last_name,
                  """ + language_code + """  AS language_code,
                  """ + is_premium + """     AS is_premium,
                  """ + is_bot + """         AS is_bot) s
    ON u.chat_id = s.chat_id
    WHEN NOT MATCHED THEN
      INSERT (chat_id,
              username,
              first_name,
              last_name,
              language_code,
              is_premium,
              is_bot)
      VALUES (s.chat_id,
              s.username,
              s.first_name,
              s.last_name,
              s.language_code,
              s.is_premium,
              s.is_bot)
    WHEN MATCHED THEN
      UPDATE SET username      = s.username,
                 first_name    = s.first_name,
                 last_name     = s.last_name,
                 language_code = s.language_code,
                 is_premium    = s.is_premium,
                 is_bot        = s.is_bot,
                 dt_updated    = current_timestamp;
    """)

#добавляет входящее сообщение в бд
def save_simple_message(data_from_message):
    chat_id = str(data_from_message.chat.id)
    message_id = str(data_from_message.message_id)
    message_type = "'" + str(data_from_message.content_type) + "'"
    message_txt_data = ''
    if data_from_message.text == None:
        message_txt_data = "Null"
    else:
        message_txt_data = "'" + (str(data_from_message.text)).replace("'",'"') + "'"
    cur.execute("""
    INSERT INTO arabot.income_simple_message
    (
     chat_id,
     message_id,
     message_type,
     message_txt_data
    )
    VALUES
    (
     """ + chat_id + """,
     """ + message_id + """,
     """ + message_type + """,
     """ + message_txt_data + """
    )
    """)

#сохраняет входящую инфу о нажатой пользователем кнопке
def save_callback_query(call):
    cur.execute("""
    INSERT INTO arabot.income_callback_query
    (
     chat_id,
     message_id,
     button_id
    )
    VALUES
    (
     """ + str(call.message.chat.id) + """,
     """ + str(call.message.message_id) + """,
     '""" + str(call.data) + """'
    )""")


#добавляет новую версию сообщения
def insert_new_smiple_message_ver(data_from_message):
    chat_id = str(data_from_message.chat.id)
    message_id = str(data_from_message.message_id)
    message_type = "'" + str(data_from_message.content_type) + "'"
    message_txt_data = ''
    if data_from_message.text == None:
        message_txt_data = "Null"
    else:
        message_txt_data = "'" + (str(data_from_message.text)).replace("'",'"') + "'"
    cur.execute("""
    INSERT INTO arabot.income_simple_message
    (
     chat_id,
     message_id,
     dt_created,
     dt_updated,
     message_version,
     message_type,
     message_txt_data
    )
    select chat_id,
           message_id,
           dt_created,
           current_timestamp,
           message_version + 1,
           message_type,
           """ + message_txt_data + """
      from arabot.income_simple_message
     where chat_id = """ + chat_id + """
       and message_id = """ + message_id + """
     order by message_version desc
     limit 1
    """)

#сохраняет исходящие сообщения меню по нажатии пользователем на кнопку
def save_outcome_data(chat_id, msg_id, msg_type, text, flg_main_menu, flg_need_response):
    cur.execute("""
    INSERT INTO arabot.outcome_data
    (
     chat_id,
     message_id,
     message_type,
     activity_menu_flg,
     text_to_user,
     flg_need_response
    )
    values
    (
     """ + str(chat_id) + """,
     """ + str(msg_id) + """,
     '""" + str(msg_type) + """',
     """ + str(flg_main_menu) + """,
     '""" + str(text) + """',
     """ + str(flg_need_response) + """
    )
    """)

#получает список айдишников сообщений, в рамках которых открыты меню у пользователя
def get_msg_of_open_menu(chat_id):
    cur.execute("""
    select distinct message_id
      from arabot.outcome_data
     where chat_id = """ + str(chat_id) + """
       and activity_menu_flg = 1
    """)
    tuple_data = cur.fetchall()
    array_messages = []
    for item in tuple_data:
        array_messages.append(item[0])
    return array_messages

#обновляем, что нет активных меню в текущий момент
def close_old_opening_menu(chat_id):
    cur.execute("""
    update arabot.outcome_data
       set activity_menu_flg = 0
    where chat_id = """ + str(chat_id) + """
    """)

#получает последнее сообщение, которое отправил пользователю и немного редактирует его. В данном случае - добавляет восклицательный знак.
#Это необходимо, т.к. если есть кейс, что пользователь просит в рамках одного меню еще пикчу (нажимает на кнопку "еще"), то телеграму нельзя отправить тоже самое меню. Оно должно быть другим. Иначе - телега даёт ошибку.
def get_last_bot_text_menu(chat_id):
    cur.execute("""
    select text_to_user
      from arabot.outcome_data
     where chat_id = """ + str(chat_id) + """
     order by dt_created desc
     limit 1
    """)
    tuple_data = cur.fetchone()
    return tuple_data[0] + '!'

#наполняем таблицу с музыкой, проставляем ID будущих кнопок
def gen_music_data(list_data_of_music_files):
    #очищаем таблицу
    cur.execute("""truncate table arabot.music_files""")
    #наполянем данными по существующим группам-альбомам-песням
    for item in list_data_of_music_files:
        sql_stmt = """
        INSERT INTO arabot.music_files (FIRST_CHAR_PERFORMER_DISPLAY_NAME,
                                        PERFORMER_DISPLAY_NAME,
                                        ALBUM_DISPLAY_NAME,
                                        SONG_DISPLAY_NAME,
                                        PATH_TO_FILE)
        VALUES ('""" + (str(item[0])).replace("'","'||''''||'") + """',
                '""" + (str(item[1])).replace("'","'||''''||'")  + """',
                '""" + (str(item[2])).replace("'","'||''''||'") + """',
                '""" + (str(item[3])).replace("'","'||''''||'")  + """',
                '""" + (str(item[4])).replace("'","'||''''||'")  + """')
        """
        cur.execute(sql_stmt)
    #создаем айдишники
    cur.execute("CALL arabot.set_music_id();")

#выдает словарь с уникальными первыми буквами названий групп и их айдишниками
def get_abc_dict():
    cur.execute("""
    SELECT DISTINCT first_char_performer_display_name,
                    first_char_performer_id
               FROM arabot.music_files
    """)
    rows = cur.fetchall()
    abc_dict = {}
    for item in rows:
        abc_dict[item[0]] = item[1]
    return abc_dict

#выдает словарь с уникальными названиями групп и их айдишниками
def get_performer_dict(char_id):
    cur.execute("""
    SELECT DISTINCT performer_display_name,
                    performer_display_id
               FROM arabot.music_files
              WHERE first_char_performer_id = '""" + char_id + """'
    """)
    rows = cur.fetchall()
    performer_dict = {}
    for item in rows:
        performer_dict[item[0]] = item[1]
    return performer_dict

#выдает словарь с уникальными названиями альбомов и их айдишниками
def get_albums_dict(performer_id):
    cur.execute("""
    SELECT DISTINCT album_display_name,
                    album_display_id
               FROM arabot.music_files
              WHERE performer_display_id = '""" + performer_id + """'
    """)
    rows = cur.fetchall()
    albums_dict = {}
    for item in rows:
        albums_dict[item[0]] = item[1]
    return albums_dict

#выдает словарь с уникальными песнями в альбоме и их айдишниками
def get_songs_in_album_dict(album_id):
    cur.execute("""
    SELECT DISTINCT song_display_name,
                    song_display_id
               FROM arabot.music_files
              WHERE album_display_id = '""" + album_id + """'
    """)
    rows = cur.fetchall()
    songs_dict = {}
    for item in rows:
        songs_dict[item[0]] = item[1]
    return songs_dict

#выдает путь к песне
def get_song_path(song_id):
    cur.execute("""
    SELECT path_to_file
      FROM arabot.music_files
     WHERE song_display_id = '""" + song_id + """'
    """)
    result_tuple = cur.fetchone()
    result_string = result_tuple[0]
    return result_string

#получает ID альбома по ID песни
def get_album_id_by_song_id(song_id):
    cur.execute("""
    SELECT album_display_id
      FROM arabot.music_files
     WHERE song_display_id = '""" + song_id + """'
    """)
    result_tuple = cur.fetchone()
    result_string = result_tuple[0]
    return result_string

#получает ID исполнителя по ID альбома
def get_performer_id_by_album_id(album_id):
    cur.execute("""
    SELECT distinct performer_display_id
      FROM arabot.music_files
     WHERE album_display_id = '""" + album_id + """'
    """)
    result_tuple = cur.fetchone()
    result_string = result_tuple[0]
    return result_string

#получает ID исполнителей по ID первой пуквы исполнителей
def get_first_char_preformer_id_by_performer_id(performer_id):
    cur.execute("""
    SELECT distinct first_char_performer_id
      FROM arabot.music_files
     WHERE performer_display_id = '""" + performer_id + """'
    """)
    result_tuple = cur.fetchone()
    result_string = result_tuple[0]
    return result_string

#выдает словарь всех существующих подписок в словаре
def get_dict_of_full_subs():
    cur.execute("""
    SELECT id,
           descr
      FROM arabot.dict_subscriptions;
    """)
    rows = cur.fetchall()
    subs_dict = {}
    for item in rows:
        subs_dict[item[1]] = '3/main_subs_' + str(item[0])
    return subs_dict

#проверяет подписывался ли когда-нибудь юзер на эту подписку
def check_subs_of_user_by_subs_id(subscription_id, chat_id):
    cur.execute("""
    SELECT count(*)
      FROM arabot.user_subscriptions
     WHERE chat_id = """ + str(chat_id) + """
       AND subscription_id = """ + str(subscription_id) + """;
    """)
    result_tuple = cur.fetchone()
    result_int = int(result_tuple[0])
    return result_int

#проверяет статус подписки
def get_status_of_subscription(subscription_id, chat_id):
    cur.execute("""
    SELECT activity_flg
      FROM arabot.user_subscriptions
     WHERE chat_id = """ + str(chat_id) + """
      AND subscription_id = """ + str(subscription_id) + """;
    """)
    result_tuple = cur.fetchone()
    result_int = int(result_tuple[0])
    return result_int

#добавляет пользователя и id подписки в таблицу с подписками
def add_to_subscriptions(chat_id, subscription_id):
    cur.execute("""
    INSERT INTO arabot.user_subscriptions
    (
     chat_id,
     subscription_id,
     activity_flg
    )
    VALUES
    (
     """ + str(chat_id) + """,
     """ + str(subscription_id) + """,
     0
    );
    """)

#обновляет статус подписки
def update_subscription(chat_id, subscription_id, status):
    cur_text = """
    UPDATE arabot.user_subscriptions
       SET activity_flg = """ + str(status) + """,
           dt_upd = current_timestamp
     WHERE chat_id = """ + str(chat_id) + """
       AND subscription_id = """ + str(subscription_id) + """;
    """
    cur.execute(cur_text)

#получает все текущие напоминалки пользователя
def get_current_notifications(chat_id):
    cur.execute("""
    SELECT id,
           notif_name
      FROM arabot.notifications;
    """)
    rows = cur.fetchall()
    subs_dict = {}
    for item in rows:
        subs_dict[item[1]] = '4/1/' + str(item[0])
    return subs_dict

#проверяет в бд, должен ли пользователем сейчас отвечать текстом или нет
def check_need_response_flg(chat_id):
    cur.execute("""
    SELECT flg_need_response
      FROM arabot.outcome_data
     WHERE chat_id = """ + str(chat_id) + """
     ORDER BY id desc
     LIMIT 1
    """)
    result_tuple = cur.fetchone()
    flg_need_response = 0
    if result_tuple:
        flg_need_response = int(result_tuple[0])
    return flg_need_response

#возаращает ID последней нажатой кнопки
def get_last_pressed_button(chat_id):
    #забираем последний BUTTON ID
    cur.execute("""
    SELECT button_id
      FROM arabot.income_callback_query
     WHERE chat_id = """ + str(chat_id) + """
     ORDER BY id desc
     LIMIT 1
    """)
    result_tuple = cur.fetchone()
    button_id = str(result_tuple[0])

    cur.execute("""
    SELECT message_id
      FROM arabot.outcome_data
     WHERE chat_id = """ + str(chat_id) + """
     ORDER BY id desc
     LIMIT 1
    """)

    result_tuple = cur.fetchone()
    message_id = int(result_tuple[0])

    return button_id, message_id

#создает новую напоминалку
def create_new_notification(chat_id, notif_name):
    cur.execute("""
    INSERT INTO arabot.notifications
    (
     chat_id,
     notif_name
    )
    VALUES
    (
     """ + str(chat_id) + """,
     '""" + str(notif_name) + """'
    );
    """)

#получает id последней созданной напоминалки
def get_last_notification_id(chat_id):
    cur.execute("""
    SELECT id
      FROM arabot.notifications
     WHERE chat_id = """ + str(chat_id) + """
     ORDER BY dt_created desc
     LIMIT 1
    """)
    result_tuple = cur.fetchone()
    result_str = str(result_tuple[0])
    return result_str

#получает значение из заданного поля по id напоминалки
def get_value_from_notification(notification_id, value):
    cur.execute("""
    SELECT """ + value + """
      FROM arabot.notifications
     WHERE id = """ + notification_id + """
    """)
    result_tuple = cur.fetchone()
    result_str = str(result_tuple[0])
    return result_str

#обновляет данные в таблице с напоминалками
def update_notfications(notification_id, target_field, target_value, repeat_flg):

    cursor_text = """
    UPDATE arabot.notifications
       SET dt_updated = current_timestamp,
           """ + str(target_field)  + """ = """ + str(target_value) + """
     WHERE id = """ + str(notification_id) + """;
    """

    if repeat_flg == 0:
        cursor_text = """
        UPDATE arabot.notifications
           SET dt_updated = current_timestamp,
               repeat_flg = 0
         WHERE id = """ + str(notification_id) + """;
        """
    elif repeat_flg == 1:
        cursor_text = """
        UPDATE arabot.notifications
           SET dt_updated = current_timestamp,
               """ + str(target_field)  + """ = """ + str(target_value) + """,
               repeat_flg = 1
         WHERE id = """ + str(notification_id) + """;
        """

    cur.execute(cursor_text)

#обнуляет всевозмодные варианты повторов
def notification_reset_repeat(notification_id):
    cur.execute("""
    UPDATE arabot.notifications
       SET dt_updated = current_timestamp,
           repeat_flg = NULL,
           every_year_flg = NULL,
           every_month_flg = NULL,
           every_week_flg = NULL,
           every_day_flg = NULL,
           every_hour_flg = NULL,
           every_minute_flg = NULL
     WHERE id = """ + str(notification_id) + """;
    """)

#получает статус напоминалки. Включена или нет
def get_status_of_notification(notification_id):
    cur.execute("""
    SELECT activity_flg
      FROM arabot.notifications
     WHERE id = """ + notification_id + """
    """)
    result_tuple = cur.fetchone()
    result_str = str(result_tuple[0])
    return result_str

# возаращет список десятков всех кандзи. Ну то есть в базе находится 157 кандзи например. Вот запрос получает список из чисел от 1 до 16 выдает его
def get_list_of_decade_number():
    cur.execute("""
    SELECT distinct decade_number
      FROM arabot.jap_kanji;
    """)
    rows = cur.fetchall()
    return rows

# получает 4 рандомных кандзи из таблицы (по номеру десятка, если он указан)
def get_list_of_kanji(decade_number = None):
    additional_filter = ''
    if decade_number != None:
        additional_filter = ' and decade_number = ' + str(decade_number)
    cur.execute("""
    select id, kanji, reading, rus_word
      from arabot.jap_kanji
     where 1 = 1 """ + additional_filter + """
     ORDER BY random()
     limit 4
    """)
    rows = cur.fetchall()
    return rows

#ищет перевод в нашем словаре
def search_in_my_dict_translate(kanji_search, kana_search, rus_search):
    current_filtr = ''
    if kanji_search != None:
        current_filtr = "lower(using_kanji) like lower('%" + kanji_search.replace("'","''") + "%') "
    elif kana_search != None:
        current_filtr = "lower(using_kana) like lower('%" + kana_search.replace("'","''") + "%') "
    elif rus_search != None:
        current_filtr = "lower(rus) like lower('%" + rus_search.replace("'","''") + "%') "

    cur.execute("""
    SELECT STRING_AGG (
        'С употреблением кандзи: ' || case when using_kanji is null then 'данные отсутствуют' else using_kanji end || '\n' ||
        'С использованием каны: ' || case when using_kana is null then 'данные отсутствуют' else using_kana end || '\n' ||
        'Чтения кандзи: ' || case when reading_kanji is null then 'данные отсутствуют' else reading_kanji end || '\n' ||
        'Перевод: ' || case when rus is null then 'данные отсутствуют' else rus end
            ,';\n\n')
    FROM arabot.japanese_dict
    where 1 = 1
    and """ + current_filtr + """
    """)
    result_tuple = cur.fetchone()
    result_str = str(result_tuple[0])
    return result_str

#ищет перевод в словаре warodai
def search_in_warodai_dict_translate(jap_text, rus_text):
    current_filtr = ''
    if jap_text != None:
        current_filtr = "( similarity(lower('" + jap_text.replace("'","''") + "'),lower(using_kana) ) * 100  >= 40 or similarity(lower('" + jap_text.replace("'","''") + "'),lower(using_kanji) ) * 100  >= 40 ) "
    elif rus_text != None:
        current_filtr = " similarity(lower('" + rus_text.replace("'","''") + "'),lower(rus_word) ) * 100  >= 40 "

    cur.execute("""
    SELECT STRING_AGG (
        'С употреблением кандзи: ' || case when using_kanji is null then 'данные отсутствуют' else using_kanji end || '\n' ||
        'С использованием каны: ' || case when using_kana is null then 'данные отсутствуют' else using_kana end || '\n' ||
        'Чтения по-русски: ' || case when reading_rus is null then 'данные отсутствуют' else reading_rus end || '\n' ||
        'Перевод: ' || case when rus_word is null then 'данные отсутствуют' else rus_word end
            ,';\n\n')
    FROM arabot.warodai_dict
    where 1 = 1
    and """ + current_filtr + """
    """)
    result_tuple = cur.fetchone()
    result_str = str(result_tuple[0])
    return result_str



