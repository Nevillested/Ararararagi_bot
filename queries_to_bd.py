import my_cfg
import psycopg2

conn = psycopg2.connect(my_cfg.pg_sql_con_string)
conn.autocommit = True
cur = conn.cursor()

#логирование ошибок
def save_error(error_text):
    cur.execute("""
    INSERT INTO arabot.error_log
    (
     error_text
    )
    VALUES
    (
     '""" + error_text.replace("'", "") + """'
    )
    """)

#проверяет были ли сообщения в бд с пользователем
def check_msg(chat_id):
    cur.execute("""
    select count(*)
      from arabot.outcome_data
     where chat_id = """ + str(chat_id) + """
     """)
    tuple_data = cur.fetchone()
    return int(tuple_data[0])

#проверяет пользователя в бд
def check_user(chat_id):
    cur.execute("""
    select count(*)
      from arabot.users
     where chat_id = """ + str(chat_id) + """
     """)
    tuple_data = cur.fetchone()
    return int(tuple_data[0])

#проверяет пользователя в бд, если есть-обновляет данные, если нет-добавляет данные
def update_user(data_from_message):
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
              is_bot,
              dt_created)
      VALUES (s.chat_id,
              s.username,
              s.first_name,
              s.last_name,
              s.language_code,
              s.is_premium,
              s.is_bot,
              current_timestamp)
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
def save_data(chat_id, msg_id, type, btn_id = None, msg_txt = None):
    chat_id = str(chat_id)
    msg_id = str(msg_id)
    type = "'" + str(type) + "'"
    btn_data = None
    msg_txt_data = None

    if btn_id == None:
        btn_data = "Null"
    else:
        btn_data = "'" + btn_id + "'"

    if msg_txt == None:
        msg_txt_data = "Null"
    else:
        msg_txt_data = "'" + (str(msg_txt)).replace("'",'"') + "'"

    cur.execute("""
    INSERT INTO arabot.income_data
    (
     chat_id,
     message_id,
     message_type,
     button_id,
     msg_txt_data
    )
    VALUES
    (
     """ + chat_id + """,
     """ + msg_id + """,
     """ + type + """,
     """ + btn_data + """,
     """ + msg_txt_data + """
    )
    """)

#добавляет новую версию сообщения
def insert_new_msg_ver(data_from_message):
    message_id = str(data_from_message.message_id)
    msg_txt_data = None
    if data_from_message.text == None:
        msg_txt_data = "Null"
    else:
        msg_txt_data = "'" + (str(data_from_message.text)).replace("'",'"') + "'"
    cur.execute("""
    INSERT INTO arabot.income_data
    (
     chat_id,
     message_id,
     dt_insert,
     dt_update,
     message_version,
     message_type,
     msg_txt_data
    )
    select chat_id,
           message_id,
           dt_insert,
           current_timestamp,
           message_version + 1,
           message_type,
           """ + msg_txt_data + """
      from arabot.income_data
     where message_id = """ + message_id + """
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

#получает последний зафисированный msg_id меню
def get_menu_msg_id(chat_id):
    cur.execute("""
    select message_id
      from arabot.outcome_data
     where message_type = 'menu'
       and chat_id =  """ + str(chat_id) + """
       and activity_menu_flg = 1
    """)
    tuple = cur.fetchall()
    rows = []
    for item in tuple:
        rows.append(item[0])
    return rows

#получает последний зафисированный msg_id
def get_last_msg_id():
    cur.execute("""
    select max(a.message_id)
    from ( select message_id
             from arabot.income_data
            union all
           select message_id
             from arabot.outcome_data
         ) as a
    """)
    tuple_data = cur.fetchone()
    return int(tuple_data[0])

#проставляем msg_id как неактивное
def set_msg_menu_as_inactive(msg_id):
    cur.execute("""
    update arabot.outcome_data
       set activity_menu_flg = 0
    where message_id = """ + str(msg_id) + """
    """)

#наполняем таблицу с музыкой, проставляем ID будущих кнопок
def gen_music_data(list_data_of_music_files):
    #очищаем таблицу
    cur.execute("""truncate table arabot.music_files""")


    for item in list_data_of_music_files:
        if item[1].lower() == "metallica" and item[2].lower() == "master of puppets":
            print(item[4])

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

#получает ID исполнителей по ID первой буквы исполнителей
def get_first_char_preformer_id_by_performer_id(performer_id):
    cur.execute("""
    SELECT distinct first_char_performer_id
      FROM arabot.music_files
     WHERE performer_display_id = '""" + performer_id + """'
    """)
    result_tuple = cur.fetchone()
    result_string = result_tuple[0]
    return result_string

#получает список всех имеющихся исполнителей и песен, а также пути в файловой системе к ним
def get_full_list_music_files():
    cur.execute("""
    SELECT performer_display_name,
           song_display_name,
           path_to_file
      FROM arabot.music_files
    """)
    rows = cur.fetchall()
    
    # Создаём список (название, путь, процент схожести):
    music_list = [(item[0], item[1], item[2], 0.0) for item in rows]
    
    return music_list

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
      FROM arabot.notifications
     WHERE chat_id = """ + str(chat_id) + """;
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
      FROM arabot.income_data
     WHERE chat_id = """ + str(chat_id) + """
       AND message_type = 'button'
     ORDER BY id desc
     LIMIT 1
    """)
    result_tuple = cur.fetchone()
    button_id = str(result_tuple[0])

    return button_id

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

