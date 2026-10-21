package main

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"strconv"
	"time"
)

type UserResultStructGetMe struct {
	Id                            int64  `json:"id"`
	Is_bot                        bool   `json:"is_bot"`
	First_name                    string `json:"first_name"`
	Username                      string `json:"username"`
	Can_join_groups               bool   `json:"can_join_groups"`
	Can_read_all_group_messages   bool   `json:"can_read_all_group_messages"`
	Supports_inline_queries       bool   `json:"supports_inline_queries"`
	Supports_guest_queries        bool   `json:"supports_guest_queries"`
	Can_connect_to_business       bool   `json:"can_connect_to_business"`
	Has_main_web_app              bool   `json:"has_main_web_app"`
	Has_topics_enabled            bool   `json:"has_topics_enabled"`
	Allows_users_to_create_topics bool   `json:"allows_users_to_create_topics"`
	Can_manage_bots               bool   `json:"can_manage_bots"`
	Supports_join_request_queries bool   `json:"supports_join_request_queries"`
}

type BodyStructGetMe struct {
	Ok     bool                  `json:"ok"`
	Result UserResultStructGetMe `json:"result"`
}

type FromStr struct {
	Id            int64  `json:"id"`
	Is_bot        bool   `json:"is_bot"`
	First_name    string `json:"first_name"`
	Username      string `json:"username"`
	Language_code string `json:"language_code"`
}

type ChatStr struct {
	Id         int64  `json:"id"`
	First_name string `json:"first_name"`
	Username   string `json:"username"`
	Type       string `json:"type"`
}

type EntitiesStr struct {
	Offset int64  `json:"offset"`
	Length int64  `json:"length"`
	Type   string `json:"type"`
}

type MessageStr struct {
	MessageId int64         `json:"message_id"`
	From      FromStr       `json:"from"`
	Chat      ChatStr       `json:"chat"`
	Date      int64         `json:"date"`
	Text      string        `json:"text"`
	Entities  []EntitiesStr `json:"entities"`
}

type UserResultStructGetUpdates struct {
	UpdateId int64      `json:"update_id"`
	Message  MessageStr `json:"message"`
}

type BodyStructGetUpdates struct {
	Ok     bool                         `json:"ok"`
	Result []UserResultStructGetUpdates `json:"result"`
}

var base_url string = "https://api.telegram.org/bot" + os.Getenv("TELEGRAM_TOKEN")

func callToTG(method string) ([]byte, error) {

	response, response_error := http.Get(base_url + method)

	if response_error != nil {
		return nil, response_error
	} else {
		defer response.Body.Close()
		return io.ReadAll(response.Body)
	}

}

// апи простого знакомства с телегой, рукопожатие
func getMe() error {

	var get_body_byte, err = callToTG("/getMe")

	if err != nil {
		return err
	} else {

		var body BodyStructGetMe

		//переводим поток байт сразу в структуру минуя состоние string чтобы не писать свой json парсер
		err := json.Unmarshal(get_body_byte, &body)

		//проверяем ошибки
		if err != nil {
			return err
		}

		return nil

	}

}

// апи получения обновлений по боту
func getUpdates() {

	//номер обработанного события - конечно начинаем с нуля
	var offset int64 = 0

	//бесконечный цикл получения обновлений. Поллинг - запросил, подождал 30 секунд для получения события и запросил снова
	for {

		var get_body_byte, err = callToTG("/getUpdates?offset=" + strconv.FormatInt(offset, 10) + "&timeout=30")

		if err != nil {
			log.Println("Update error: ", err)
			time.Sleep(3 * time.Second)
			continue
		} else {
			//стрктура переменной кула положим тело
			var CurBodyGetUpdates BodyStructGetUpdates

			//переводим тело из байтов в нашу структуру
			err := json.Unmarshal(get_body_byte, &CurBodyGetUpdates)

			if err != nil {
				log.Fatal("JSON error: ", err)
			}

			var answer []UserResultStructGetUpdates = CurBodyGetUpdates.Result

			//телеграм может в теле вернуть сразу все события, поэтому проходимся по каждому
			for _, update := range answer {

				var update_id = update.UpdateId

				offset = update_id + 1

				fmt.Println("Пришло сообщение от", update.Message.From.Id)

			}

		}

		/*пример ответа
		  {
		      "ok":true,
		      "result":
		      [
		          {
		              "update_id":146930112,
		              "message":
		              {
		                  "message_id":1,
		                  "from":
		                  {
		                      "id":1275894304,
		                      "is_bot":false,
		                      "first_name":"-",
		                      "username":"g1ts0",
		                      "language_code":"en"
		                  },
		                  "chat":
		                  {
		                      "id":1275894304,
		                      "first_name":"-",
		                      "username":"g1ts0",
		                      "type":"private"
		                  },
		                  "date":1792483988,
		                  "text":"/start",
		                  "entities":
		                  [
		                      {
		                          "offset":0,
		                          "length":6,
		                          "type":"bot_command"
		                      }
		                  ]
		              }
		          }
		      ]
		  }
		*/
	}

}
