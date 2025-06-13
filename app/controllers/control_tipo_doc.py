from app.database.db import get_connection

class ControlTipoDoc:
    @staticmethod
    def obtener_tipo_doc():
        try:
            sql = """
                select * from tipo_documento
            """

            conexion = get_connection()
            tipos_doc = []
            with conexion.cursor() as cursor:
                cursor.execute(sql)
                tipos_doc = cursor.fetchall()
            conexion.close()
            
            return tipos_doc
        except Exception as e:
            print(f"Error al obtener areas: {e}")
            return None 