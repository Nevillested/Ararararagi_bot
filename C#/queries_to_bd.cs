using System;
using Oracle.ManagedDataAccess.Client;
using System.Data;
using System.Reflection;

namespace ararararargibot
{
    internal class queries_to_bd
    {
        /*эта страшная шутка внизу - Tuple, это метод, возвращающий два значения. В данном случае 2 переменные типов OracleCommand и OracleConnection соответственно.
        конкретно этот метод открывает новое подключение к oracle db*/
        public static Tuple<OracleCommand, OracleConnection> new_conection()
        {
            try
            {
                string constr = "User Id=john;Password=abcd1234;Data Source=localhost:1521/XEPDB1;";
                OracleConnection con = new OracleConnection(constr);
                con.Open();
                OracleCommand cmd = new OracleCommand();
                cmd.Connection = con;
                return Tuple.Create(cmd, con);
            }
            catch (Exception exception)
            {
                Console.WriteLine("Ошибка подключения к бд.\r\n" + exception);
                return null;
            }
        }

        //добавление первоначального сообщения в историю
        public static void insert_story(string USER_TEXT, string USER_NAME, int MSG_ID, long CHAT_ID)
        {
            try
            {
                var con = new_conection();

                con.Item1.CommandText = "Insert into income_event_data(USER_TEXT, USER_NAME, MSG_ID, CHAT_ID) VALUES (:1, :2, :3, :4)";
                con.Item1.Parameters.Add(new OracleParameter("1", OracleDbType.Clob, USER_TEXT, ParameterDirection.Input));
                con.Item1.Parameters.Add(new OracleParameter("2", OracleDbType.Varchar2, USER_NAME, ParameterDirection.Input));
                con.Item1.Parameters.Add(new OracleParameter("3", OracleDbType.Int64, MSG_ID, ParameterDirection.Input));
                con.Item1.Parameters.Add(new OracleParameter("4", OracleDbType.Int64, CHAT_ID, ParameterDirection.Input));

                con.Item1.ExecuteNonQuery();
                con.Item2.Dispose();
            }
            catch(Exception exception)
            {
                Console.WriteLine("Ошибка в " + MethodBase.GetCurrentMethod().Name);
                queries_to_bd.insert_error(1, "USER_TEXT: " + USER_TEXT + ";USER_NAME: " + USER_NAME + ";MSG_ID: " + MSG_ID.ToString() + ";CHAT_ID: " + CHAT_ID.ToString(), exception);
            }
        }

        //добавление измененного сообщения в историю
        public static void update_story(string USER_TEXT, int MSG_ID, long CHAT_ID, Exception ERROR)
        {
            try
            {
                var con = new_conection();

                con.Item1.CommandText = " insert into income_event_data (user_text, user_name, chat_id, msg_id, dt_ins, dt_upd, msg_ver)" +
                                        " select :1 , user_name, chat_id, msg_id, dt_ins, current_timestamp, msg_ver + 1" +
                                        " from ( select user_name, chat_id, msg_id, dt_ins, msg_ver" +
                                               " from income_event_data" +
                                               " where chat_id = :2 and msg_id = :3 order by msg_ver desc )" +
                                        " where rownum = 1";

                con.Item1.Parameters.Add(new OracleParameter("1", OracleDbType.Clob, USER_TEXT, ParameterDirection.Input));
                con.Item1.Parameters.Add(new OracleParameter("2", OracleDbType.Int64, CHAT_ID, ParameterDirection.Input));
                con.Item1.Parameters.Add(new OracleParameter("3", OracleDbType.Int64, MSG_ID, ParameterDirection.Input));

                con.Item1.ExecuteNonQuery();
                con.Item2.Dispose();
            }
            catch(Exception exception)
            {
                Console.WriteLine("Ошибка в " + MethodBase.GetCurrentMethod().Name);
                queries_to_bd.insert_error(1, "USER_TEXT: " + USER_TEXT + ";MSG_ID: " + MSG_ID.ToString() + ";CHAT_ID: " + CHAT_ID.ToString(), exception);
            }
        }

