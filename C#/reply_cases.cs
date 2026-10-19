using System;
using System.Reflection;
using Telegram.Bot;
using Telegram.Bot.Types.ReplyMarkups;

namespace ararararargibot
{
    internal class reply_cases
    {
        public static async void Send_answer_for_cur_reply(Telegram.Bot.Types.Message msg)
        {
            try
            {
                string msg_text = "";
                msg_text = msg.Text.ToLower();

                //триггер на удаление пробелов
                if (msg.ReplyToMessage.Text.Contains("Введи то, где надо убрать все пробелы"))
                {
                    string delete_space = msg.Text.Replace(" ", "");

                    await Program.bot.SendTextMessageAsync(msg.Chat.Id, delete_space);

                }

                //триггер на шифрование по Цезарю
                if (msg.ReplyToMessage.Text.Contains("Введите шифруемый текст на кириллице") || msg.ReplyToMessage.Text.Contains("Введите числовой ключ в диапазоне от 1 до 32  для шифровки"))
                {
                    if (msg.ReplyToMessage.Text.Contains("Введите шифруемый текст на кириллице"))
                    {
                        //вставка шифруемого текста
                        cezar.save_user_msg(msg.Chat.Id, msg_text);
                        await Program.bot.SendTextMessageAsync(msg.Chat.Id, "Введите числовой ключ в диапазоне от 1 до 32  для шифровки", replyMarkup: new ForceReplyMarkup { Selective = true });
                    }
                    else if (msg.ReplyToMessage.Text.Contains("Введите числовой ключ в диапазоне от 1 до 32  для шифровки"))
                    {
                        cezar.save_key(msg.Chat.Id, Convert.ToInt32(msg_text));
                        //отдача результата
                        await Program.bot.SendTextMessageAsync(msg.Chat.Id, "Зашифрованный текст:\r\n" + cezar.encrypt(msg.Chat.Id), replyToMessageId: msg.MessageId);
                    }
                }

                //триггер на дешифрование по Цезарю
                if (msg.ReplyToMessage.Text.Contains("Введите дешифруемый текст на кириллице") || msg.ReplyToMessage.Text.Contains("Введите числовой ключ в диапазоне от 1 до 32  для дешифровки"))
                {
                    if (msg.ReplyToMessage.Text.Contains("Введите дешифруемый текст на кириллице"))
                    {
                        //вставка шифруемого текста
                        cezar.save_user_msg(msg.Chat.Id, msg_text);
                        await Program.bot.SendTextMessageAsync(msg.Chat.Id, "Введите числовой ключ в диапазоне от 1 до 32  для дешифровки", replyMarkup: new ForceReplyMarkup { Selective = true });
                    }
                    else if (msg.ReplyToMessage.Text.Contains("Введите числовой ключ в диапазоне от 1 до 32  для дешифровки"))
                    {
                        cezar.save_key(msg.Chat.Id, Convert.ToInt32(msg_text));
                        //отдача результата
                        await Program.bot.SendTextMessageAsync(msg.Chat.Id, "Расшифрованный текст:\r\n" + cezar.decrypt(msg.Chat.Id), replyToMessageId: msg.MessageId);
                    }
                }   

                //триггер на поиск слова в словаре
                if (msg.ReplyToMessage.Text.Contains("Поищем что есть в словаре похожее."))
                {
                    string result_dict = queries_to_bd.get_translate(msg_text);

                    //C# не может сделать рейплейс \\r\\n на \r\n в строке, пришедшей из ораклы, тк там иероглифы, поэтому прогоняем по циклу и создаем новую
                    string result = "";
                    char q = Convert.ToChar("%");
                    for (int c = 0; c < result_dict.Length; c++)
                    {
                        result += result_dict[c];
                        if (result_dict[c] == q)
                        {
                            result += "\r\n";
                        }
                    }
                    //убираем из результата особый знак %, который означает перенос строки 
                    result = result.Replace("%", "");

                    await Program.bot.SendTextMessageAsync(msg.Chat.Id, "Вот шо мы нашли:\r\n\r\n" + result, replyToMessageId: msg.MessageId);
                }
                
                //триггер на поиск кандзи по номеру десятки
                if (msg.ReplyToMessage.Text == "Какой номер десятка кандзи?")
                {
                    int number_kanji = Convert.ToInt32(msg_text);
                    string result = queries_to_bd.get_kanji(number_kanji);

                    await Program.bot.SendTextMessageAsync(msg.Chat.Id, result, replyToMessageId: msg.MessageId);
                }
            }
            catch (Exception exception)
            {
                Console.WriteLine("Ошибка в " + MethodBase.GetCurrentMethod().Name);
                queries_to_bd.insert_error(1, Newtonsoft.Json.JsonConvert.SerializeObject(msg), exception);
            }
        }
    }
}
