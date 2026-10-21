-- Схема arabot (выгружено pg_dump --schema-only, оставлены только объекты arabot)

--
-- Name: arabot; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA arabot;

--
-- Name: calculate_dt_next_run(integer, integer, integer, integer, integer, integer, integer, integer, integer, integer, integer, integer, integer); Type: FUNCTION; Schema: arabot; Owner: postgres
--

CREATE FUNCTION arabot.calculate_dt_next_run(activity_flg integer, year_num integer, month_num integer, day_num integer, hour_num integer, minute_num integer, repeat_flg integer, every_year_flg integer, every_month_flg integer, every_week_flg integer, every_day_flg integer, every_hour_flg integer, every_minute_flg integer) RETURNS timestamp without time zone
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Выполняем вычисление и возвращаем результат
    RETURN current_timestamp;
END;
$$;

--
-- Name: instr(text, text, integer, integer); Type: FUNCTION; Schema: arabot; Owner: postgres
--

CREATE FUNCTION arabot.instr(str text, sub text, startpos integer DEFAULT 1, occurrence integer DEFAULT 1) RETURNS integer
    LANGUAGE plpgsql
    AS $$
declare 
    tail text;
    shift int;
    pos int;
    i int;
begin
    shift:= 0;
    if startpos = 0 or occurrence <= 0 then
        return 0;
    end if;
    if startpos < 0 then
        str:= reverse(str);
        sub:= reverse(sub);
        pos:= -startpos;
    else
        pos:= startpos;
    end if;
    for i in 1..occurrence loop
        shift:= shift+ pos;
        tail:= substr(str, shift);
        pos:= strpos(tail, sub);
        if pos = 0 then
            return 0;
        end if;
    end loop;
    if startpos > 0 then
        return pos+ shift- 1;
    else
        return length(str)- length(sub)- pos- shift+ 3;
    end if;
end $$;

--
-- Name: make_uid(text); Type: FUNCTION; Schema: arabot; Owner: postgres
--

CREATE FUNCTION arabot.make_uid(p_column_name text) RETURNS text
    LANGUAGE plpgsql
    AS $_$
DECLARE
    result   text := '';
    done     boolean := false;
    chars    text[] := ARRAY[
        'A','B','C','D','E','F','G','H','I','J','K','L','M',
        'N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
        'a','b','c','d','e','f','g','h','i','j','k','l','m',
        'n','o','p','q','r','s','t','u','v','w','x','y','z'
    ];
    length   integer := 10;
    cnt      integer;
    prefix   text;
BEGIN
    -- prefix
    prefix := CASE p_column_name
        WHEN 'first_char_performer_id' THEN '2/1/'
        WHEN 'performer_display_id'    THEN '2/2/'
        WHEN 'album_display_id'        THEN '2/3/'
        WHEN 'song_display_id'         THEN '2/4/'
    END;

    WHILE NOT done LOOP
        result := prefix;

        FOR i IN 1..length LOOP
            result := result || chars[1 + floor(random() * array_length(chars, 1))];
        END LOOP;

        EXECUTE format(
            'SELECT count(*) FROM arabot.music_files WHERE %I = $1',
            p_column_name
        )
        INTO cnt
        USING result;

        IF cnt = 0 THEN
            done := true;
        END IF;
    END LOOP;

    RETURN result;
END;
$_$;

--
-- Name: set_music_id(); Type: PROCEDURE; Schema: arabot; Owner: postgres
--