        //выдача первоначального сообщения
        public static string get_first_msg(string USER_TEXT, int MSG_ID, long CHAT_ID)
        {
            try
            {
                var con = new_conection();
                con.Item1.CommandText = "select user_text " +
                                        "  from (select user_text " +
                                        "              , max(msg_ver) OVER(PARTITION BY msg_id) - 1 as prev_ver " +
                                        "              , msg_ver " +
                                        "          from income_event_data a " +
                                        "         where chat_id = :1 " +
                                        "           and msg_id = :2 " +
                                        "       ) " +
                                        " where msg_ver = prev_ver ";

                con.Item1.Parameters.Add(new OracleParameter("1", OracleDbType.Int64, CHAT_ID, ParameterDirection.Input));
                con.Item1.Parameters.Add(new OracleParameter("2", OracleDbType.Int64, MSG_ID, ParameterDirection.Input));

                OracleDataReader dr = con.Item1.ExecuteReader();
                dr.Read();
                string result = dr.GetString(0);

                con.Item1.ExecuteNonQuery();
                con.Item2.Dispose();

                return result;
            }
            catch(Exception exception)
            {
                Console.WriteLine("Ошибка в " + MethodBase.GetCurrentMethod().Name);
                queries_to_bd.insert_error(1, "USER_TEXT: " + USER_TEXT + ";MSG_ID: " + MSG_ID.ToString() + ";CHAT_ID: " + CHAT_ID.ToString(), exception);
                return null;
            }
        }
        
        //логирование ошибок
        public static void insert_error(int exception_type, string exception_data, Exception exception_desc)
        {
            try
            {
                var con = new_conection();

                con.Item1.CommandText = "Insert into log_exception(exception_type, exception_data, exception_desc) VALUES (:1, :2, :3)";
                con.Item1.Parameters.Add(new OracleParameter("1", OracleDbType.Int64, exception_type, ParameterDirection.Input));
                con.Item1.Parameters.Add(new OracleParameter("2", OracleDbType.Varchar2, exception_data, ParameterDirection.Input));
                con.Item1.Parameters.Add(new OracleParameter("3", OracleDbType.Varchar2, exception_desc.ToString(), ParameterDirection.Input));

                con.Item1.ExecuteNonQuery();
                con.Item2.Dispose();
            }
            catch(Exception exception)
            {
                Console.WriteLine("Ошибка в " + MethodBase.GetCurrentMethod().Name +"\r\n"+ exception);
            }

        }
       
        //выдача анекдота
        public static string get_joke()
        {
            try
            {
                var con = new_conection();

                con.Item1.CommandText = "select text_joke from (select * from jokes order by dbms_random.value) where rownum = 1";

                OracleDataReader dr = con.Item1.ExecuteReader();
                dr.Read();
                string result = dr.GetString(0);

                con.Item1.ExecuteNonQuery();
                con.Item2.Dispose();

                return result;
            }
            catch (Exception exception)
            {
                Console.WriteLine("Ошибка в " + MethodBase.GetCurrentMethod().Name);
                queries_to_bd.insert_error(1, null, exception);
                return null;
            }
        }

        //выдача всех пользователей
        public static string get_users()
        {
            try
            {
                var con = new_conection();

                con.Item1.CommandText = "select '@'||(LISTAGG(user_name, '\r\n@') WITHIN GROUP (ORDER BY user_name)) as users_name from (select distinct user_name from income_event_data)";

                OracleDataReader dr = con.Item1.ExecuteReader();
                dr.Read();
                string result = dr.GetString(0);

                con.Item1.ExecuteNonQuery();
                con.Item2.Dispose();

                return result;
            }
            catch (Exception exception)
            {
                Console.WriteLine("Ошибка в " + MethodBase.GetCurrentMethod().Name);
                queries_to_bd.insert_error(1, null, exception);
                return null;
            }
        }

        //выдача id чата с пользователем
        public static int get_chat_id(string user_name)
        {
            try
            {
                var con = new_conection();

                con.Item1.CommandText = "select distinct chat_id from income_event_data where lower(user_name)=trim(lower( :1 ))";

                con.Item1.Parameters.Add(new OracleParameter("1", OracleDbType.Varchar2, user_name, ParameterDirection.Input));

                OracleDataReader dr = con.Item1.ExecuteReader();
                dr.Read();
                int result = dr.GetInt32(0);

                con.Item1.ExecuteNonQuery();
                con.Item2.Dispose();

                return result;
            }
            catch (Exception exception)
            {
                Console.WriteLine("Ошибка в " + MethodBase.GetCurrentMethod().Name);
                queries_to_bd.insert_error(1, user_name, exception);
                return -1;
            }
        }

