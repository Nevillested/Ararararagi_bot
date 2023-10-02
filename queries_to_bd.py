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