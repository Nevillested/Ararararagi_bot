from telebot import types
import common_methods
import requests
import urllib.parse
import my_cfg
import transliterate
import itertools

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

    bot.answer_inline_query(query.id, results, cache_time = 0, next_offset = offset)