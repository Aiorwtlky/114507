import sqlite3
conn = sqlite3.connect('device.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM devices WHERE device_serial = 'mdgcs001'")
print(cursor.fetchone())
conn.close()