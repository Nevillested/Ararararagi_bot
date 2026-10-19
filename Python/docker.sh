#!/bin/bash
docker stop ararararagi-bot 2>/dev/null || true
docker rm -f ararararagi-bot 2>/dev/null || true

cd /mnt/tank/projects/Ararararagi_bot/Python
docker build -t ararararagi-bot .

docker run -d --name ararararagi-bot \
  --restart unless-stopped \
  -e TZ=Asia/Tokyo \
  -v /mnt/tank/projects/Ararararagi_bot/assets:/app/assets \
  --add-host=host.docker.internal:host-gateway \
  --link flaresolverr:flaresolverr \
  ararararagi-bot
