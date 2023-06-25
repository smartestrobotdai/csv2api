docker stop $(docker ps -q)
docker rm $(docker ps -a -q)
docker build . -t csv2restapi:01
docker run -d -p 9191:9191 -v "$(pwd)/../files:/app/src/files" csv2restapi:01
sleep 5

#curl "http://localhost:9191/api/v1/test1.csv?nrows=10&startpos=0&columns=Id%2CName&delimiter=%20"
curl "http://localhost:9191/api/v1/test1.json?nrows=10&startpos=0"


CONTAINER_NAME=$(docker ps|tail -1|awk '{print $NF}')
docker logs -f ${CONTAINER_NAME}