CREATE PROCEDURE arabot.set_music_id()
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- очистка
    UPDATE arabot.music_files
    SET
        first_char_performer_id = NULL,
        performer_display_id    = NULL,
        album_display_id        = NULL,
        song_display_id         = NULL;

    ----------------------------------------------------------------
    -- first_char_performer_id
    ----------------------------------------------------------------
    CREATE TEMP TABLE tmp_first_char AS
    SELECT DISTINCT ON (first_char_performer_display_name)
           first_char_performer_display_name,
           arabot.make_uid('first_char_performer_id') AS uid
    FROM arabot.music_files
    ORDER BY first_char_performer_display_name, path_to_file;

    UPDATE arabot.music_files m
    SET first_char_performer_id = t.uid
    FROM tmp_first_char t
    WHERE m.first_char_performer_display_name = t.first_char_performer_display_name;

    DROP TABLE tmp_first_char;

    ----------------------------------------------------------------
    -- performer_display_id
    ----------------------------------------------------------------
    CREATE TEMP TABLE tmp_performer AS
    SELECT DISTINCT ON (performer_display_name)
           performer_display_name,
           arabot.make_uid('performer_display_id') AS uid
    FROM arabot.music_files
    ORDER BY performer_display_name, path_to_file;

    UPDATE arabot.music_files m
    SET performer_display_id = t.uid
    FROM tmp_performer t
    WHERE m.performer_display_name = t.performer_display_name;

    DROP TABLE tmp_performer;

    ----------------------------------------------------------------
    -- album_display_id (уникальный в рамках исполнителя: одноимённые
    -- альбомы разных исполнителей получают разные id)
    ----------------------------------------------------------------
    CREATE TEMP TABLE tmp_album AS
    SELECT DISTINCT ON (performer_display_name, album_display_name)
           performer_display_name,
           album_display_name,
           arabot.make_uid('album_display_id') AS uid
    FROM arabot.music_files
    ORDER BY performer_display_name, album_display_name, path_to_file;

    UPDATE arabot.music_files m
    SET album_display_id = t.uid
    FROM tmp_album t
    WHERE m.performer_display_name = t.performer_display_name
      AND m.album_display_name     = t.album_display_name;

    DROP TABLE tmp_album;

    ----------------------------------------------------------------
    -- song_display_id (уникальный всегда)
    ----------------------------------------------------------------
    UPDATE arabot.music_files
    SET song_display_id = arabot.make_uid('song_display_id');

END;
$$;

--
-- Name: update_notification_next_start(); Type: PROCEDURE; Schema: arabot; Owner: postgres
--

CREATE PROCEDURE arabot.update_notification_next_start()
    LANGUAGE plpgsql
    AS $$
DECLARE
  rec   record;
  next_dt_run timestamp;
  cur_interval INTERVAL;
BEGIN

   --проходимся в цикле по всем активным и повторяемым напоминалкам
   FOR rec IN
      SELECT *
        FROM arabot.notifications
       WHERE 1 = 1
	     and activity_flg = 1
		 and repeat_flg = 1
   LOOP

	 next_dt_run := TO_TIMESTAMP( rec.year_num || '-' || rec.month_num || '-' || rec.day_num || ' ' || rec.hour_num || ':'  || rec.minute_num || ':00', 'YYYY-MM-DD HH24:MI:SS');
	 
	   --заходим в цикл, в нем нагоняем упущенное время
	   --выходим из цикла только в случае, если дата следующего запуска наконец стала в будущем времени
	   LOOP
		   
		 --выходим из цикла, только если дата следующего запуска старше, чем текущее время
		 IF date_trunc('Minute', next_dt_run) > date_trunc('Minute', current_timestamp) then
		   exit;
		 end if;
	   
	     IF rec.every_year_flg is not null then
	     
	       next_dt_run := next_dt_run + INTERVAL '1 year';
		   
	     elsif rec.every_month_flg is not null then
	     
	       next_dt_run := next_dt_run + INTERVAL '1 month';
	     
	     elsif rec.every_week_flg is not null then
	     
	       next_dt_run := next_dt_run + INTERVAL '1 week';
	     
	     elsif rec.every_day_flg is not null then
	     
	       next_dt_run := next_dt_run + INTERVAL '1 day';
	     
	     elsif rec.every_hour_flg is not null then
	     
	       next_dt_run := next_dt_run + INTERVAL '1 hour';
	     
	     elsif rec.every_minute_flg is not null then
	     
	       next_dt_run := next_dt_run + INTERVAL '1 minute';
	     
	     END IF;
		 
	   END LOOP;
	   
	   update arabot.notifications
	      set dt_next_run = next_dt_run
	    where id = rec.id;
	 
   END LOOP;

END;
$$;

--
-- Name: compliments; Type: TABLE; Schema: arabot; Owner: postgres
--

CREATE TABLE arabot.compliments (
    id integer,
    text text
);

--
-- Name: COLUMN compliments.id; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.compliments.id IS 'ID строки';

--
-- Name: COLUMN compliments.text; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.compliments.text IS 'Текст комплимента';

--
-- Name: dict_subscriptions; Type: TABLE; Schema: arabot; Owner: postgres
--

CREATE TABLE arabot.dict_subscriptions (
    id integer,
    descr text
);

--
-- Name: TABLE dict_subscriptions; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON TABLE arabot.dict_subscriptions IS 'Словарь подписок';

--
-- Name: COLUMN dict_subscriptions.id; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.dict_subscriptions.id IS 'ID подписки';

