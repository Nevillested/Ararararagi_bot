from geopandas.tools import geocode
import speech_recognition as sr
from telebot import types
from gtts import gTTS
import queries_to_bd
import subprocess
import keyboards
import requests
import my_cfg
import random
import segno
import json
import os

############################### выдает массив или одиночну ссылку на пикчу по заданному тегу с данбору ###############################
def get_url_data_pic(is_single_pic, tag, page):

    array_of_InlineQueryResultPhoto = []
    array_of_string_url = []
    url_string = "https://danbooru.donmai.us/posts.json?" + my_cfg.danboru_api_key + "&tags=" + tag.replace(',','&') + "&page=" + str(page)
    response = requests.get(url_string)
    response_list = response.json()
    cnt = 0

    if len(response_list) != 0:
        for item in response_list:
            if 'variants' in item['media_asset']:
                if item['file_size'] > 20000000 or (tag == 'oshino_shinobu' and (item['rating']).lower() == 'e'): #https://danbooru.donmai.us/wiki_pages/howto:rate
                    None
                else:
                    cnt += 1
                    result = types.InlineQueryResultPhoto(
                        id = str(cnt),
                        photo_url = (((item['media_asset'])['variants'])[-1])['url'],
                        thumbnail_url = (((item['media_asset'])['variants'])[0])['url'],
                        caption = '<span class="tg-spoiler">' + item['tag_string_character'] + '</span>',
                        parse_mode='html'
                    )
                    array_of_InlineQueryResultPhoto.append(result)
                    array_of_string_url.append((((item['media_asset'])['variants'])[-1])['url'])

    if is_single_pic == 0:
        return array_of_InlineQueryResultPhoto
    else:
        return random.choice(array_of_string_url)

############################### отправляет рандомный стикер с Шинобу из имеющегося локально набора стикеров ###############################
def get_shinobu_stick():

    all_stickers_dir = str(os.getcwd()) + "/assets/stickers/"

    sticker_dir = all_stickers_dir + random.choice(os.listdir(all_stickers_dir))

    return sticker_dir

############################### подготовка данных по музыке ###############################

music_path = str(os.getcwd()) + "/assets/music"

list_data_of_music_files = list()

#получение списка с путями всех файлов в текущей директории
def getListOfPathFiles(current_path):
    allFiles = list()
    listOfFile = os.listdir(current_path)
    for entry in listOfFile:
        fullPath = os.path.join(current_path, entry)
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfPathFiles(fullPath)
        else:
            allFiles.append(fullPath)
    return allFiles

#выдает индекс н-ного вхождение подстроки в строке
def find_nth(string, substring, n):
   if (n == 1):
       return string.find(substring)
   else:
       return string.find(substring, find_nth(string, substring, n - 1) + 1)

#подготовка данных по музыке
def prepare_music_data():
    #создаем список с путями всех файлов в текущей директориим
    list_of_full_path_all_files = sorted(getListOfPathFiles(music_path))
    #а теперь наполняем новый список (list_data_of_music_files) кортежами, каждый из которых состоит из 4 элементов, где:
    #item_zero   0 элемент списка - буква, с которой начинается название группы
    #item_one    1 элемент списка - название группы
    #item_two    2 элемент списка - название альбома
    #item_three  3 элемент списка - название песни
    for path_of_file in list_of_full_path_all_files:
        #не очень красиво, что дирректория прописана вручную, но поправлю позже через os get cwd. Попробуй подключиться, если сможешь:)
        unique_item = path_of_file.replace(str(os.getcwd()) + r'/assets/music/','')

        item_zero  = (unique_item[0]).upper()
        item_one   = unique_item[0:find_nth(unique_item,r'/',1)]
        item_two   = unique_item[find_nth(unique_item,r'/',1)+1:find_nth(unique_item,r'/',2)]
        item_three = unique_item[find_nth(unique_item,r'/',2)+1:unique_item.rindex('.')]
        item_four  = path_of_file
        list_data_of_music_files.append([item_zero, item_one, item_two, item_three, item_four])

    #раскомментировать, если появится новая музыка
    queries_to_bd.gen_music_data(list_data_of_music_files)

############################### Метод шифрования и дешифрования ###############################
def encrypting_decrypting(operation_type, lang_code, key, text_to_oper):
    cnt_abc = 0
    alphabet = ''
    text_out = ''
    text_to_oper = text_to_oper.lower()
    if lang_code == 'RU':
        cnt_abc = 32
        alphabet = 'азокщцчспфнхгъбыуьмивтяерйюжэлшд'
    if lang_code == 'EN':
        cnt_abc = 26
        alphabet = 'yvhzkaucsoqigjxbnfdptrlwme'

    if operation_type == 'encrypt':

        for chr in text_to_oper:

            index_in_abc = alphabet.find(chr)

            if index_in_abc >= 0:

                new_index_in_abc = index_in_abc + int(key)

                if new_index_in_abc >= cnt_abc:

                    new_index_in_abc = new_index_in_abc % cnt_abc

                text_out += alphabet[new_index_in_abc]

            else:
                text_out += chr

        text_out = 'Зашифрованный текст:\n' + ' ``` ' + text_out + ' ``` '

    elif operation_type == 'decrypt':

        for chr in text_to_oper:

            index_in_abc = alphabet.find(chr)

            if index_in_abc >= 0:

                new_index_in_abc = index_in_abc - int(key)

                if new_index_in_abc < 0:

                    new_index_in_abc = cnt_abc -(- new_index_in_abc % cnt_abc)

                text_out += alphabet[new_index_in_abc]

            else:
                text_out += chr

        text_out = 'Расшифрованный текст:\n' + ' ``` ' + text_out + ' ``` '

    return text_out

