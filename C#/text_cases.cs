using System;
using Telegram.Bot;
using System.IO;
using Telegram.Bot.Types.ReplyMarkups;
using System.Reflection;

namespace ararararargibot
{
    internal class text_cases
    {
        public static async void Send_answer_for_cur_text(Telegram.Bot.Types.Message msg)
        {
            try
            {
                string msg_text = msg.Text.ToLower();

                //условия
                if (msg_text != null)
                {
                    Random rand = new Random();

                    if (msg_text.Contains("/help") || msg_text.Contains("/start"))
                    {
                        await Program.bot.SendTextMessageAsync(msg.Chat.Id, "Помощь немощу, сам же догадаться не можешь интуитивно да:" +
                        "\r\n/stick - рандомный стикер с Шинобу" +
                        "\r\n/pikcha - рандомная пикча с Шинобу" +
                        "\r\n/maid - шикарные несколько артов горничных" +
                        "\r\n/encrypt - зашифруй данне по ключу" +
                        "\r\n/decrypt - расшифруй данные по ключу" +
                        "\r\n/rand - реши свою судьбу: да/нет" +
                        "\r\n/anekdot - рандомный анекдот из сборника, честно спизженного с просторов нашего необъятного" +
                        "\r\n/delete_space - я не знаю зачем, но пусть будет - удаляет пробелы" +
                        "\r\n/get_translate_jp - поиск слова в японском словаре" +
                        "\r\n/get_kanji - учим кандзи по хитрому файлу");
                    }
                    else if (msg_text == "/stick")
                    {
                        int val = rand.Next(1, 12);
                        await Program.bot.SendStickerAsync(chatId: msg.Chat.Id, sticker: "https://cdn.tlgrm.app/stickers/34e/704/34e704f5-0115-3c1e-954e-74d2b180751d/192/" + val + ".webp", replyToMessageId: msg.MessageId);
                    }
                    else if (msg_text == "/pikcha")
                    {
                        string[] allfiles = Directory.GetFiles(Directory.GetCurrentDirectory() + "/data/arts/shinobu");
                        int val = rand.Next(0, allfiles.Length);
                        string path = @allfiles[val];
                        using (var fileStream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read))
                        {
                            await Program.bot.SendPhotoAsync(chatId: msg.Chat.Id, photo: fileStream, caption: "Ну ты и изврат");
                        }
                    }
                    else if (msg_text == "/maid")
                    {
                        string[] allfiles = Directory.GetFiles(Directory.GetCurrentDirectory() + "/data/arts/maids");
                        int val = rand.Next(0, allfiles.Length);
                        string path = @allfiles[val];
                        using (var fileStream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read))
                        {
                            var imag = await Program.bot.SendPhotoAsync(chatId: msg.Chat.Id, photo: fileStream, caption: val.ToString());
                        }
                    }
                    else if (msg_text == "/rand")
                    {
                        int val = rand.Next(0, 10);
                        if (val < 5)
                        {
                            await Program.bot.SendTextMessageAsync(msg.Chat.Id, "Да!");
                        }
                        else
                        {
                            await Program.bot.SendTextMessageAsync(msg.Chat.Id, "Нет!");
                        }
                    }
                    else if (msg_text == "/anekdot")
                    {
                        string joke = queries_to_bd.get_joke();
                        await Program.bot.SendTextMessageAsync(msg.Chat.Id, joke.Replace("\\r\\n", "\r\n"));
                    }
                    else if (msg.Text == "/delete_space")
                    {
                        await Program.bot.SendTextMessageAsync(msg.Chat.Id, "Введи то, где надо убрать все пробелы", replyMarkup: new ForceReplyMarkup());
                    }
                    else if (msg_text == "/encrypt")
                    {
                        await Program.bot.SendTextMessageAsync(msg.Chat.Id, "Введите шифруемый текст на кириллице", replyMarkup: new ForceReplyMarkup());
                    }
                    else if (msg_text == "/decrypt")
                    {
                        await Program.bot.SendTextMessageAsync(msg.Chat.Id, "Введите дешифруемый текст на кириллице", replyMarkup: new ForceReplyMarkup());
                    }
                    else if (msg_text.Contains("лучшая девочка"))
                    {
                        string[] shinobu = { "Шинобу лучшая девочка, товарищ старший лейтенант!", "Шинобу.", "Однозначно Шинобу!", "Лучшая девочка-та, ради кого я создан, это Шинобу!", "Шинобу", "Солышко мое Шинобу", "А я уже кидал пикчу с Шинобу?", "А я уже кидал стикос с Шинобу?" };
                        int value = rand.Next(1, shinobu.Length);
                        await Program.bot.SendTextMessageAsync(msg.Chat.Id, shinobu[value], replyToMessageId: msg.MessageId);
                    }
                    else if (msg_text.Contains("спать"))
                    {
                        string[] sleep = { "поспать это хорошо", "ну если @g1ts0 ляжет, то видимо и мне придется", "погнали", "ура, мы идем спать" };
                        int value = rand.Next(1, sleep.Length);
                        await Program.bot.SendTextMessageAsync(msg.Chat.Id, sleep[value], replyToMessageId: msg.MessageId);
                    }
                    else if (msg_text == "/get_users" && msg.Chat.Id == 1275894304) //выдает логины всех пользователей
                    {
                        string users_name = queries_to_bd.get_users();
                        users_name = users_name.Replace("\\r\\n", "\r\n");
                        await Program.bot.SendTextMessageAsync(msg.Chat.Id, users_name, replyToMessageId: msg.MessageId);
                    }
                    else if (msg_text.Contains("/send_@") && msg.Chat.Id == 1275894304) //принимает логин пользователя, ищет ид его чата и отправляет сообщение
                    {
                        msg_text = msg_text.Replace("/send_@", ""); //обрезаем сообщение, оставляя ник пользователя без "@" и само сообщение
                        int idx_end_nickname = msg_text.IndexOf(' '); //ищем индекс пробела, чтобы понять, где кончается ник и начинается сообщение
                        string rst_nikname = msg_text.Substring(0, msg_text.Length - (msg_text.Length - idx_end_nickname)); //вытаскиваем ник, кому отправляем 
                        int msg_chat_id = queries_to_bd.get_chat_id(rst_nikname); //по нику ищем в бд id с чатом пользователя 
                        string rst_msg = msg_text.Substring(idx_end_nickname); //вытаскиваем сообщение
                        await Program.bot.SendTextMessageAsync(msg_chat_id, rst_msg); //отправляем
                    }
                    else if (msg.Text == "/get_translate_jp")
                    {
                        await Program.bot.SendTextMessageAsync(msg.Chat.Id, "Поищем что есть в словаре похожее.\r\nВведите слово на русском.", replyMarkup: new ForceReplyMarkup());
                    }
                    else if (msg.Text == "/get_kanji")
                    {
                        await Program.bot.SendTextMessageAsync(msg.Chat.Id, "Какой номер десятка кандзи?", replyMarkup: new ForceReplyMarkup());
                    }
                    else
                    {
                        char[] alphbet_rus = " абвгдеёжзийклмнопрстуфхцчшщъыьэюя".ToCharArray();
                        string clean_msg = "";
                        for (int i = 0; i < msg_text.Length; i++)
                        {
                            for (int j = 0; j < alphbet_rus.Length; j++)
                            {
                                if (msg_text[i] == alphbet_rus[j])
                                {
                                    clean_msg += alphbet_rus[j];
                                }
                            }
                        }
                        await Program.bot.SendTextMessageAsync(msg.Chat.Id, queries_to_bd.get_other_answer(clean_msg));
                    }
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