--
-- Name: COLUMN dict_subscriptions.descr; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.dict_subscriptions.descr IS 'Описание подписки';

--
-- Name: error_log; Type: TABLE; Schema: arabot; Owner: postgres
--

CREATE TABLE arabot.error_log (
    id integer NOT NULL,
    dt_ins timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    error_text text
);

--
-- Name: TABLE error_log; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON TABLE arabot.error_log IS 'Ошибки';

--
-- Name: COLUMN error_log.id; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.error_log.id IS 'ID строки';

--
-- Name: COLUMN error_log.dt_ins; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.error_log.dt_ins IS 'дата вставки';

--
-- Name: COLUMN error_log.error_text; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.error_log.error_text IS 'Текст ошибки';

--
-- Name: error_log_id_seq; Type: SEQUENCE; Schema: arabot; Owner: postgres
--

CREATE SEQUENCE arabot.error_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

--
-- Name: error_log_id_seq; Type: SEQUENCE OWNED BY; Schema: arabot; Owner: postgres
--

ALTER SEQUENCE arabot.error_log_id_seq OWNED BY arabot.error_log.id;

--
-- Name: income_data; Type: TABLE; Schema: arabot; Owner: postgres
--

CREATE TABLE arabot.income_data (
    id integer NOT NULL,
    dt_insert timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    chat_id bigint,
    message_id bigint,
    button_id text,
    message_version integer DEFAULT 0,
    message_type text,
    msg_txt_data text,
    dt_update timestamp without time zone
);

--
-- Name: TABLE income_data; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON TABLE arabot.income_data IS 'Данные о входящих сообщениях';

--
-- Name: COLUMN income_data.id; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.income_data.id IS 'ID строки';

--
-- Name: COLUMN income_data.dt_insert; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.income_data.dt_insert IS 'Дата вставки';

--
-- Name: COLUMN income_data.chat_id; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.income_data.chat_id IS 'ID чата';

--
-- Name: COLUMN income_data.message_id; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.income_data.message_id IS 'ID сообщения';

--
-- Name: COLUMN income_data.button_id; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.income_data.button_id IS 'ID кнопки';

--
-- Name: COLUMN income_data.message_version; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.income_data.message_version IS 'версия сообщения';

--
-- Name: income_callback_query_id_seq; Type: SEQUENCE; Schema: arabot; Owner: postgres
--

CREATE SEQUENCE arabot.income_callback_query_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

--
-- Name: income_callback_query_id_seq; Type: SEQUENCE OWNED BY; Schema: arabot; Owner: postgres
--

ALTER SEQUENCE arabot.income_callback_query_id_seq OWNED BY arabot.income_data.id;

--
-- Name: international_holiday; Type: TABLE; Schema: arabot; Owner: postgres
--

CREATE TABLE arabot.international_holiday (
    id integer,
    text_holiday text,
    date_holiday timestamp without time zone
);

--
-- Name: COLUMN international_holiday.id; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.international_holiday.id IS 'ID строки';

--
-- Name: COLUMN international_holiday.text_holiday; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.international_holiday.text_holiday IS 'Название праздника';

--
-- Name: COLUMN international_holiday.date_holiday; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.international_holiday.date_holiday IS 'Дата праздника';

--
-- Name: jap_dict; Type: TABLE; Schema: arabot; Owner: postgres
--

CREATE TABLE arabot.jap_dict (
    id integer NOT NULL,
    jap_word_without_kanji text,
    jap_word_with_kanji text,
    rus_word text
);

--
-- Name: TABLE jap_dict; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON TABLE arabot.jap_dict IS 'Японский словарь';

--
-- Name: COLUMN jap_dict.id; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.jap_dict.id IS 'ID строки';

--
-- Name: COLUMN jap_dict.jap_word_without_kanji; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.jap_dict.jap_word_without_kanji IS 'Написание на японском без кандзи';

--
-- Name: COLUMN jap_dict.jap_word_with_kanji; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.jap_dict.jap_word_with_kanji IS 'Написание на японском с кандзи';

--
-- Name: COLUMN jap_dict.rus_word; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.jap_dict.rus_word IS 'Русский перевод';

--
-- Name: jap_dict_id_seq; Type: SEQUENCE; Schema: arabot; Owner: postgres
--

CREATE SEQUENCE arabot.jap_dict_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

--
-- Name: jap_dict_id_seq; Type: SEQUENCE OWNED BY; Schema: arabot; Owner: postgres
--

