#################################
##                             ##
##   Dockerfile for practice   ##
##                             ##
#################################

FROM ubuntu:latest

MAINTAINER KristinaRozina

RUN mkdir /app && cd /app

WORKDIR /app

# Установка локали
RUN apt-get update && \ 
	apt-get install -y apt-utils && \
	apt-get -y install locales && \
	sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
	locale-gen

# Установка базы данных Clickhouse:
RUN apt-get update && \
	apt-get install -y clickhouse-client clickhouse-server && \
	apt-get install -y python3.8 && \
	apt-get install -y python3-pip

# Установка clickhouse-driver:
RUN pip3 install clickhouse-driver 

# Установка QT
RUN pip3 install pyqtgraph numpy 

RUN pip3 install flask && pip3 install multiprocessing

COPY ./ __main__.py 
COPY ./ mypaint.py 
COPY ./ colors.py 
COPY ./ templates/
COPY ./ static/

CMD ["python3", "./__main__py"] 
