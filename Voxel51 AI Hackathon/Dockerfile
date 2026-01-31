FROM mongo

ENV MONGO_INITDB_ROOT_USERNAME=username
ENV MONGO_INITDB_ROOT_PASSWORD=cc

COPY init-mongo.js /docker-entrypoint-initdb.d/

CMD ["mongod"]