ALTER SEQUENCE arabot.jap_dict_id_seq OWNED BY arabot.jap_dict.id;

--
-- Name: jap_kanji; Type: TABLE; Schema: arabot; Owner: postgres
--

CREATE TABLE arabot.jap_kanji (
    id integer,
    kanji text,
    reading text,
    rus_word text,
    examples text,
    decade_number integer
);

--
-- Name: COLUMN jap_kanji.id; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.jap_kanji.id IS 'ID строки';

--
-- Name: COLUMN jap_kanji.kanji; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.jap_kanji.kanji IS 'Иероглиф кандзи';

--
-- Name: COLUMN jap_kanji.reading; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.jap_kanji.reading IS 'Китайское и японское чтения';

--
-- Name: COLUMN jap_kanji.rus_word; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.jap_kanji.rus_word IS 'Перевод на русском';

--
-- Name: COLUMN jap_kanji.examples; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.jap_kanji.examples IS 'Прмиеры использования';

--
-- Name: COLUMN jap_kanji.decade_number; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.jap_kanji.decade_number IS 'Номер десятка кандзи';

--
-- Name: japanese_dict; Type: VIEW; Schema: arabot; Owner: postgres
--

CREATE VIEW arabot.japanese_dict AS
 SELECT jap_dict.jap_word_with_kanji AS using_kanji,
    NULL::text AS reading_kanji,
    jap_dict.jap_word_without_kanji AS using_kana,
    jap_dict.rus_word AS rus
   FROM arabot.jap_dict
UNION ALL
 SELECT jap_kanji.kanji AS using_kanji,
    jap_kanji.reading AS reading_kanji,
    jap_kanji.examples AS using_kana,
    jap_kanji.rus_word AS rus
   FROM arabot.jap_kanji;

--
-- Name: jokes; Type: TABLE; Schema: arabot; Owner: postgres
--

CREATE TABLE arabot.jokes (
    id integer NOT NULL,
    joke_text text
);

--
-- Name: TABLE jokes; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON TABLE arabot.jokes IS 'Анекдоты';

--
-- Name: COLUMN jokes.id; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.jokes.id IS 'ID строки';

--
-- Name: COLUMN jokes.joke_text; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.jokes.joke_text IS 'Текст анекдота';

--
-- Name: jokes_id_seq; Type: SEQUENCE; Schema: arabot; Owner: postgres
--

CREATE SEQUENCE arabot.jokes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

--
-- Name: jokes_id_seq; Type: SEQUENCE OWNED BY; Schema: arabot; Owner: postgres
--

ALTER SEQUENCE arabot.jokes_id_seq OWNED BY arabot.jokes.id;

--
-- Name: music_files; Type: TABLE; Schema: arabot; Owner: postgres
--

CREATE TABLE arabot.music_files (
    id integer NOT NULL,
    first_char_performer_display_name text,
    first_char_performer_id text,
    performer_display_name text,
    performer_display_id text,
    album_display_name text,
    album_display_id text,
    song_display_name text,
    song_display_id text,
    path_to_file text,
    tg_file_id character varying,
    file_exists bigint
);

--
-- Name: TABLE music_files; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON TABLE arabot.music_files IS 'Данные музыки';

--
-- Name: COLUMN music_files.first_char_performer_display_name; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.music_files.first_char_performer_display_name IS 'Первая буква названия исполнителя';

--
-- Name: COLUMN music_files.first_char_performer_id; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.music_files.first_char_performer_id IS 'ID первой буквы названия исполнителя';

--
-- Name: COLUMN music_files.performer_display_name; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.music_files.performer_display_name IS 'Название исполнителя';

--
-- Name: COLUMN music_files.performer_display_id; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.music_files.performer_display_id IS 'ID исполнителя';

--
-- Name: COLUMN music_files.album_display_name; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.music_files.album_display_name IS 'Название альбома';

--
-- Name: COLUMN music_files.album_display_id; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.music_files.album_display_id IS 'ID альбома';

--
-- Name: COLUMN music_files.song_display_name; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.music_files.song_display_name IS 'Название песни';

--
-- Name: COLUMN music_files.song_display_id; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.music_files.song_display_id IS 'ID песни';

--
-- Name: COLUMN music_files.path_to_file; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.music_files.path_to_file IS 'Путь к песне';

--
-- Name: music_files_id_seq; Type: SEQUENCE; Schema: arabot; Owner: postgres
--

