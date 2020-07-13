from time import sleep
import time
from datetime import datetime
from clickhouse_driver import Client
from random import randint
import subprocess
from subprocess import Popen
import sys
import paint
import flask
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify
import threading
from threading import Thread
import _thread
import json


check = 0       # переменная для контроля доступа к БД  

client = Client('localhost')

app = flask.Flask(__name__)
app.config["DEBUG"] = True

values = [0, datetime.today().strftime("%Y-%m-%d %H:%M:%S"),
    randint(1, 10), 
    randint(1, 10), 
    randint(1, 10),
    randint(1, 10), 
    randint(1, 10)]

columns = ['id_iter', 'time_', 'num_1', 'num_2', 'num_3', 'num_4', 'num_5']


def table_init(client):
	client.execute('DROP DATABASE IF EXISTS practice') 
	client.execute('CREATE DATABASE practice')
	client.execute('CREATE TABLE practice.numbers('
						'id_iter Int32, time_ String, num_1 Int32, '
						'num_2 Int32, num_3 Int32, '
						'num_4 Int32, num_5 Int32)'
						'ENGINE = MergeTree ORDER BY time_')


def put_to_table(client, buf, columns):
    values = str(buf[0]) + """, '""" + str(buf[1]) + """'"""
    names = 'id_iter'
    for i in range(1, len(columns)):
        names += ', ' + columns[i]
    for i in range(2, len(buf)):
        values += ', ' + str(buf[i]) 
    query = 'INSERT INTO practice.numbers ('+names+') VALUES ('+values+')'
    print(query)
    client.execute(query)
    #k = client.execute('SELECT * FROM practice.numbers')
    #if k: print('Successfully added')


def db():
    global client
    global check
    #global api_flow
    #global values
    table_init(client)
    put_to_table(client, values, columns)

    #while True:
    for i in range(10):
        check = 1   # доступ к бд открыт
        sleep(1)
        #print(time.time())
        check = 0   # доступ к бд закрыт
        data = client.execute('SELECT * FROM practice.numbers WHERE id_iter = '+str(i))
        values[0] = data[0][0] + 1
        values[1] = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        for i in range(2, len(values)):
            values[i] += 3 * data[0][0]
        put_to_table(client, values, columns)
        #print(time.time())


class Db(Thread):
        
    def __init__(self):
        """Инициализация потока"""
        Thread.__init__(self)
        self.name = "DB"
    
    def run(self):
        """Запуск потока"""
        db()


@app.route('/', methods=['GET'])
def home():
    return '''
            <h1>Добро пожаловать в базу данных</h1>
            <p>Автоматически была создана таблица стартовых данных</p>
            <p>Чтобы просмотреть таблицу и график значений, перейдите http://127.0.0.1:5000/all</p>
            <p>Чтобы добавить новое число, перейдите http://127.0.0.1:5000/form </p>
            
           '''


@app.route('/all', methods=['GET'])
def show_entries(a):
    global client
    global columns
    data = client.execute('SELECT * FROM practice.numbers ORDER BY time_')
    print('Необработанные данные из таблицы:', data)
    entries = []
    buf = []
    for i in range(len(data)):
        buf.append([])
        for j in range(len(data[i]) - 2):
            buf[i].append([])
            buf[i][j].append(columns[j+2])
            buf[i][j].append(data[i][j+2])
        entries.append({})
        entries[i]['index'] = data[i][0]
        entries[i]['time'] = data[i][1]
        entries[i]['nums'] = buf[i]
        print(i, ' запись: ', entries[i])
    entries = json.dumps(entries)
    print('Обработанные данные: ', entries)
    return '''<html>
                <head>
                    <title>All</title>
                    <script src="https://cdn.jsdelivr.net/npm/vue/dist/vue.js"></script>
                </head>
                <body>
                    <div id="app">
                        <div v-for="data in restData" :key="data.index">
                            Index:{{data.index}} Time:{{data.time}} <span v-for="num in data.nums" :key="num[1]">{{num[0]}}: {{num[1]}}</span>
                        </div>
                    </div>

                    <script>
                        var app = new Vue({
                            el: '#app',
                            data: {
                                restData: '''+entries+''',
                            }
                        })
                    </script>
                </body>
            </html>'''
    

@app.route('/pupka', methods=['GET'])
def shrek():
    global client
    data = client.execute('SELECT * FROM practice.numbers ORDER BY time_')
    return str(data)


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


@app.route('/form', methods=['GET'])
def form():
    return ''' 
        <html>
            <head>
                <title>Добавить новую переменную</title>
                <script src="https://cdn.jsdelivr.net/npm/vue/dist/vue.js"></script>
            </head>
            <body>
                <h1>Добавить новую переменную</h1>
                <pre>Имя переменной:          Начальное значение:</pre>
                <div id="app">
                    <form>
                        <input type="text" v-model="formInput1">
                        <input type="text" v-model="formInput2">
                        <button @click.prevent="sendData(formInput1, formInput2)">Добавить</button>
                    </form>
                </div>

                <script>
                    var app = new Vue({
                    el: '#app',
                    data: {
                            formInput1: "",
                            formInput2: ""
                        },
                    methods: {
                            sendData(name, value){
                                fetch(`http://127.0.0.1:5000/add?name=${name}&value=${value}`)
                                         }
                                }
                        })
                </script>
            </body>
        </html>
        '''


@app.route('/add', methods=['POST'])
def add_num():
    global client
    global check
    global values
    while True:
        if check:
            query_parameters = request.args
            name = query_parameters.get('name')
            print(name)
            
            value = query_parameters.get('value')
            client.execute('ALTER TABLE practice.numbers ADD COLUMN '+ name +' Int32')
            client.execute('UPDATE practice.numbers SET '+ name +' = '+ str(value) +' WHERE practice.numbers.id_iter = '+id)
            values[name] = int(value)
            break
    
    return '''Num added!'''


if __name__ == '__main__':
    #db()
    #db_thread = Db()
    #api_thread = Api()
    #db_thread.start()
    #api_thread.start()
    _thread.start_new_thread(db, ())
    app.run()
    #sleep(10)
    #print(client.execute('SELECT * FROM practice.numbers'))
