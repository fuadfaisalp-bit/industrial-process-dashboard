import sqlite3

conn = sqlite3.connect("database/process_data.db")
cursor = conn.cursor()

cursor.execute("""
SELECT *
FROM modbus_data
ORDER BY timestamp DESC
LIMIT 10
""")

rows = cursor.fetchall()

print("\nLatest 10 Records:\n")

for row in rows:
    print(row)

conn.close()