using Telegram.Bot.Types.Enums;
using System;
using System.Reflection;

namespace ararararargibot
{
    internal class income_event
    {
        public static void income(Telegram.Bot.Types.Update cur_event)
        {
            Telegram.Bot.Types.Message msg = cur_event.Message;

            try
            {
                if (msg is not null)
                {
                    Console.WriteLine("Сообщение от: " + cur_event.Message.From.Username + "\r\nТип сообщения: " + cur_event.Message.Type.ToString() + "\r\nТекст сообщения: " + cur_event.Message.Text + "\r\n");
                    //пересылка сообщений владельцу
                    resend_to_owner.sending_to_owner(msg);

                    //пишем историю
                    queries_to_bd.insert_story(msg.Text, msg.From.Username, msg.MessageId, msg.Chat.Id);

                    if (msg.Type == MessageType.Text)
                    {
                        if (msg.ReplyToMessage == null)
                        {
                            text_cases.Send_answer_for_cur_text(msg);
                        }
                        else if (msg.ReplyToMessage != null)
                        {
                            reply_cases.Send_answer_for_cur_reply(msg);
                        }

                    }
                }
                else
                {
                    //ответ на редактирование сообщений
                    Telegram.Bot.Types.Message msg_edited = cur_event.EditedMessage;
                    edit_msg.send_answer_for_edit_msg(msg_edited);
                }
            }
            catch (Exception exception)
            {
                Console.WriteLine("Ошибка в " + MethodBase.GetCurrentMethod().Name);
                queries_to_bd.insert_error(1, Newtonsoft.Json.JsonConvert.SerializeObject(cur_event), exception);
            }
        }
    }
}
