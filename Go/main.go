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

func main() {
	token := os.Getenv("token")

	var base_url string = "https://api.telegram.org/bot" + token

	var url string

	//апи простого знакомства с телегой, рукопожатие
	url = base_url + "/getMe"

	//отправляем запрос и полчаем ответ
	response, response_error := http.Get(url)

	//проверяем ошибки
	if response_error != nil {
		//log выводит через принт время и наш ошибку, а также в зависимости от вызванного метода - делает os.exit с соответствующим кодом
		log.Fatal("Connection error: ", response_error)
	}

	// выполнится в самом конце main - чтобы не копились соединения
	defer response.Body.Close()

	//читаем из сетевого соединения (из потока) тело ответа уже находится в json формате, только весь этот json тут - в байтах
	response_body_byte, response_body_error := io.ReadAll(response.Body)

	//проверяем ошибки
	if response_body_error != nil {
		//log выводит через принт время и наш ошибку, а также в зависимости от вызванного метода - делает os.exit с соответствующим кодом
		log.Fatal("Reading body error: ", response_body_error)
	}

	var CurBodyGetme BodyStructGetMe

	//переводим поток байт сразу в структуру минуя состоние string чтобы не писать свой json парсер
	err := json.Unmarshal(response_body_byte, &CurBodyGetme)

	//проверяем ошибки
	if err != nil {
		//log выводит через принт время и наш ошибку, а также в зависимости от вызванного метода - делает os.exit с соответствующим кодом
		log.Fatal("JSON error: ", err)
	}

	//номер обработанного события - конечно начинаем с нуля
	var offset int64 = 0

	//бесконечный цикл получения обновлений. Поллинг - запросил, подождал 30 секунд для получения события и запросил снова
	//апи получения обновлений по боту
	for {

		url = base_url + "/getUpdates?offset=" + strconv.FormatInt(offset, 10) + "&timeout=30"

		response, response_error := http.Get(url)

		if response_error != nil {
			log.Println("Update error: ", response_error)
			time.Sleep(3 * time.Second)
			continue
		}

		//получаем тело в байтах. само тело имеет вид { "ok": true, "result": [...] }
		response_body_byte, response_body_error := io.ReadAll(response.Body)

		//проверяем ошибки
		if response_body_error != nil {
			//log выводит через принт время и наш ошибку, а также в зависимости от вызванного метода - делает os.exit с соответствующим кодом
			log.Fatal("Reading body error: ", response_body_error)
		}

		//стрктура переменной кула положим тело
		var CurBodyGetUpdates BodyStructGetUpdates

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

		//переводим тело из байтов в нашу структуру
		err := json.Unmarshal(response_body_byte, &CurBodyGetUpdates)

		if err != nil {
			log.Fatal("JSON error: ", err)
		}

		var answer []UserResultStructGetUpdates = CurBodyGetUpdates.Result

		//телеграм может в теле вернуть сразу все события, поэтому проходимся по каждому
		for _, update := range answer {

			var update_id = update.UpdateId

			fmt.Printf("%+v\n", update_id)

			offset = update_id + 1
		}

		response.Body.Close()
	}

}
