# PostgreSQL kommunikation
import psycopg2

def get_connection():
    return psycopg2.connect(
    host="localhost",
    database="ragdb",
    user="postgres",
    password="postgres"
)