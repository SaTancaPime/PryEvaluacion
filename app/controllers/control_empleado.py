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
        
    @staticmethod
    def obtener_empleados(id_sucursal, id_area):
        try:
            sql = """
                select e.id_empleado, e.nombre || ' ' || e.apepat || ' ' || e.apemat as nombre 
                from empleado e
                inner join rol r on e.id_rol = r.id_rol
                inner join area a on r.id_area = a.id_area
                where e.id_sucursal = %s and a.id_area = %s and e.estado = true
            """

            conexion = get_connection()
            empleados = []
            with conexion.cursor() as cursor:
                cursor.execute(sql, (id_sucursal, id_area))
                empleados = cursor.fetchall()
            conexion.close()
            
            return empleados
        except Exception as e:
            print(f"Error al obtener empleados: {e}")
            return None