import mysql.connector

# Inicializamos la conexion con nuestra base de datos

database = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    password = '',
    database = 'registros_h'
)