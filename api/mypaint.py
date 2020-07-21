import pyqtgraph as qt
import pyqtgraph.exporters
import numpy as np 
from clickhouse_driver import Client
from colors import colors 
import sys
from random import randint

nums_count = 0  # количество чисел
iters_count = 0

the_title = "pyqtgraph plot"

def get_data_one(id_, client):
	buf = []
	low_buf = client.execute('SELECT num_%s FROM practice.numbers'%id_)
	for item in low_buf:
		buf.append(item[0])
	return buf


def get_nums_count(client):
	global nums_count
	a = client.execute('SELECT * FROM practice.numbers ORDER BY id_iter DESC LIMIT 1')
	nums_count = len(a[0]) - 2
	

def get_x(client):
	x_ = client.execute('SELECT id_iter FROM practice.numbers')
	x = []
	global iters_count
	for item in x_:
		x.append(item[0])
	iters_count = len(x)
	return x


def graph(nums, client):
	x = get_x(client)
	plt = qt.plot()
	plt.showGrid(x=True, y=True)
	plt.addLegend()
	plt.setLabel('left', 'Value', units='V') 
	plt.setLabel('bottom', 'Time', units='s') 
	plt.setXRange(0, 10) 
	plt.setYRange(0, 200) 
	plt.setWindowTitle('Chart')

	c = []
	for i in range(nums_count):
		color = randint(1, len(colors))
		c.append(plt.plot(
			x, 
			nums[i], 
			symbol=i+1, 
			pen=color, 
			symbolPen=color, 
			symbolBrush=0.1, 
			name=str(i+1)))

	qt.QtGui.QApplication.processEvents()	
	

def get_data_all(a, client):
	nums = []
	for i in range(a):
		nums.append(get_data_one(i+1, client))  
	return nums


def painting():
	
	client = Client('localhost') 	# Подключение к серверу.
	get_nums_count(client)
	graph(get_data_all(nums_count, client), client)

	if sys.flags.interactive != 1 or not hasattr(qt.QtCore, 'PYQT_VERSION'): qt.QtGui.QApplication.exec_()

if __name__ == "__main__":
	painting()
