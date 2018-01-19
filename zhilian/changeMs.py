import time


def change_ms(time):
    date = time.mktime(time.strptime(d, '%Y-%m-%d %H:%M:%S')) * 1000
    return date
