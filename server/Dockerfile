FROM python:3.9

WORKDIR /app/src/server

#RUN pip  --trusted-host pypi.org --trusted-host files.pythonhosted.org install -r /app/src/requirements.txt
COPY ./requirements.txt /app/src/
RUN pip  install -r /app/src/requirements.txt

COPY ./config.json /app/src/server/
COPY async_server.py /app/src/server/
CMD [ "python3", "-u", "async_server.py"]
#docker run -d -p 9191:9191 -v "$(pwd)/../csv_files:/app/src/csv_files" csv2restapi:01
#docker build . -t csv2restapi:01

#Stop all running containers:
#docker stop $(docker ps -q)

#Remove all stopped containers:
#docker rm $(docker ps -a -q)

#Remove all Docker images:
#docker rmi $(docker images -q)