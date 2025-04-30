import pymysql

db = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='car_server_db',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)
