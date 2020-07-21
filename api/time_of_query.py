from time import time
from clickhouse_driver import Client


def get_time(names_list, client):
    names = names_list[0]
    for i in range(1, len(names_list)):
        names += ', ' + names_list[i]
    time_before = time()
    client.execute('SELECT (' + names + ') FROM numbers')
    time_after = time()
    time_of_query = time_after - time_before
    return time_of_query