#получает описание напоминалки по ее ID
def get_notification_desc(notification_id):
    cur.execute("""
    SELECT NOTIF_DESC
    FROM arabot.v_notifications
    WHERE id = """ + notification_id + """
    """)
    result_tuple = cur.fetchone()
    result_str = str(result_tuple[0])
    return result_str

#удаляет напоминалку по ее ID
def delete_notification(notification_id):
    cur.execute("""
    DELETE FROM arabot.notifications
     WHERE id = """ + str(notification_id) + """
    """)

# возаращет список десятков всех кандзи. Ну то есть в базе находится 157 кандзи например. Вот запрос получает список из чисел от 1 до 16 выдает его
def get_list_of_decade_number(decade_number_start = None):
    cursor = """
    SELECT distinct decade_number
      FROM arabot.jap_kanji
    """
    if decade_number_start != None:
        cursor += ' where decade_number >= ' + str(decade_number_start)
    cur.execute(cursor)
    rows = cur.fetchall()
    return rows

#получает данные для напоминалок
def get_notifications_data():
    cur.execute("""
    SELECT id,
           notif_name,
           chat_id
      FROM arabot.v_notifications
     WHERE date_trunc('Minute', CURRENT_TIMESTAMP) = date_trunc('Minute', dt_next_run)
       AND activity_flg = 1
    """)
    rows = cur.fetchall()
    return rows

#получает данные для рассылок
def get_subscriptions_data():
    cur.execute("""
    SELECT chat_id, subscription_id
      FROM arabot.user_subscriptions a
     WHERE a.activity_flg = 1
    """)
    rows = cur.fetchall()
    return rows

#обновляет следующее время старта напоминалки
def update_notification_next_start():
    cur.execute("CALL arabot.update_notification_next_start();")

#получает рандомный анекдот
def get_random_joke():
    cur.execute("""
    select ' ``` ' || joke_text || ' ``` '
      from arabot.jokes
     ORDER BY random()
     limit 1
    """)
    result_tuple = cur.fetchone()
    result_str = str(result_tuple[0])
    return result_str

#получает рандомный комплимент
def get_random_compliment():
    cur.execute("""
    select text
      from arabot.compliments
     ORDER BY random()
     limit 1
    """)
    result_tuple = cur.fetchone()
    result_str = str(result_tuple[0])
    return result_str

#получает текущий международный праздник
def get_current_holiday():
    cur.execute("""
    SELECT text_holiday
    FROM arabot.international_holiday
    WHERE EXTRACT(day FROM date_holiday) = EXTRACT(day FROM now())
    and EXTRACT(month FROM date_holiday) = EXTRACT(month FROM now())
    """)
    result_tuple = cur.fetchone()
    result_str = None
    if result_tuple != None:
        result_str = str(result_tuple[0])
    return result_str

#проверяет была ли отправка рассылки или напоминалок за текущее время. Если была, возвращает 1, если нет - возвращает 0
def get_flg_sent(datetime_txt):
    cur.execute("""
    select count(*)
      from arabot.scheduler_stamp
     where datetime_txt = '""" + str(datetime_txt) + """';
    """)
    result_tuple = cur.fetchone()
    result = str(result_tuple[0])
    return int(result)

#обновляет данные о том, что произошла отправка
def upd_flg_sent(datetime_txt):
    cur.execute("""
    UPDATE arabot.scheduler_stamp SET datetime_txt = '""" + str(datetime_txt) + """';
    """)