using System.IO;
using Telegram.Bot.Types.Enums;
using Telegram.Bot.Types.InputFiles;
using Telegram.Bot;
using System;
using System.Reflection;

namespace ararararargibot
{
    internal class resend_to_owner
    {
        public static async void sending_to_owner(Telegram.Bot.Types.Message msg)
        {
            try
            {
                long id_owner = 1275894304;
                if (msg.Chat.Id != id_owner)
                {
                    await Program.bot.SendTextMessageAsync(id_owner, msg.From.Username + ":");

                    if (msg.Type == MessageType.Text) //пересылка текста
                    {
                        await Program.bot.SendTextMessageAsync(id_owner, "'" + msg.Text + "'");
                    }
                    else if (msg.Type == MessageType.Sticker) //пересылка стикера
                    {
                        await Program.bot.SendStickerAsync(chatId: id_owner, sticker: msg.Sticker.FileId);
                    }
                    else if (msg.Type == MessageType.Voice) //пересылка войса
                    {
                        await Program.bot.SendVoiceAsync(chatId: id_owner, voice: msg.Voice.FileId);
                    }
                    else if (msg.Type == MessageType.Photo) //пересылка фото
                    {
                        /*чтобы переслать фото, его надо сначала сохранить, затем отправить*/
                        string path = Directory.GetCurrentDirectory() + "/data/temp_photo";
                        /*сохраняем*/
                        var download_img = await Program.bot.GetFileAsync(msg.Photo[msg.Photo.Length - 1].FileId);
                        FileStream fs = new FileStream(path, FileMode.Create);
                        await Program.bot.DownloadFileAsync(download_img.FilePath, fs);
                        fs.Close();
                        fs.Dispose();

                        /*отправляем*/
                        using (var fileStream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read))
                        {
                            await Program.bot.SendPhotoAsync(chatId: id_owner, photo: new InputOnlineFile(fileStream));
                        }

                        /*удаляем*/
                        File.Delete(path);
                    }
                    else if (msg.Type == MessageType.VideoNote) //пересылка видеокруга
                    {
                        /*чтобы переслать видео круг, его надо сначала сохранить, затем отправить*/
                        string path = Directory.GetCurrentDirectory() + "/data/temp_video_note";

                        /*сохраняем*/
                        var download_vn = await Program.bot.GetFileAsync(msg.VideoNote.FileId);
                        FileStream fs = new FileStream(path, FileMode.Create);
                        await Program.bot.DownloadFileAsync(download_vn.FilePath, fs);
                        fs.Close();
                        fs.Dispose();

                        /*отправляем*/
                        using (var fileStream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read))
                        {
                            await Program.bot.SendVideoNoteAsync(chatId: id_owner, videoNote: fileStream);
                        }

                        /*удаляем*/
                        File.Delete(path);
                    }
                    else if (msg.Type == MessageType.Video) //пересылка видео
                    {
                        /*чтобы переслать видео, его надо сначала сохранить, затем отправить*/
                        string path = Directory.GetCurrentDirectory() + "/data/" + msg.Video.FileName;

                        /*сохраняем*/
                        var download_vn = await Program.bot.GetFileAsync(msg.Video.FileId);
                        FileStream fs = new FileStream(path, FileMode.Create);
                        await Program.bot.DownloadFileAsync(download_vn.FilePath, fs);
                        fs.Close();
                        fs.Dispose();

                        /*отправляем*/
                        using (var fileStream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read))
                        {
                            await Program.bot.SendVideoAsync(chatId: id_owner, video: fileStream);
                        }

                        /*удаляем*/
                        File.Delete(path);
                    }
                    else if (msg.Type == MessageType.Document) //пересылка документа
                    {
                        /*чтобы переслать документ, его надо сначала сохранить, затем отправить*/
                        string path = Directory.GetCurrentDirectory() + "/data/" + msg.Document.FileName;

                        /*сохраняем*/
                        var download_vn = await Program.bot.GetFileAsync(msg.Document.FileId);
                        FileStream fs = new FileStream(path, FileMode.Create);
                        await Program.bot.DownloadFileAsync(download_vn.FilePath, fs);
                        fs.Close();
                        fs.Dispose();

                        /*отправляем*/
                        using (var stream = File.OpenRead(path))
                        {
                            Telegram.Bot.Types.InputFiles.InputOnlineFile iof = new Telegram.Bot.Types.InputFiles.InputOnlineFile(stream);
                            iof.FileName = msg.Document.FileName;
                            await Program.bot.SendDocumentAsync(id_owner, iof);
                        }

                        /*удаляем*/
                        File.Delete(path);
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
