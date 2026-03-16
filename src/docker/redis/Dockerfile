FROM redis:7.2-bookworm

ARG REDIS_PORT

RUN apt-get update && apt-get install -y redis-tools

ENV REDIS_ENV custom

EXPOSE $REDIS_PORT

CMD ["redis-server", "/data/redis.conf"]