CREATE SEQUENCE arabot.music_files_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

--
-- Name: music_files_id_seq; Type: SEQUENCE OWNED BY; Schema: arabot; Owner: postgres
--

ALTER SEQUENCE arabot.music_files_id_seq OWNED BY arabot.music_files.id;

--
-- Name: notifications; Type: TABLE; Schema: arabot; Owner: postgres
--

CREATE TABLE arabot.notifications (
    id integer NOT NULL,
    chat_id bigint,
    notif_name text,
    activity_flg integer DEFAULT 0,
    dt_created timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    dt_updated timestamp without time zone,
    repeat_flg integer,
    every_year_flg integer,
    every_month_flg integer,
    every_week_flg integer,
    every_day_flg integer,
    every_hour_flg integer,
    every_minute_flg integer,
    year_num integer,
    month_num integer,
    day_num integer,
    hour_num integer,
    minute_num integer,
    dt_next_run timestamp with time zone
);

--
-- Name: TABLE notifications; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON TABLE arabot.notifications IS 'Напоминалки юзеров';

--
-- Name: COLUMN notifications.id; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.notifications.id IS 'ID строки';

--
-- Name: COLUMN notifications.chat_id; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.notifications.chat_id IS 'ID чата';

--
-- Name: COLUMN notifications.notif_name; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.notifications.notif_name IS 'Название';

--
-- Name: COLUMN notifications.activity_flg; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.notifications.activity_flg IS 'Флаг активности напоминалки';

--
-- Name: COLUMN notifications.dt_created; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.notifications.dt_created IS 'Дата создания';

--
-- Name: COLUMN notifications.dt_updated; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.notifications.dt_updated IS 'Дата обновления';

--
-- Name: COLUMN notifications.repeat_flg; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.notifications.repeat_flg IS 'Общий флаг повторности';

--
-- Name: COLUMN notifications.every_year_flg; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.notifications.every_year_flg IS 'Флаг повторения каждый год';

--
-- Name: COLUMN notifications.every_month_flg; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.notifications.every_month_flg IS 'Флаг повторения каждый месяц';

--
-- Name: COLUMN notifications.every_week_flg; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.notifications.every_week_flg IS 'Флаг повторения каждую неделю';

--
-- Name: COLUMN notifications.every_day_flg; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.notifications.every_day_flg IS 'Флаг повтороения каждый день';

--
-- Name: COLUMN notifications.every_hour_flg; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.notifications.every_hour_flg IS 'Флаг повтороения каждый час';

--
-- Name: COLUMN notifications.every_minute_flg; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.notifications.every_minute_flg IS 'Флаг повтороения каждую минуту';

--
-- Name: COLUMN notifications.year_num; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.notifications.year_num IS 'Номер года';

--
-- Name: COLUMN notifications.month_num; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.notifications.month_num IS 'Номер месяца';

--
-- Name: COLUMN notifications.day_num; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.notifications.day_num IS 'Номер дня месяца';

--
-- Name: COLUMN notifications.hour_num; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.notifications.hour_num IS 'Номер часа';

--
-- Name: COLUMN notifications.minute_num; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.notifications.minute_num IS 'Номер минуты';

--
-- Name: COLUMN notifications.dt_next_run; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.notifications.dt_next_run IS 'Дата следующей отправки напоминалки';

--
-- Name: notifications_id_seq; Type: SEQUENCE; Schema: arabot; Owner: postgres
--

CREATE SEQUENCE arabot.notifications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

--
-- Name: notifications_id_seq; Type: SEQUENCE OWNED BY; Schema: arabot; Owner: postgres
--

ALTER SEQUENCE arabot.notifications_id_seq OWNED BY arabot.notifications.id;

--
-- Name: outcome_data; Type: TABLE; Schema: arabot; Owner: postgres
--

CREATE TABLE arabot.outcome_data (
    id integer NOT NULL,
    chat_id bigint,
    message_id bigint,
    message_type text,
    activity_menu_flg integer,
    dt_created timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    text_to_user text,
    flg_need_response integer
);

--
-- Name: TABLE outcome_data; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON TABLE arabot.outcome_data IS 'Все исходящие сообщения';

--
-- Name: COLUMN outcome_data.id; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.outcome_data.id IS 'ID строки';

--
-- Name: COLUMN outcome_data.chat_id; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.outcome_data.chat_id IS 'ID чата';

--
-- Name: COLUMN outcome_data.message_id; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.outcome_data.message_id IS 'ID сообщения';

