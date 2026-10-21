package main

import (
	"ararararagi_bot/internal/db"
	"context"
	"log"
	"os"

	"github.com/jackc/pgx/v5/pgxpool"
)

func main() {

	var err = getMe()

	if err != nil {
		log.Fatal("GetMe error: ", err)
	} else {
		log.Println("GetMe success")
	}

	pg_connect, pg_con_error := pgxpool.New(context.Background(), os.Getenv("DATABASE_URL"))

	if pg_con_error != nil {
		log.Fatal("DB connect error: ", pg_con_error)
	}

	var queries = db.New(pg_connect)

	defer pg_connect.Close()

	//на этапе запуска бота подготовим данные для кнопок музыки, тк самой музыки очень много
	prepare_music_data(queries)

	//getUpdates()

}
