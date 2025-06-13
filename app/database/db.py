from app.config import Config
import psycopg2

def get_connection():
    try:
        connection = psycopg2.connect(
            host=Config.POSTGRES_HOST,
            port=5432,
            user=Config.POSTGRES_USER,
            password=Config.POSTGRES_PASSWORD,
            database=Config.POSTGRES_DB
        )
        return connection
    except Exception as e:
        print(f"Error en la conexión con la BD: {e}")
        return None