--
-- Name: COLUMN outcome_data.message_type; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.outcome_data.message_type IS 'Тип исходящего сообщения';

--
-- Name: COLUMN outcome_data.activity_menu_flg; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.outcome_data.activity_menu_flg IS 'Активно ли меню с чатом. Если строка попала в эту таблицу, значит автоматически флаг = 1';

--
-- Name: COLUMN outcome_data.dt_created; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.outcome_data.dt_created IS 'Дата создания';

--
-- Name: COLUMN outcome_data.text_to_user; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.outcome_data.text_to_user IS 'Исходящий текст, полученнный от нажатия на кнопку пользователем';

--
-- Name: COLUMN outcome_data.flg_need_response; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.outcome_data.flg_need_response IS 'Флаг обязательности ответа пользователем на это сообщение';

--
-- Name: outcome_data_id_seq; Type: SEQUENCE; Schema: arabot; Owner: postgres
--

CREATE SEQUENCE arabot.outcome_data_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

--
-- Name: outcome_data_id_seq; Type: SEQUENCE OWNED BY; Schema: arabot; Owner: postgres
--

ALTER SEQUENCE arabot.outcome_data_id_seq OWNED BY arabot.outcome_data.id;

--
-- Name: payments; Type: TABLE; Schema: arabot; Owner: postgres
--

CREATE TABLE arabot.payments (
    id integer NOT NULL,
    dt_ins timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    chat_id bigint,
    title text,
    descr text,
    currency text,
    total_amount integer,
    telegram_payment_charge_id text,
    provider_payment_charge_id text
);

--
-- Name: TABLE payments; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON TABLE arabot.payments IS 'Данные платежей';

--
-- Name: COLUMN payments.id; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.payments.id IS 'ID строки';

--
-- Name: COLUMN payments.dt_ins; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.payments.dt_ins IS 'Дата вставки';

--
-- Name: COLUMN payments.chat_id; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.payments.chat_id IS 'ID часа с юзером, запросивший данные';

--
-- Name: COLUMN payments.title; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.payments.title IS 'Заголовок платежа';

--
-- Name: COLUMN payments.descr; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.payments.descr IS 'Описание платежа';

--
-- Name: COLUMN payments.currency; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.payments.currency IS 'Валюта платежа';

--
-- Name: COLUMN payments.total_amount; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.payments.total_amount IS 'Сумма платежа';

--
-- Name: COLUMN payments.telegram_payment_charge_id; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.payments.telegram_payment_charge_id IS 'ID платежа телеги';

--
-- Name: COLUMN payments.provider_payment_charge_id; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.payments.provider_payment_charge_id IS 'ID платежа платежной системы';

--
-- Name: payments_id_seq; Type: SEQUENCE; Schema: arabot; Owner: postgres
--

CREATE SEQUENCE arabot.payments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

--
-- Name: payments_id_seq; Type: SEQUENCE OWNED BY; Schema: arabot; Owner: postgres
--

ALTER SEQUENCE arabot.payments_id_seq OWNED BY arabot.payments.id;

--
-- Name: scheduler_stamp; Type: TABLE; Schema: arabot; Owner: postgres
--

CREATE TABLE arabot.scheduler_stamp (
    datetime_txt character varying
);

--
-- Name: test; Type: TABLE; Schema: arabot; Owner: postgres
--

CREATE TABLE arabot.test (
    txt text,
    id bigint
);

--
-- Name: user_subscriptions; Type: TABLE; Schema: arabot; Owner: postgres
--

CREATE TABLE arabot.user_subscriptions (
    dt_ins timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    dt_upd timestamp without time zone,
    chat_id bigint,
    subscription_id integer,
    activity_flg integer
);

--
-- Name: TABLE user_subscriptions; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON TABLE arabot.user_subscriptions IS 'Подписки пользователей';

--
-- Name: COLUMN user_subscriptions.dt_ins; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.user_subscriptions.dt_ins IS 'Дата вставки';

--
-- Name: COLUMN user_subscriptions.dt_upd; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.user_subscriptions.dt_upd IS 'Дата обновления';

--
-- Name: COLUMN user_subscriptions.chat_id; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.user_subscriptions.chat_id IS 'ID чата';

--
-- Name: COLUMN user_subscriptions.subscription_id; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.user_subscriptions.subscription_id IS 'ID подписки';

--
-- Name: COLUMN user_subscriptions.activity_flg; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.user_subscriptions.activity_flg IS 'Флаг активности на подписку';

