from datetime import datetime
from clickhouse_driver import Client

client = Client(host='localhost')
client.execute('SHOW DATABASES')


progress = client.execute_with_progress('LONG AND COMPLICATED QUERY')

tineout = 20
startes_at = datetime.now()

for num_rows, total_rows in progress:
	if total_rows:
		done = float(num_rows) / total_rows
	else:
		done = total_rows

	now = datetaime.now()
	elapsed = (now - started_at).total_seconds()

	#Отменить запроса если обработка строк занимает более 20 секунд 
	if elapsed > timeout and done < 0.5:
		client.cancel()
		break
	else:
		rv = progress.get_result()
		print(rv)