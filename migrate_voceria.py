import mysql.connector
from db import get_connection

conn = get_connection()
cursor = conn.cursor()

# Check if column exists in voceria
cursor.execute('''
    SELECT COLUMN_NAME 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'voceria' 
    AND COLUMN_NAME = 'centro_dispensador'
''')
result = cursor.fetchone()

if result:
    print('Column centro_dispensador already exists in voceria table')
else:
    print('Adding centro_dispensador column to voceria table...')
    cursor.execute('ALTER TABLE voceria ADD COLUMN centro_dispensador VARCHAR(100) AFTER parroquia')
    conn.commit()
    print('Column added successfully')

# Check if column exists in voceria_item (should be removed)
cursor.execute('''
    SELECT COLUMN_NAME 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'voceria_item' 
    AND COLUMN_NAME = 'centro_dispensador'
''')
result = cursor.fetchone()

if result:
    print('Removing centro_dispensador column from voceria_item table...')
    cursor.execute('ALTER TABLE voceria_item DROP COLUMN centro_dispensador')
    conn.commit()
    print('Column removed successfully')
else:
    print('Column centro_dispensador already removed from voceria_item table')

cursor.close()
conn.close()
print('Migration complete!')