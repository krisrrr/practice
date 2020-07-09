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
RUN apt-get update 
RUN apt-get install -y apt-utils
RUN apt-get -y install locales 
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen 
RUN locale-gen

# Установка базы данных Clickhouse:
RUN apt-get update
RUN apt-get install -y clickhouse-client clickhouse-server
RUN apt-get install -y python3.8 
RUN apt-get install -y python3-pip

# Установка clickhouse-driver:
RUN pip3 install clickhouse-driver

# Установка QT
RUN pip3 install pyqtgraph numpy
COPY ./ __main__.py 
COPY ./ task1_2_var1.py 
COPY ./ colors.py 


#ENTRYPOINT ["python3", "task1_1_var1.py"]
#CMD ["bash"]
#CMD ["python3", "practice"]
