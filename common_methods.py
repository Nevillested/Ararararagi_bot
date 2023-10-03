import requests
from bs4 import BeautifulSoup
import random
import urllib
import os
import queries_to_bd

############################### отправляет рандомную пикчу с Шинобу с реактора ###############################
def send_shinobu_pic(bot, chat_id, msg_id):
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

    queries_to_bd.save_outcome_data(chat_id, msg_id, 'photo', img_dir)

############################### отправляет рандомный стикер с Шинобу из имеющегося локально набора стикеров ###############################
def send_shinobu_stick(bot, chat_id, msg_id):
    #не очень красиво, что дирректория прописана вручную, но поправлю позже через os get cwd. Попробуй подключиться, если сможешь:)
    all_stickers_dir = "/home/duck/Documents/GitHub/arabot_dev/assets/stickers/"

    sticker_dir = all_stickers_dir + random.choice(os.listdir(all_stickers_dir))

    bot.send_sticker(chat_id, sticker = open(sticker_dir, "rb"))

    queries_to_bd.save_outcome_data(chat_id, msg_id, 'sticker', sticker_dir)

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