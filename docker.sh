# 1. Остановить и удалить контейнер
docker stop ararararagi-bot
docker rm -f ararararagi-bot

# 2. Запустить FlareSolverr если ещё не запущен
if [ ! "$(docker ps -q -f name=flaresolverr)" ]; then
    docker run -d \
      --name flaresolverr \
      --restart unless-stopped \
      -p 8191:8191 \
      ghcr.io/flaresolverr/flaresolverr:latest
fi

# 3. Пересобрать образ (из папки бота!)
cd /home/g1ts0/Github/Ararararagi_bot
docker build -t ararararagi-bot .

# 4. Запустить контейнер с пробросом music
docker run -d --name ararararagi-bot \
  --restart unless-stopped \
  -e TZ=Asia/Tokyo \
  -v /home/g1ts0/Github/Ararararagi_bot/assets:/app/assets \
  --add-host=host.docker.internal:host-gateway \
  --link flaresolverr:flaresolverr \
  ararararagi-bot
