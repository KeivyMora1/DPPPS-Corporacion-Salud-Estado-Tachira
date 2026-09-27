from db import get_connection
conn = get_connection()
cursor = conn.cursor()
cursor.execute("SHOW COLUMNS FROM voceria_item LIKE 'centro_dispensador'")
result = cursor.fetchone()
print('Exists in voceria_item:', result)
cursor.close()
conn.close()