        //выдача перевода слов из словаря по японскому
        public static string get_translate(string user_text)
        {
            try
            {
                OracleConnection connection = new OracleConnection("User Id=john;Password=abcd1234;Data Source=localhost:1521/XEPDB1;");
                using (OracleCommand command = new OracleCommand("find_jpn_words", connection))
                {
                    command.CommandType = CommandType.StoredProcedure;
                    command.Parameters.Add("input_word", OracleDbType.Varchar2).Value = user_text;

                    command.Parameters.Add("output_result", OracleDbType.Varchar2, 4000);
                    command.Parameters["output_result"].Direction = ParameterDirection.Output;
                    connection.Open();
                    command.ExecuteNonQuery();
                    string SomeOutVar = command.Parameters["output_result"].Value.ToString();

                    return SomeOutVar;
                }
            }
            catch (Exception exception)
            {
                Console.WriteLine("Ошибка в " + MethodBase.GetCurrentMethod().Name);
                queries_to_bd.insert_error(1, user_text, exception);
                return null;
            }
        }
        
        //выдача кандзи по номеру десятка
        public static string get_kanji(int number_kanji)
        {
            try
            {
                string result = "";

                //из-за ошибки "результат строковой конкатенации слишком велик" прогоняем по циклу по одной строчке в бд и забираем каждую сюда
                for (int i = number_kanji * 10; i < number_kanji * 10 + 10; i++)
                {
                    var con = new_conection();
                    con.Item1.CommandText = "select listagg(('Кандзи: '||kanji||'\r\nПеревод: '||word_rus||'\r\nЧтения: '||reading||'\r\nПримеры:\r\n '||examples),';') from KANJI_FROM_SOURCES_FILE where id =:1";

                    con.Item1.Parameters.Add(new OracleParameter("1", OracleDbType.Int64, i, ParameterDirection.Input));

                    OracleDataReader dr = con.Item1.ExecuteReader();
                    dr.Read();
                    result += "\r\n\r\n" + dr.GetString(0);

                    con.Item1.ExecuteNonQuery();
                    con.Item2.Dispose();
                }

                return result;
            }
            catch (Exception exception)
            {
                Console.WriteLine("Ошибка в " + MethodBase.GetCurrentMethod().Name);
                queries_to_bd.insert_error(1, null, exception);
                return null;
            }
        }

        //выдача ответа на сообщение, если нет подходящих триггеров в text_cases
        public static string get_other_answer(string user_text)
        {
            try
            {
                var con = new_conection();

                con.Item1.CommandText = "with t1 as ( "
                                       + "select answer "
                                       + "  from(select answer, "
                                       + "                UTL_MATCH.edit_distance_similarity(lower(question), lower(:1)) as match_procent "
                                       + "           from other_bot_answers "
                                       + "           order by dbms_random.value "
                                       + "       ) "
                                       + " where match_procent >= 85 "
                                       + "   and rownum = 1 "
                                       + ") "
                                       + "select case "
                                       + "         when EXISTS(select answer from t1) "
                                       + "           then (select answer from t1) "
                                       + "         else 'моя твоя не понимать, сори' "
                                       + "       end as answer_to_client "
                                       + "  from dual ";

                con.Item1.Parameters.Add(new OracleParameter("1", OracleDbType.Varchar2, user_text, ParameterDirection.Input));
                OracleDataReader dr = con.Item1.ExecuteReader();
                dr.Read();
                string result = dr.GetString(0);
                con.Item1.ExecuteNonQuery();
                con.Item2.Dispose();
                return result;
            }
            catch (Exception exception)
            {
                Console.WriteLine("Ошибка в " + MethodBase.GetCurrentMethod().Name);
                queries_to_bd.insert_error(1, null, exception);
                return null;
            }
        }
    }
}