--
-- Name: users; Type: TABLE; Schema: arabot; Owner: postgres
--

CREATE TABLE arabot.users (
    chat_id bigint,
    dt_created timestamp without time zone,
    dt_updated timestamp with time zone,
    username text,
    first_name text,
    last_name text,
    language_code text,
    is_premium text,
    is_bot text
);

--
-- Name: TABLE users; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON TABLE arabot.users IS 'Пользователи';

--
-- Name: COLUMN users.chat_id; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.users.chat_id IS 'ID чата';

--
-- Name: COLUMN users.dt_created; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.users.dt_created IS 'Дата вставки';

--
-- Name: COLUMN users.dt_updated; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.users.dt_updated IS 'Дата обновления';

--
-- Name: COLUMN users.username; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.users.username IS 'Никнейм';

--
-- Name: COLUMN users.first_name; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.users.first_name IS 'Отображаемое имя';

--
-- Name: COLUMN users.last_name; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.users.last_name IS 'Отображаемая фамилия';

--
-- Name: COLUMN users.language_code; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.users.language_code IS 'Языковой код';

--
-- Name: COLUMN users.is_premium; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.users.is_premium IS 'Премиум?';

--
-- Name: COLUMN users.is_bot; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.users.is_bot IS 'Бот?';

--
-- Name: v_notifications; Type: VIEW; Schema: arabot; Owner: postgres
--

