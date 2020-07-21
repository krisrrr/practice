from time import sleep
import time
from datetime import datetime
from clickhouse_driver import Client
from random import randint
import sys
import flask
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify
import json
from multiprocessing import Process
import mypaint
from time_of_query import get_time


client = Client('localhost')

app = flask.Flask(__name__)

columns = {1: 'id_iter', 2: 'time_', 3: 'num_1', 4: 'num_2', 5: 'num_3', 6: 'num_4', 7: 'num_5'}


def table_init(client):
	client.execute('DROP TABLE IF EXISTS numbers')
	client.execute('CREATE TABLE numbers('
						'id_iter Int32, time_ String, num_1 Int32, '
						'num_2 Int32, num_3 Int32, '
						'num_4 Int32, num_5 Int32)'
						'ENGINE = MergeTree ORDER BY time_')


def put_to_table(client, values):
    global columns
    names_list = client.execute("SELECT name FROM system.columns WHERE type = 'Int32' " )
    buf = str(values[0]) + """, '""" + str(values[1]) + """'"""
    names = 'id_iter, time_'
    for i in range(1, len(names_list) - 8):
        names += ', ' + names_list[i][0]
    for i in range(2, len(values)):
        buf += ', ' + str(values[i]) 
    query = 'INSERT INTO numbers ('+names+') VALUES ('+buf+')'
    client.execute(query)


def db():
    values = [1, datetime.today().strftime("%Y-%m-%d %H:%M:%S"),
        randint(1, 20), 
        randint(1, 20), 
        randint(1, 20),
        randint(1, 20), 
        randint(1, 20)]
    global client
    table_init(client)
    put_to_table(client, values)
    k = 1
    while True:
        values.clear()
        sleep(1)
        data = client.execute('SELECT * FROM numbers WHERE id_iter = '+str(k))
        values.append(data[0][0] + 1)
        values.append(datetime.today().strftime("%Y-%m-%d %H:%M:%S"))
        for i in range(2, len(data[0])):
            values.append(data[0][i] + 3 * data[0][0])
        put_to_table(client, values)
        k += 1
        

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/all', methods=['GET'])
def show_entries():
    global client
    global columns
    data = client.execute('SELECT * FROM numbers ORDER BY id_iter')
    times =  datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    return render_template(
        'show_entries.html', 
        time=times, 
        names=columns,
        data=data,
        iters=len(data),
        items_count=len(columns) - 2)
    

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


@app.route('/new-var', methods=['POST', 'GET'])
def new_num():
    global client
    global columns
    if request.method == 'POST':
        name = request.form['var']
        value = request.form['val']
        columns[len(columns) + 1] = name

        max_id = client.execute('SELECT max(id_iter) FROM numbers ')
        last_iter = client.execute('SELECT * FROM numbers WHERE id_iter =' + str(max_id[0][0]))
        last_iter_str = str(last_iter[0][0]) + ', ' + "'" + last_iter[0][1] + "'"
        for i in range(2, len(last_iter[0])): 
            last_iter_str += ', '+ str(last_iter[0][i])
        last_iter_str += ', ' + value
        names = columns[1]
        for key in columns:
            if key > 1:
                names += ', ' + columns[key]
        client.execute('ALTER TABLE numbers ADD COLUMN '+ name +' Int32') 
        query = 'INSERT INTO numbers ('+ names +') VALUES ('+ last_iter_str +')'
        client.execute(query)
        return redirect('/all')
    else:
        return render_template('new_add.html')


@app.route('/graph', methods=['GET'])
def graphic():
    mypaint.painting()
    return render_template('index.html')


@app.route('/time-of-query', methods=['POST', 'GET'])
def get_time_of_query():
    global client
    if request.method == 'POST':
        input_names = request.form['names']
        names = [i for i in input_names.split()]
        time_of_query = get_time(names, client)
        return render_template(
            'time.html', 
            names=input_names,
            time=time_of_query)
    else:
        return render_template('get_time.html')


if __name__ == '__main__':
    proc = Process(target=db)
    proc.start()
    app.run()
