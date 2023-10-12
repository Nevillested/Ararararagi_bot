from telebot import types

def main(bot, call):

    print('Запрос: ' + call.query)

    #bot.answer_inline_query(query_id_out, results_out)

    result_row = [types.InlineQueryResultArticle('1', 'Это первый вариант приветствия', types.InputTextMessageContent('Привет')),
                  types.InlineQueryResultArticle('2', 'Это второй вариант приветствия', types.InputTextMessageContent('Добрый день'))]

    bot.answer_inline_query(call.id, result_row, cache_time = 0)