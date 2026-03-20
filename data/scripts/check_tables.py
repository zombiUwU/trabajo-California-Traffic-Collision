import sqlite3
# codigo para revisar las tablas disponibles en la base de datos .sqlite

# Conectarse al archivo .sqlite

conn = sqlite3.connect("switrs.sqlite")
# Para ver todas las tablas de la BD\
    
tables = conn.execute("""
SELECT name
FROM sqlite_master
WHERE type='table';
""").fetchall()

print("Tablas disponibles:")
for t in tables:
    print("-", t[0])

conn.close()