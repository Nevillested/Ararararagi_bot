using Telegram.Bot;
using System.Threading.Tasks;
using System.Threading;
using System;
using Telegram.Bot.Polling;
using System.Reflection;

namespace ararararargibot
{
    class Program
    {
        public static ITelegramBotClient bot = new TelegramBotClient("old_token");

        public static async Task HandleUpdateAsync(ITelegramBotClient botClient, Telegram.Bot.Types.Update cur_event, CancellationToken cancellationToken)
        {
            income_event.income(cur_event);
        }

        public static async Task HandleErrorAsync(ITelegramBotClient botClient, Exception exception, CancellationToken cancellationToken)
        {
            Console.WriteLine("Ошибка в " + MethodBase.GetCurrentMethod().Name);
            queries_to_bd.insert_error(1, null, exception);
        }

        static void Main()
        {
            var cts = new CancellationTokenSource();
            var cancellationToken = cts.Token;
            var receiverOptions = new ReceiverOptions
            {
                AllowedUpdates = { }, // receive all cur_event types
            };
            bot.StartReceiving(
                HandleUpdateAsync,
                HandleErrorAsync,
                receiverOptions,
                cancellationToken
            );
            Console.ReadLine();
        }
    }
}