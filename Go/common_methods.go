package main

import (
	"ararararagi_bot/internal/db"
	"context"
	"io/fs"
	"log"
	"os"
	"path/filepath"
	"strings"
)

var assets_path = os.Getenv("ASSETS_DIR")

var music_path = filepath.Join(assets_path, "music")

var audioFormats = map[string]bool{
	"wav": true, "aiff": true, "aif": true, "au": true, "pcm": true, "bwf": true,
	"flac": true, "alac": true, "ape": true, "wv": true, "tak": true, "tta": true, "shn": true,
	"mp3": true, "aac": true, "m4a": true, "ogg": true, "opus": true, "wma": true,
	"atrac": true, "atrac3": true, "atrac3plus": true,
	"ac3": true, "eac3": true, "dts": true,
	"amr": true, "amr-wb": true, "speex": true,
	"mpc": true, "lc-aac": true, "he-aac": true, "he-aacv2": true,
	"qcelp": true, "ra": true, "rm": true,
	"mod": true, "xm": true, "s3m": true, "it": true, "mtm": true, "669": true,
	"ult": true, "far": true, "stm": true,
	"mid": true, "midi": true, "rmi": true, "kar": true,
	"dsf": true, "dff": true,
	"caf": true, "mka": true, "nut": true, "3ga": true,
	"voc": true, "8svx": true, "16svx": true, "iff": true,
	"dvf": true, "dss": true, "msv": true, "gsm": true, "sd2": true,
}

type musicFiles struct {
	item_zero  string //0 элемент списка - буква, с которой начинается название группы
	item_one   string //1 элемент списка - название группы
	item_two   string //2 элемент списка - название альбома
	item_three string //3 элемент списка - название песни
	item_four  string //4 элемент списка - полный путь к песне
}

func prepare_music_data(queries *db.Queries) {

	//это массив экземпляров. Каждый экземпляр состоит из нескольких полей. Описание полей - выше
	var musicFilesList []musicFiles

	//массив в котором будет временно держать автора, альбом и песню Потом эти данные будут разложены по полям каждого экземпляра в массиве
	var author_album_song []string

	//тут будем держать путь к песне вида "Автор/Альбом/Песня.mp3", чтобы на основе этого полчить автора, альбом и песню
	var path_author_album_song string

	//проходимся рекурсивно по каждому файлу в папке с музыкой music_path...
	err := filepath.WalkDir(
		music_path,
		func(path string, d fs.DirEntry, err error) error {
			if err != nil {
				return err // не смог прочитать что-то, прекращаем обход
			}
			if d.IsDir() {
				return nil // папка, пропускаем, а WalkDir сам зайдёт внутрь
			}

			ext := strings.ToLower(strings.TrimPrefix(filepath.Ext(path), "."))

			if !audioFormats[ext] || strings.Contains(path, "_compressed") {
				return nil // не аудио или сжатая копия: пропускаем этот файл
			}

			//путь к песне вида "Автор/Альбом/Песня.mp3"
			path_author_album_song = strings.ReplaceAll(path, music_path+"/", "")

			//после разделения строки вида "Автор/Альбом/Песня.mp3" получаем массив из 3 элементов
			author_album_song = strings.SplitN(path_author_album_song, "/", 3)

			if len(author_album_song) < 3 {
				return nil // файл лежит не в папке Автор/Альбом/, пропускаем
			}

			//заталкиваем в массив новый экземпляр структуры с уже заполненными полями
			musicFilesList = append(musicFilesList, musicFiles{
				item_zero:  strings.ToUpper(string([]rune(author_album_song[0])[0])),
				item_one:   author_album_song[0],
				item_two:   author_album_song[1],
				item_three: strings.TrimSuffix(author_album_song[2], filepath.Ext(author_album_song[2])),
				item_four:  path_author_album_song,
			})

			return nil
		},
	)

	if err != nil {
		log.Fatal("Error walking the path: ", err)
	}

	//на основе всей музыки что получили - отправляем все в бд на генерацию айдишников и разложению по таблице
	//но для начала обнулим все поля file_exists в бд, чтобы потом отметить только те что реально есть
	err = queries.UpdateMusicFilesSetAllFileNotExists(context.Background())

	if err != nil {
		log.Fatal("Update error: ", err)
	}

	var params db.MergeMusicFilesParams

	for _, song := range musicFilesList {
		params.FirstChars = append(params.FirstChars, song.item_zero)
		params.Performers = append(params.Performers, song.item_one)
		params.Albums = append(params.Albums, song.item_two)
		params.Songs = append(params.Songs, song.item_three)
		params.Paths = append(params.Paths, song.item_four)
	}

	err = queries.MergeMusicFiles(context.Background(), params)

	if err != nil {
		log.Fatal("Merge error: ", err)
	}

	err = queries.SetMusicID(context.Background())

	if err != nil {
		log.Fatal("SetMusicID error: ", err)
	}

}
