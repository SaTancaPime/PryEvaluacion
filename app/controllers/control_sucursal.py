from app.database.db import get_connection

class ControlSucursal:
    @staticmethod
    def obtener_sucursales():
        try:
            sql = """
                select id_sucursal, nombre from sucursal where estado = true
            """

            conexion = get_connection()
            sucursales = []
            with conexion.cursor() as cursor:
                cursor.execute(sql)
                sucursales = cursor.fetchall()
            conexion.close()
            
            return sucursales
        except Exception as e:
            print(f"Error al obtener sucursales: {e}")
            return None    