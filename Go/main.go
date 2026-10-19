package main

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
)

type UserResultStruct struct {
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

type BodyStruct struct {
	Ok     bool             `json:"ok"`
	Result UserResultStruct `json:"result"`
}

func main() {
	token := os.Getenv("token")

	var url string

	url = "https://api.telegram.org/bot" + token + "/getMe"

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

	var CurBody BodyStruct

	//переводим поток байт сразу в структуру минуя состоние string чтобы не писать свой json парсер
	err := json.Unmarshal(response_body_byte, &CurBody)

	//проверяем ошибки
	if err != nil {
		//log выводит через принт время и наш ошибку, а также в зависимости от вызванного метода - делает os.exit с соответствующим кодом
		log.Fatal("JSON error: ", err)
	}

	fmt.Println(CurBody.Ok)

	fmt.Printf("%+v\n", CurBody.Result)

}
