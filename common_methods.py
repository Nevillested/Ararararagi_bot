import requests
from bs4 import BeautifulSoup
import random
import urllib
import os
import queries_to_bd
import random

############################### отправляет рандомную пикчу с Шинобу с реактора ###############################
def send_shinobu_pic(bot, chat_id, msg_id_outcome):
    num_page = str(random.randint(1,50))
    page = "https://joyreactor.cc/search/+/" + num_page + "?tags=Oshino+Shinobu%2C+"
    html_page = urllib.request.urlopen(page)
    soup = BeautifulSoup(html_page, "lxml")
    images_url = []

    for img in soup.findAll('img'):
        if img.get('src').__contains__('post'):
            images_url.append('https:'+img.get('src'))

    url_of_result_image =  images_url[random.randint(1,len(images_url)-1)]

    response = requests.get(url_of_result_image)

    #не очень красиво, что дирректория прописана вручную, но поправлю позже через os get cwd. Попробуй подключиться, если сможешь:)
    img_dir = '/home/duck/Documents/GitHub/arabot_dev/assets/temp/shinobu.jpeg'
    if response.status_code:
        fp = open(img_dir, 'wb')
        fp.write(response.content)
        fp.close()

    bot.send_photo(chat_id, photo = open(img_dir, 'rb'), has_spoiler = True)

    queries_to_bd.save_outcome_data(chat_id, msg_id_outcome, 'photo', img_dir, 0, 0)

    msg_id_outcome = msg_id_outcome + 1

    return msg_id_outcome

############################### отправляет рандомный стикер с Шинобу из имеющегося локально набора стикеров ###############################
def send_shinobu_stick(bot, chat_id, msg_id_outcome):
    #не очень красиво, что дирректория прописана вручную, но поправлю позже через os get cwd. Попробуй подключиться, если сможешь:)
    all_stickers_dir = "/home/duck/Documents/GitHub/arabot_dev/assets/stickers/"

    sticker_dir = all_stickers_dir + random.choice(os.listdir(all_stickers_dir))

    bot.send_sticker(chat_id, sticker = open(sticker_dir, "rb"))

    queries_to_bd.save_outcome_data(chat_id, msg_id_outcome, 'sticker', sticker_dir, 0, 0)

    msg_id_outcome = msg_id_outcome + 1

    return msg_id_outcome

############################### подготовка данных по музыке ###############################

#не очень красиво, что дирректория прописана вручную, но поправлю позже через os get cwd. Попробуй подключиться, если сможешь:)
music_path = "/home/duck/Documents/GitHub/arabot_dev/assets/music"

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
        unique_item = path_of_file.replace(r'/home/duck/Documents/GitHub/arabot_dev/assets/music/','')

        item_zero  = (unique_item[0]).upper()
        item_one   = unique_item[0:find_nth(unique_item,r'/',1)]
        item_two   = unique_item[find_nth(unique_item,r'/',1)+1:find_nth(unique_item,r'/',2)]
        item_three = unique_item[find_nth(unique_item,r'/',2)+1:unique_item.rindex('.')]
        item_four  = path_of_file
        list_data_of_music_files.append([item_zero, item_one, item_two, item_three, item_four])

    #раскомментировать, если появится новая музыка по директории '/home/duck/Documents/GitHub/arabot_dev/assets/music'
    #queries_to_bd.gen_music_data(list_data_of_music_files)

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

            if index_in_abc > 0:

                new_index_in_abc = index_in_abc + int(key)

                if new_index_in_abc > cnt_abc:

                    new_index_in_abc = new_index_in_abc % cnt_abc# new_index_in_abc - cnt_abc

                text_out += alphabet[new_index_in_abc]

            else:
                text_out += chr

        text_out = 'Зашифрованный текст:\n' + '```' + text_out + '```'

    elif operation_type == 'decrypt':

        for chr in text_to_oper:

            index_in_abc = alphabet.find(chr)

            if index_in_abc > 0:

                new_index_in_abc = index_in_abc - int(key)

                if new_index_in_abc < 0:

                    new_index_in_abc = cnt_abc -(- new_index_in_abc % cnt_abc)

                text_out += alphabet[new_index_in_abc]

            else:
                text_out += chr

        text_out = 'Расшифрованный текст:\n' + '```' + text_out + '```'

    return text_out

############################### Метод отправки квизов ###############################
#это можно было сделать намного лучше, но у меня руки из жопы обращаться со списками, массивами и кортежами
def send_kanji_quiz_by(bot, chat_id, decade_number, msg_id_outcome):

    tuple_of_kanji = queries_to_bd.get_list_of_kanji(decade_number)

    array_of_kanji_id = []

    poll_options_out = []

    array_of_kanji = []

    for item in tuple_of_kanji:

        #наполняем массив с вариантами ответов
        poll_options_out.append(item[3] + ' (Чтения: ' + item[2] + ')')

        #наполняем массив с ID кандзи
        array_of_kanji_id.append(item[0])

        #наполяем массив с иероглифами кандзи
        array_of_kanji.append(item[1])

    #выбираем рандомом ID кандзи, по которому будем спрашивать
    selected_value = random.choice(array_of_kanji_id)

    #ищем индекс правильного ответа в массивев массиве
    correct_option_id_out = array_of_kanji_id.index(selected_value)

    #ищем иероглиф кандзи, по которому задаем вопрос
    question_kaji = array_of_kanji[correct_option_id_out]

    text = 'Что это за кандзи ' + question_kaji + ' ?'

    #отправляем квиз
    bot.send_poll(chat_id, text, options = poll_options_out, correct_option_id  = correct_option_id_out, type = 'quiz')

    #сохраняем данные
    queries_to_bd.save_outcome_data(chat_id, msg_id_outcome, 'poll', text, 0, 0)

    #инкрементируем msg_id
    msg_id_outcome = msg_id_outcome + 1

    return msg_id_outcome