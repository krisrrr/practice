from time import sleep
from datetime import datetime
from clickhouse_driver import Client
from random import randint
import subprocess
from subprocess import Popen
import sys
import task1_2_var1
from flask import request, jsonify

count_of_nums = 10  # число чисел
count_of_iters = 10

def table_init(client, names=None):
	if names == None:     
		client.execute('CREATE DATABASE practice')
		client.execute('CREATE TABLE practice.numbers('
						'id_iter Int32, time_ String, num_1 Int32, '
						'num_2 Int32, num_3 Int32, '
						'num_4 Int32, num_5 Int32, '
						'num_6 Int32, num_7 Int32, '
						'num_8 Int32, num_9 Int32, '
						'num_10 Int32)'
						'ENGINE = MergeTree ORDER BY time_')
	else:
		pass
	k = client.execute('SHOW TABLES IN practice')
	if k: print('Database and table successfully created')

def put_to_table(client, buf):
	client.execute('INSERT INTO practice.numbers ('
						'id_iter, time_, num_1, num_2, num_3, num_4, num_5,'
						'num_6, num_7, num_8, num_9, num_10)'
						'VALUES', [(buf[0], buf[1], buf[2], buf[3], buf[4], buf[5], buf[6], buf[7], buf[8], buf[9], buf[10], buf[11])])
	k = client.execute('SELECT * FROM practice.numbers')
	if k: print('Successfully added')


def drop_database(client):
	client.execute('DROP DATABASE IF EXISTS practice')
	
def __main__():
	client = Client('localhost')  	# Подключение к серверу.
	buf = []                     	# Создание буфферного списка.
	drop_database(client)		  	# Удаление базы данных, если она существует, во избежание накопления данных при повторном выполнении программы.
	
	


	table_init(client)			  	# Создание базы данных и таблицы.

	buf.append(1)														# Добавление номера итерации - 1, потому что первая итерация.
	buf.append(datetime.today().strftime("%Y-%m-%d %H:%M:%S"))			# Добавление времени итерации.
	while len(buf) < count_of_nums + 2:									# Цикл, в котором происходит заполнение оставшейся части списка
		b = randint(1, 15)												# неповторяющимися случайными числами от 1 до 15.
		#print(type(b))
		if b not in buf:
			buf.append(b)
	#print(*buf, '.\n', sep='\n')
	put_to_table(client, buf)		# Занесение в базу первой итерации.
	#print(type(buf[0][0]))
	j = 2

	while j <= count_of_iters:														# Цикл итераций, начиная со 2. В цикле: 
		sleep(1)														#  обновляется:
		buf[0] = j														#   - номер итерации
		buf[1] = datetime.today().strftime("%Y-%m-%d %H:%M:%S")			#   - время итерации
		for i in range(2, count_of_nums + 2):							#   - каждое число (каждую итерацию оно умножается на 2)
			buf[i] = buf[i] + 2*j + i
		j += 1
		put_to_table(client, buf)	# Занесение в базу обновлённого списка
		print(*buf, '\n', sep=' ')	

	print(client.execute('SELECT * FROM practice.numbers'))
	#drop_database(client)
	#task1_2_var1.painting()
	print(jsonify(client.execute('SELECT * FROM practice.numbers')))

if __name__ == '__main__':
	__main__()
	
