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

    query_text = query.query

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
        search_text = query_text[6:].strip().lower()
    
        # получаем весь список песен из БД
        music_list = queries_to_bd.get_full_list_music_files()  # [(performer, song, path, 0.0), ...]

        try:

            #получаем текущий публичный ngrok URL
            ngrok_api = "http://ngrok:4040/api/tunnels"
            tunnels = requests.get(ngrok_api).json()["tunnels"]
            public_url = tunnels[0]["public_url"]  

            #вычисляем процент схожести и сохраняем в 4-е значение
            updated_music_list = []

            for performer, song, path, _ in music_list:
                full_title = f"{performer} {song}"
                similarity = SequenceMatcher(None, full_title.lower(), search_text).ratio()
                updated_music_list.append((performer, song, path, similarity))

            # ортируем по убыванию схожести и берём топ-5
            top_music = sorted(updated_music_list, key=lambda x: x[3], reverse=True)[:5]

            #формируем результаты для inline query
            for cnt, (performer, song, path, similarity) in enumerate(top_music, start=1):
                ext = os.path.splitext(path)[1].lower()
                full_title = f"{performer} - {song}"

                size_mb = os.stat(path).st_size / (1024*1024)

                #формируем относительный путь от папки /music/ для URL
                relative_path = os.path.relpath(path, "/app/assets/music")

                #кодируем URL
                url_path = "/music/" + "/".join([urllib.parse.quote(part) for part in relative_path.split(os.sep)])

                #длительность песни в секундах
                process = subprocess.run(
                    ['./ffmpeg/ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                    '-of', 'default=noprint_wrappers=1:nokey=1', path],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )

                duration_sec = int(float(process.stdout.strip()))

                #полный публичный URL
                audio_url = public_url + url_path

                #отправляем песню как аудио, если mp3/m4a
                if size_mb < 50:
                    result = types.InlineQueryResultAudio(
                        id=str(cnt),
                        audio_url=audio_url,
                        title=song,
                        performer=performer,
                        audio_duration=duration_sec
                    )
                #для остальных форматов отправляем как документ
                else:
                    result = types.InlineQueryResultArticle(
                        id=str(cnt),
                        title=performer + ': ' + song,
                        input_message_content=types.InputTextMessageContent(
                            audio_url
                        ),
                        description="Файл слишком большой. Открыть файл в браузере"
                    )

                results.append(result)

        except Exception as e:
            print("Ошибка получения ngrok URL:", e)

            result = types.InlineQueryResultArticle(
                id="1",
                title="Какая-то ошибка",
                input_message_content=types.InputTextMessageContent(
                    "Тут должна быть песня, но пока что что-то не работает."
                ),
                description="ничего не знаю"
            )

            bot.answer_inline_query(query.id, [result], cache_time=0)

    bot.answer_inline_query(query.id, results, cache_time = 0, next_offset = offset)