CREATE VIEW arabot.v_notifications AS
 SELECT id,
    chat_id,
    notif_name,
    activity_flg,
    dt_created,
    dt_updated,
    repeat_flg,
    COALESCE(dt_next_run, to_timestamp((((((((((year_num || '-'::text) || month_num) || '-'::text) || day_num) || ' '::text) || hour_num) || ':'::text) || minute_num) || ':00'::text), 'YYYY-MM-DD HH24:MI:SS'::text)) AS dt_next_run,
    ((((((((((((((((((((('Название: '::text ||
        CASE
            WHEN (notif_name IS NOT NULL) THEN notif_name
            ELSE '-'::text
        END) || '
'::text) || 'Год: '::text) ||
        CASE
            WHEN (year_num IS NOT NULL) THEN (year_num)::text
            ELSE '-'::text
        END) || '
'::text) || 'Месяц: '::text) ||
        CASE
            WHEN (month_num IS NOT NULL) THEN (month_num)::text
            ELSE '-'::text
        END) || '
'::text) || 'День: '::text) ||
        CASE
            WHEN (day_num IS NOT NULL) THEN (day_num)::text
            ELSE '-'::text
        END) || '
'::text) || 'Час: '::text) ||
        CASE
            WHEN (hour_num IS NOT NULL) THEN (hour_num)::text
            ELSE '-'::text
        END) || '
'::text) || 'Минута: '::text) ||
        CASE
            WHEN (minute_num IS NOT NULL) THEN (minute_num)::text
            ELSE '-'::text
        END) || '
'::text) || 'Повторять: '::text) ||
        CASE
            WHEN (repeat_flg = 1) THEN ('да, '::text ||
            CASE
                WHEN (every_year_flg IS NOT NULL) THEN 'каждый год'::text
                WHEN (every_month_flg IS NOT NULL) THEN 'каждый час'::text
                WHEN (every_week_flg IS NOT NULL) THEN 'каждую неделю'::text
                WHEN (every_day_flg IS NOT NULL) THEN 'каждый день'::text
                WHEN (every_hour_flg IS NOT NULL) THEN 'каждый час'::text
                WHEN (every_minute_flg IS NOT NULL) THEN 'каждую минуту'::text
                ELSE NULL::text
            END)
            ELSE 'нет'::text
        END) || '
'::text) ||
        CASE
            WHEN (activity_flg = 0) THEN 'Следующего напоминания не будет, тк напоминалка выключена'::text
            ELSE ('Дата следующего напоминания с учетом периодичности повтора: '::text || (COALESCE(dt_next_run, to_timestamp((((((((((year_num || '-'::text) || month_num) || '-'::text) || day_num) || ' '::text) || hour_num) || ':'::text) || minute_num) || ':00'::text), 'YYYY-MM-DD HH24:MI:SS'::text)))::text)
        END) AS notif_desc,
    year_num,
    month_num,
    day_num,
    hour_num,
    minute_num,
    every_year_flg,
    every_month_flg,
    every_week_flg,
    every_day_flg,
    every_hour_flg,
    every_minute_flg
   FROM arabot.notifications;

--
-- Name: warodai_dict; Type: TABLE; Schema: arabot; Owner: postgres
--

CREATE TABLE arabot.warodai_dict (
    temp text,
    id integer NOT NULL,
    using_kana text,
    using_kanji text,
    reading_rus text,
    internal_id text,
    rus_word text
);

--
-- Name: COLUMN warodai_dict.id; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.warodai_dict.id IS 'ID строки';

--
-- Name: COLUMN warodai_dict.using_kana; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.warodai_dict.using_kana IS 'С использованием каны';

--
-- Name: COLUMN warodai_dict.using_kanji; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.warodai_dict.using_kanji IS 'С использованием кандзи';

--
-- Name: COLUMN warodai_dict.reading_rus; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.warodai_dict.reading_rus IS 'Чтение на русском';

--
-- Name: COLUMN warodai_dict.internal_id; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.warodai_dict.internal_id IS 'Внутренний ID издателя';

--
-- Name: COLUMN warodai_dict.rus_word; Type: COMMENT; Schema: arabot; Owner: postgres
--

COMMENT ON COLUMN arabot.warodai_dict.rus_word IS 'Перевод на русский';

--
-- Name: warodai_dict_id_seq; Type: SEQUENCE; Schema: arabot; Owner: postgres
--

CREATE SEQUENCE arabot.warodai_dict_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

--
-- Name: warodai_dict_id_seq; Type: SEQUENCE OWNED BY; Schema: arabot; Owner: postgres
--

ALTER SEQUENCE arabot.warodai_dict_id_seq OWNED BY arabot.warodai_dict.id;

--
-- Name: error_log id; Type: DEFAULT; Schema: arabot; Owner: postgres
--

ALTER TABLE ONLY arabot.error_log ALTER COLUMN id SET DEFAULT nextval('arabot.error_log_id_seq'::regclass);

--
-- Name: income_data id; Type: DEFAULT; Schema: arabot; Owner: postgres
--

ALTER TABLE ONLY arabot.income_data ALTER COLUMN id SET DEFAULT nextval('arabot.income_callback_query_id_seq'::regclass);

--
-- Name: jap_dict id; Type: DEFAULT; Schema: arabot; Owner: postgres
--

ALTER TABLE ONLY arabot.jap_dict ALTER COLUMN id SET DEFAULT nextval('arabot.jap_dict_id_seq'::regclass);

--
-- Name: jokes id; Type: DEFAULT; Schema: arabot; Owner: postgres
--

ALTER TABLE ONLY arabot.jokes ALTER COLUMN id SET DEFAULT nextval('arabot.jokes_id_seq'::regclass);

--
-- Name: music_files id; Type: DEFAULT; Schema: arabot; Owner: postgres
--

ALTER TABLE ONLY arabot.music_files ALTER COLUMN id SET DEFAULT nextval('arabot.music_files_id_seq'::regclass);

--
-- Name: notifications id; Type: DEFAULT; Schema: arabot; Owner: postgres
--

ALTER TABLE ONLY arabot.notifications ALTER COLUMN id SET DEFAULT nextval('arabot.notifications_id_seq'::regclass);

--
-- Name: outcome_data id; Type: DEFAULT; Schema: arabot; Owner: postgres
--

ALTER TABLE ONLY arabot.outcome_data ALTER COLUMN id SET DEFAULT nextval('arabot.outcome_data_id_seq'::regclass);

--
-- Name: payments id; Type: DEFAULT; Schema: arabot; Owner: postgres
--

ALTER TABLE ONLY arabot.payments ALTER COLUMN id SET DEFAULT nextval('arabot.payments_id_seq'::regclass);

--
-- Name: warodai_dict id; Type: DEFAULT; Schema: arabot; Owner: postgres
--

ALTER TABLE ONLY arabot.warodai_dict ALTER COLUMN id SET DEFAULT nextval('arabot.warodai_dict_id_seq'::regclass);

--
-- Name: music_files music_files_pkey; Type: CONSTRAINT; Schema: arabot; Owner: postgres
--

ALTER TABLE ONLY arabot.music_files
    ADD CONSTRAINT music_files_pkey PRIMARY KEY (id);

--
-- Name: idx_path_to_file; Type: INDEX; Schema: arabot; Owner: postgres
--

CREATE UNIQUE INDEX idx_path_to_file ON arabot.music_files USING btree (path_to_file);

