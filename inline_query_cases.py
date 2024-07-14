from telebot import types
import common_methods
import requests
import urllib.parse
import my_cfg

def main(bot, query):

    results = []

    query_text = query.query

    cnt = 0

    offset = None

    if len(query.offset) != 0 and str(query.offset) != 'None':
        offset = int(query.offset)

    #для избранных, кто знает ключевое слово. (меня попросили оставить.)
    if query_text.find("fuck") >= 0:
        #меня очень просили это сделать, проше прощения
        dict = {"Способ похождения №1" : "ой, иди нахуй", "Способ похождения №2" : "ой, иди в пизду", "Способ похождения №3" : "ой, иди в очко", "Способ похождения №4" : "Ваш звонок очень важен для нас, оставайтесь на линии"}

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

    elif query_text.find("pic") >= 0:

        tags = (query_text.lower())[4:]

        if len(tags) > 0:

            if len(query.offset) == 0:
                offset = 0

            offset += 1

            url_string = "https://danbooru.donmai.us/posts.json?" + my_cfg.danboru_api_key + "&tags=" + tags + "&page=" + str(offset)
            response = requests.get(url_string)
            response_list = response.json()

            for item in response_list:
                if 'variants' in item['media_asset']:
                    cnt += 1
                    result = types.InlineQueryResultPhoto(
                        id = str(cnt),
                        photo_url = (((item['media_asset'])['variants'])[-1])['url'],
                        thumbnail_url = (((item['media_asset'])['variants'])[0])['url']
                    )
                    results.append(result)

    bot.answer_inline_query(query.id, results, cache_time = 0, next_offset = offset)