import pyqtgraph as qt
import pyqtgraph.exporters
import numpy as np 
from clickhouse_driver import Client
from task1_1_var1 import count_of_nums 
from task1_1_var1 import count_of_iters 
from colors import colors 
import sys

the_title = "pyqtgraph plot"

def get_data(id_, client):
	buf = []
	low_buf = client.execute('SELECT num_%s FROM practice.numbers'%id_)
	for i in range(10):
		buf.append(low_buf[i][0])
	return buf


def graph(nums):
	x = range(0, count_of_iters)
	plt = qt.plot()
	plt.showGrid(x=True, y=True)
	plt.addLegend()
	plt.setLabel('left', 'Value', units='V') 
	plt.setLabel('bottom', 'Time', units='s') 
	plt.setXRange(0, count_of_iters+1) 
	plt.setYRange(0, 200) 
	plt.setWindowTitle('pyqtgraph plot')

	c = []
	for i in range(count_of_nums):
		c.append(plt.plot(x, nums[i], symbol=i+1, pen=colors[i], symbolPen=colors[i], symbolBrush=0.1, name=str(i+1)))
		#c.append(plt.plot(x, nums[i], pen='%s'%colors[i], symbol=str(i+1) , symbolPen='%s'%colors[i], symbolBrush=0.2, name='num_%'%(i+1)))
	#c1 = plt.plot(x, y, pen='b', symbol='x' , symbolPen='b', symbolBrush=0.2, name='red') 
	#c2 = plt.plot(x, y2, pen='r', symbol='o' , symbolPen='r', symbolBrush=0.2, name='blue')
	


def main():
	
	client = Client('localhost')  	# Подключение к серверу.
	
	nums = []
	for i in range(count_of_nums):
		nums.append(get_data(i+1, client))  
	print(*nums, sep='\n')

	graph(nums)
	if sys.flags.interactive != 1 or not hasattr(qt.QtCore, 'PYQT_VERSION'): qt.QtGui.QApplication.exec_()


if __name__ == '__main__':
	main()