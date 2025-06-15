from app.database.db import get_connection

class ControlAsistencia:
    @staticmethod
    def registrar_asistencia(id_empleado, hora_actual):
        try:
            sql = """
                select registrar_asistencia(
                    p_id_empleado := %s,
                    p_hora_actual := %s
                )
            """
            
            conexion = get_connection()
            respuesta = 0
            with conexion.cursor() as cursor:
                cursor.execute(sql, (id_empleado, hora_actual))
                respuesta = cursor.fetchone()[0]
            conexion.commit()
            conexion.close()
            
            return respuesta
        except Exception as e:
            print(f"Error al agregar entrada: {e}")
            return None    