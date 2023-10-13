from telebot import types
import common_methods
import requests
import emoji
import urllib.parse

def main(bot, query):

    results = []

    query_text = query.query

    #для избранных, кто знает ключевое слово. (меня попросили оставить.)
    if query_text.find("fuck") >= 0:
        cnt = 0
        #меня очень просили это сделать, проше прощения
        dict = {"Способ похождения №1" : "ой, иди нахуй", "Способ похождения №2" : "ой, иди в пизду", "Способ похождения №3" : "ой, иди в очко", "Способ похождения №4" : "Ваше звонок очень важен для нас, оставайтесь на линии"}

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

    else:

        current_text = query_text.lower()

        result = types.InlineQueryResultArticle(
            id = 1,
            title = current_text,
            input_message_content = types.InputTextMessageContent(current_text),
            description = current_text
        )
        results.append(result)

    bot.answer_inline_query(query.id, results, cache_time = 0)