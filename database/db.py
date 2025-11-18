import mysql.connector

def create_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='4080',  
        database='SecureExamProctoring'
    )
