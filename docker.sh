# 1. Остановить и удалить контейнер
docker stop ararararagi-bot
docker rm -f ararararagi-bot

# 2. Пересобрать образ (из папки бота!)
cd /home/g1ts0/Github/Ararararagi_bot
docker build -t ararararagi-bot .

# 3. Запустить контейнер с пробросом music
docker run -d --name ararararagi-bot \
  --restart unless-stopped \
  -e TZ=Asia/Tokyo \
  -v /home/g1ts0/Github/Ararararagi_bot/assets:/app/assets \
  --add-host=host.docker.internal:host-gateway \
  ararararagi-bot
