docker stop $(docker ps -q)
docker rm $(docker ps -a -q)
docker build . -t csv2restapi:01
docker run -d -p 9191:9191 -v "$(pwd)/./files:/app/files" csv2restapi:01
sleep 5

#curl "http://localhost:9191/api/v1/test1.csv?nrows=10&startpos=0&columns=Id%2CName&delimiter=%20"
#curl "http://localhost:9191/api/v1/test1.json?condition=doc1.str.contains%28%27FLA%27%29&nrows=10&startpos=0&output_orient=records"
#curl "http://localhost:9191/api/v1/test1.csv?condition=doc1.str.contains%28%27AAA%27%29%7Cdoc2.str.contains%28%27AAA%27%29%20&delimiter=%20&columns=Id%2CName"


CONTAINER_NAME=$(docker ps|grep csv2restapi|awk '{print $NF}')
docker logs -f ${CONTAINER_NAME}

