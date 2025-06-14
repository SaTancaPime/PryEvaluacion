from app.database.db import get_connection

class ControlArea:
    @staticmethod
    def obtener_areas():
        try:
            sql = """
                select id_area, nombre from area where estado = true
            """

            conexion = get_connection()
            areas = []
            with conexion.cursor() as cursor:
                cursor.execute(sql)
                areas = cursor.fetchall()
            conexion.close()
            
            return areas
        except Exception as e:
            print(f"Error al obtener areas: {e}")
            return None      