from app.database.db import get_connection

class ControlIncidente:
    @staticmethod
    def obtener_tipos_incidente():
        try:
            sql = """
                select id_tipoincidente, nombre_tipo, penalizacion_empleado, penalizacion_area from tipo_incidente
            """

            conexion = get_connection()
            tipos_incidente = []
            with conexion.cursor() as cursor:
                cursor.execute(sql)
                tipos_incidente = cursor.fetchall()
            conexion.close()
            
            return tipos_incidente
        except Exception as e:
            print(f"Error al obtener tipos de incidente: {e}")
            return None
        
    @staticmethod
    def agregar_incidente_cliente(id_cliente, evidencia, descripcion, id_empleado, id_tipo_incidente, id_area, id_sucursal):
        try:
            sql = """
                SELECT sp_insertar_incidente_cliente(
                    p_id_cliente := %s,
                    p_evidencia := %s,
                    p_descripcion := %s,
                    p_id_empleado_reportado := %s,
                    p_id_tipo_incidente := %s,
                    p_id_area := %s,
                    p_id_sucursal := %s
                );
            """
            
            conexion = get_connection()
            incidente = -1
            with conexion.cursor() as cursor:
                cursor.execute(sql, (id_cliente, evidencia, descripcion, id_empleado, id_tipo_incidente, id_area, id_sucursal))
                incidente = cursor.fetchone()[0]
            conexion.commit()
            conexion.close()
            
            return incidente
        except Exception as e:
            print(f"Error al agregar incidente (cliente): {e}")
            return None
        
    @staticmethod
    def agregar_incidente_empleado(id_empleado, evidencia, descripcion, id_empleado_reportado, id_tipo_incidente, id_area, id_sucursal):
        try:
            sql = """
                SELECT sp_insertar_incidente_empleado(
                    p_id_empleado := %s,
                    p_evidencia := %s,
                    p_descripcion := %s,
                    p_id_empleado_reportado := %s,
                    p_id_tipo_incidente := %s,
                    p_id_area := %s,
                    p_id_sucursal := %s
                );
            """
            
            conexion = get_connection()
            incidente = -1
            with conexion.cursor() as cursor:
                cursor.execute(sql, (id_empleado, evidencia, descripcion, id_empleado_reportado, id_tipo_incidente, id_area, id_sucursal))
                incidente = cursor.fetchone()[0]
            conexion.commit()
            conexion.close()
            
            return incidente
        except Exception as e:
            print(f"Error al agregar incidente (empleado): {e}")
            return None