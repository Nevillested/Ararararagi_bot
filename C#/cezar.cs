using Oracle.ManagedDataAccess.Client;
using System;
using System.Data;
using System.Reflection;

namespace ararararargibot
{
    internal class cezar
    {
        //Сохраняем прилетевшее сообщение для шифровки / дешифровки
        public static void save_user_msg(long chat_id, string user_msg)
        {
            try
            {
                var con = queries_to_bd.new_conection();
                con.Item1.CommandText = "Insert into cezar(chat_id, msg) VALUES (:1, :2)";
                con.Item1.Parameters.Add(new OracleParameter("1", OracleDbType.Int32, chat_id, ParameterDirection.Input));
                con.Item1.Parameters.Add(new OracleParameter("2", OracleDbType.Varchar2, user_msg, ParameterDirection.Input));
                con.Item1.ExecuteNonQuery();
                con.Item2.Dispose();
            }
            catch (Exception exception)
            {
                Console.WriteLine("Ошибка в " + MethodBase.GetCurrentMethod().Name);
                queries_to_bd.insert_error(1, chat_id.ToString() + user_msg, exception);
            }
        }

        //Сохраняем ключ для шифровки / дешифровки
        public static void save_key(long chat_id, int user_key)
        {
            try
            {
                var con = queries_to_bd.new_conection();
                con.Item1.CommandText = "merge into cezar a using (select id from(select * from cezar where chat_id = :1 order by id desc) where rownum = 1 ) b on(a.id = b.id) when matched then update set a.key = :2 ";
                con.Item1.Parameters.Add(new OracleParameter("1", OracleDbType.Int32, chat_id, ParameterDirection.Input));
                con.Item1.Parameters.Add(new OracleParameter("2", OracleDbType.Int32, user_key, ParameterDirection.Input));
                con.Item1.ExecuteNonQuery();
                con.Item2.Dispose();
            }
            catch (Exception exception)
            {
                Console.WriteLine("Ошибка в " + MethodBase.GetCurrentMethod().Name);
                queries_to_bd.insert_error(1, chat_id.ToString() + user_key.ToString(), exception);
            }
        }
        
        //символы русской азбуки
        const string alfabet = "ЮЬНЕЛХЙМЭДЁШОУКЖСИЗГРЫЪЩВПЧЦФАЯТБ";

        //шифруем сообщение
        public static string encrypt(long msg_chat_id)
        {
            try
            {
                var con = queries_to_bd.new_conection();

                con.Item1.CommandText = "select msg, key from (select * from cezar where chat_id = :1 order by id desc) where rownum = 1";
                con.Item1.Parameters.Add(new OracleParameter("1", OracleDbType.Int32, msg_chat_id, ParameterDirection.Input));

                OracleDataReader dr = con.Item1.ExecuteReader();
                dr.Read();
                string msg_db = dr.GetString(0);
                int key_db = dr.GetInt32(1);

                con.Item2.Dispose();

                //шифруем сообщение
                const string alfabet = "ЮЬНЕЛХЙМЭДЁШОУКЖСИЗГРЫЪЩВПЧЦФАЯТБ";

                //добавляем в алфавит маленькие буквы
                var fullAlfabet = alfabet.ToLower() + alfabet.ToLower();
                var letterQty = fullAlfabet.Length;
                var retVal = "";
                for (int i = 0; i < msg_db.Length; i++)
                {
                    var c = msg_db.ToLower()[i];
                    var index = fullAlfabet.IndexOf(c);
                    if (index < 0)
                    {
                        //если символ не найден, то добавляем его в неизменном виде
                        retVal += c.ToString().ToLower();
                    }
                    else
                    {
                        var codeIndex = (letterQty + index + key_db) % letterQty;
                        retVal += fullAlfabet.ToLower()[codeIndex];
                    }
                }

                return retVal;
            }
            catch (Exception exception)
            {
                Console.WriteLine("Ошибка в " + MethodBase.GetCurrentMethod().Name);
                queries_to_bd.insert_error(1, msg_chat_id.ToString() , exception);
                return null;
            }
        }

        //дешифруем сообщение
        public static string decrypt(long msg_chat_id)
        {
            try
            {
                var con = queries_to_bd.new_conection();

                con.Item1.CommandText = "select msg, key from (select * from cezar where chat_id = :1 order by id desc) where rownum = 1";
                con.Item1.Parameters.Add(new OracleParameter("1", OracleDbType.Int32, msg_chat_id, ParameterDirection.Input));

                OracleDataReader dr = con.Item1.ExecuteReader();
                dr.Read();
                string msg_db = dr.GetString(0);
                int key_db = dr.GetInt32(1);

                con.Item2.Dispose();
                //дешифруем сообщение
                const string alfabet = "ЮЬНЕЛХЙМЭДЁШОУКЖСИЗГРЫЪЩВПЧЦФАЯТБ";

                //добавляем в алфавит маленькие буквы
                var fullAlfabet = alfabet.ToLower() + alfabet.ToLower();
                var letterQty = fullAlfabet.Length;
                var retVal = "";
                for (int i = 0; i < msg_db.Length; i++)
                {
                    var c = msg_db.ToLower()[i];
                    var index = fullAlfabet.IndexOf(c);
                    if (index < 0)
                    {
                        //если символ не найден, то добавляем его в неизменном виде
                        retVal += c.ToString().ToLower();
                    }
                    else
                    {
                        var codeIndex = (letterQty + index - key_db) % letterQty;
                        retVal += fullAlfabet.ToLower()[codeIndex];
                    }
                }
                return retVal;
            }
            catch (Exception exception)
            {
                Console.WriteLine("Ошибка в " + MethodBase.GetCurrentMethod().Name);
                queries_to_bd.insert_error(1, msg_chat_id.ToString(), exception);
                return null;
            }
        }

    }
}
