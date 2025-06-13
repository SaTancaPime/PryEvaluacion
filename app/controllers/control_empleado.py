from app.database.db import get_connection

class ControlEmpleado:
    @staticmethod
    def buscar_empleado(id_tipo_doc, nro_doc):
        try:
            sql = """
                SELECT sp_buscar_empleado(
                    p_id_tipo_documento := %s,
                    p_nro_documento := %s
                );
            """
            conexion = get_connection()
            empleado = -1
            with conexion.cursor() as cursor:
                cursor.execute(sql, (id_tipo_doc, nro_doc))
                empleado = cursor.fetchone()[0]
            conexion.close()
            return empleado
        except Exception as e:
            print(f"Error al buscar empleado: {e}")
            return -1