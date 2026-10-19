from telebot import types
import common_methods
import itertools
from difflib import SequenceMatcher
import os
import queries_to_bd
import requests
import urllib.parse
import subprocess

def main(bot, query):

    results = []

    query_text = (query.query).lower()

    cnt = 0

    offset = None

    if len(query.offset) != 0 and str(query.offset) != 'None':
        offset = int(query.offset)

    #для избранных, кто знает ключевое слово. (меня попросили оставить.)
    if query_text.find("fuck") >= 0:
        #меня очень просили это сделать, прошу прощения
        dict = {"Способ похождения №1" : "ой, иди нахуй", "Способ похождения №2" : "ой, иди в пизду", "Способ похождения №3" : "ой, иди в очко", "Способ похождения №4" : "Ваш звонок очень важен для нас, оставайтесь на линии"}

        if len(query_text[4:]) != 0:
            dict["Уникальный способ похождения"] = query_text[4:]

        for key, value in dict.items():
            cnt += 1

            reply_to = types.InlineKeyboardMarkup(row_width = 1)

            reply_to.add(types.InlineKeyboardButton('сходить', url= "https://track24.ru/google/?q=" + urllib.parse.quote(value) ))

            result = types.InlineQueryResultArticle(
                id = str(cnt),
                title = key,
                input_message_content = types.InputTextMessageContent(value),
                description = value,
                reply_markup = reply_to
            )
            results.append(result)

    #получение пикчи с данбору
    elif query_text.find("pic") >= 0:

        if len(query.offset) == 0:
            offset = 0

        offset += 1

        tags = (query_text.lower())[4:]

        tags = (common_methods.transliterating(tags)).replace(' ', '_')

        array_tags = tags.split("_")

        for result_tag in itertools.permutations(array_tags):

            new_tag = '_'.join(result_tag)

            results = common_methods.get_url_data_pic(is_single_pic = 0, tag = new_tag, page = offset)

            if len(results) != 0:
                break

    #получение музыки из библиотеки
    elif query_text.find("music") >= 0:

        # получаем текст после "music " и приводим к нижнему регистру
        search_text = query_text[query_text.lower().find("music") + 5:].strip().lower()

        # получаем список песен из БД
        music_list = queries_to_bd.get_full_list_music_files()  

        #создаем список, в котором будут песни, больше всего совпавшие с текстом пользователя
        updated_music_list = []

        #наполняем список с песнями для пользователя
        for performer, song, tg_file_id in music_list:
            full_title = f"{performer} {song}"
            similarity = SequenceMatcher(None, full_title.lower(), search_text).ratio()
            updated_music_list.append((performer, song, similarity, tg_file_id))

        # сортируем по убыванию схожести и берем топ-5
        top_music = sorted(updated_music_list, key=lambda x: x[2], reverse=True)[:50]

        results = []

        for cnt, (performer, song, similarity, tg_file_id) in enumerate(top_music, start=1):

            if tg_file_id != None:
                # если есть file_id, используем CachedAudio
                result = types.InlineQueryResultCachedAudio(
                    id=str(cnt),
                    audio_file_id=tg_file_id
                )
            else:
                result = types.InlineQueryResultArticle(
                    id = str(cnt),
                    title = 'Я все сказал.',
                    input_message_content = types.InputTextMessageContent('Попробуй отправить через обычное меню'),
                    description = 'Песня пока не закэширована в телеге'
                )

            results.append(result)

    try:
        bot.answer_inline_query(query.id, results, cache_time = 0, next_offset = offset)
    except:
        None