############################### Методы преобразования текста в речь и наоборот ###############################

#преобразует текст в речь
def convert_text_to_speech(chat_id, text_in, lang):

    rec_lang = None

    if lang == '1':
        rec_lang = "ru"
    elif lang == '2':
        rec_lang = "en"

    myobj = gTTS(text=text_in, lang=rec_lang, slow=False)

    myobj.save("assets/temp/convert_text_to_speech/" + chat_id + ".ogg")

    result = os.getcwd() + r'/assets/temp/convert_text_to_speech/' + chat_id + '.ogg'

    return result

#преобразует речь в текст
def convert_speech_to_text(lang, file_path_ogg):

    file_path_wav = file_path_ogg.replace('.ogg', '.wav')

    process = subprocess.run(['ffmpeg','-y', '-i', file_path_ogg, file_path_wav])

    rec_lang = None

    if lang == '1':
        rec_lang = "ru-RU"
    elif lang == '2':
        rec_lang = "en-EN"

    r = sr.Recognizer()

    result = ''

    hellow = sr.AudioFile(file_path_wav)

    with hellow as source:
        audio = r.record(source)
    result = r.recognize_google(audio, language = rec_lang)

    return result

############################### Методы для работы с погодой ###############################

#получает долготу и широту по месту
def get_coordinates(place):
    location = geocode(place, provider="nominatim" , user_agent = 'my_request')
    point = location.geometry.iloc[0]
    return point.y, point.x

#выдает погоду на текущее время
def current_weather(cur_data):

    api_key = my_cfg.weather_token

    latitude, longitude = get_coordinates(cur_data)

    address = f'https://api.openweathermap.org/data/2.5/weather?lat={str(latitude)}&lon={str(longitude)}&lang=ru&appid={api_key}'
    x = requests.get(address)

    response = json.loads(str(x.json()).replace('[','').replace(']','').replace('\'', '\"'))

    new_dict = {}
    for item in response:
        if item in ['weather', 'main', 'wind', 'sys']:
            new_dict[item] = response[item]

    weather_description  = str(new_dict['weather']['description'])

    main_temp            = str(round((int(new_dict['main']['temp']) - 273.15),2)) + '°'
    main_feels_like      = str(round((int(new_dict['main']['feels_like']) - 273.15),2))+ '°'
    main_temp_min        = str(round((int(new_dict['main']['temp_min']) - 273.15),2))+ '°'
    main_temp_max        = str(round((int(new_dict['main']['temp_max']) - 273.15),2))+ '°'
    main_pressure        = str(round((float(new_dict['main']['pressure']) * 0.75006375541921), 0)) + ' мм.рт.ст.'
    wind_speed           = str(new_dict['wind']['speed']) + ' м/с'


    result = 'На небе: ' + weather_description + '.'
    result = result + '\nТемпература: ' + main_temp + '. Ощущается как ' + main_feels_like + '. Минимальная ' + main_temp_min + '. Максимальная ' + main_temp_max + '. Давление ' + main_pressure + '.'
    result = result + '\nВетер: ' + wind_speed + '.'

    return result

############################### Методы создания QR-кода ###############################
#создает qr-код
def create_qr_code(text, chat_id):
    qrcode = segno.make_qr(text)
    new_dir = str(os.getcwd()) + '/assets/temp/qr_codes/'
    os.chdir(new_dir)
    name = "qr_code_" + chat_id + ".pdf"
    qrcode.save(name, border=1, scale=8)
    result =  new_dir + name
    return result

############################### Методы получения пикчи  рекатора по тегу ###############################
#заменяет спец символы для URL строки
def url_encode_string(input_string):
    replacements = {"'": "%27", " ": "%20", "%": "%25", "/": "%2F", " " : "+"}

    for char, replacement in replacements.items():
        input_string = input_string.replace(char, replacement)

    return input_string

#свой метод транслитерации русских слов
def transliterating(word):
    dic = {'ь':'', 'ъ':'', 'а':'a', 'б':'b','в':'v', 'г':'g', 'д':'d', 'е':'e', 'ё':'yo','ж':'zh', 'з':'z', 'и':'i', 'й':'y', 'к':'k', 'л':'l', 'м':'m', 'н':'n', 'о':'o', 'п':'p', 'р':'r',  'с':'s', 'т':'t', 'у':'u', 'ф':'f', 'х':'h', 'ц':'ts', 'ч':'ch', 'ш':'sh', 'щ':'sch', 'ы':'yi', 'э':'e', 'ю':'yu', 'я':'ya'}
    result = ''
    for char in word:
        if char in (dic.keys()):
            result += dic[char]
        else:
            result += char
    return result
