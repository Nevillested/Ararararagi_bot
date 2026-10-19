using System;
using System.Reflection;
using Telegram.Bot;

namespace ararararargibot
{
    internal class edit_msg
    {
        public static async void send_answer_for_edit_msg(Telegram.Bot.Types.Message msg_edited)
        {
            try
            {
                //добавляем в бд изменное сообщение
                queries_to_bd.update_story(msg_edited.Text, msg_edited.MessageId, msg_edited.Chat.Id, null);

                //забираем из бд первоначальное сообщение
                string prev_msg = queries_to_bd.get_first_msg(msg_edited.Text, msg_edited.MessageId, msg_edited.Chat.Id);

                //экранируем все прилетевшие в сообщении специальные знаки
                string spec_char = "!#$%&'()*+,-./:;<=>?@[]^_`{|}~";
                char[] array_spec_char = spec_char.ToCharArray();
                string rst_prev_msg = prev_msg;

                for (int i = 0; i < array_spec_char.Length; i++)
                {
                    for (int j = 0; j < prev_msg.Length; j++)
                    {
                        if (array_spec_char[i] == prev_msg[j])
                        {
                            string cur_spec_char = (array_spec_char[i]).ToString();
                            string cur_spec_char_in_prev_msg = @"\" + (prev_msg[j]).ToString();
                            rst_prev_msg = rst_prev_msg.Replace(cur_spec_char, cur_spec_char_in_prev_msg);
                        }
                    }
                }

                //добавляем к сообщению спойлер, который распарсится через MarkdownV2
                rst_prev_msg = "|| '" + rst_prev_msg + "' ||";

                await Program.bot.SendTextMessageAsync(chatId: msg_edited.Chat.Id,
                                                       text: "Ты что думаешь, я ничего не видел?\r\n" + rst_prev_msg,
                                                       parseMode: Telegram.Bot.Types.Enums.ParseMode.MarkdownV2,
                                                       replyToMessageId: msg_edited.MessageId);
            }
            catch (Exception exception)
            {
                Console.WriteLine("Ошибка в " + MethodBase.GetCurrentMethod().Name);
                queries_to_bd.insert_error(1, Newtonsoft.Json.JsonConvert.SerializeObject(msg_edited), exception);
            }
        }
    }
}
