from app.database.db import get_connection
from datetime import datetime

class ControlJustificacion:
    @staticmethod
    def obtener_tipo_justificacion():
        try:
            sql = """
                select id_tipojustificacion, tipo from tipo_justificacion;
            """
            
            conexion = get_connection()
            tipos_justificacion = []
            with conexion.cursor() as cursor:
                cursor.execute(sql)
                tipos_justificacion = cursor.fetchall()
            conexion.close()
            
            return tipos_justificacion
        except Exception as e:
            print(f"Error al obtener tipos de justificación: {e}")
            return None
    
    @staticmethod
    def buscar_fechas_evento(id_empleado, evento):
        try:
            sql = """
                select fecha AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima' 
                from asistencia 
                where id_empleado = %s and (
                    (estado_entrada = %s and fecha >= current_date - interval '5 days' and fecha <= current_date)
                    or
                    (estado_entrada = '3' and fecha >= current_date)
                );
            """
            
            conexion = get_connection()
            fechas = []
            with conexion.cursor() as cursor:
                cursor.execute(sql, (id_empleado, evento))
                fechas = cursor.fetchall()
            conexion.close()
            
            return [fecha[0] for fecha in fechas]
        except Exception as e:
            print(f"Error al obtener las fechas de asistencia: {e}")
            return None
    
    @staticmethod
    def agregar_justificacion(id_tipo_justificacion, id_empleado, tipo_evento, evidencia, descripcion, fechas):
        conexion = get_connection()
        cursor = None
        try:
            cursor = conexion.cursor()
            
            # Insertar justificación
            sql_justificacion = """
                insert into justificacion (id_TipoJustificacion, id_Empleado, tipo_evento, evidencia, descripcion)
	            values (%s, %s, %s, %s, %s)
                returning id_justificacion
            """
            cursor.execute(sql_justificacion, (id_tipo_justificacion, id_empleado, tipo_evento, evidencia, descripcion))
            id_justificacion = cursor.fetchone()[0]
            
            # Insertar detalles de justificación
            sql_asistencia = """
                select id_asistencia from asistencia where id_empleado = %s and fecha = %s::date
            """
            
            sql_detalle = """
                insert into justificacion_detalle (id_justificacion, id_asistencia, fecha) 
	            values (%s, %s, %s::date)
            """
            
            for fecha_str in fechas:
                # Limpiar la fecha de espacios en blanco
                fecha_str = fecha_str.strip()
                
                # Verificar si la fecha ya está en formato ISO (yyyy-mm-dd)
                try:
                    # Intentar parsear como ISO primero
                    fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d')
                    fecha_iso = fecha_str
                except ValueError:
                    try:
                        # Si falla, intentar parsear como dd/mm/yyyy
                        fecha_obj = datetime.strptime(fecha_str, '%d/%m/%Y')
                        fecha_iso = fecha_obj.strftime('%Y-%m-%d')
                    except ValueError:
                        print(f"Error: Formato de fecha no válido: {fecha_str}")
                        continue
                
                # Buscar la asistencia correspondiente
                cursor.execute(sql_asistencia, (id_empleado, fecha_iso))
                resultado_asistencia = cursor.fetchone()
                
                if resultado_asistencia:
                    id_asistencia = resultado_asistencia[0]
                    cursor.execute(sql_detalle, (id_justificacion, id_asistencia, fecha_iso))
                else:
                    print(f"Advertencia: No se encontró registro de asistencia para empleado {id_empleado} en fecha {fecha_iso}")
                
            conexion.commit()
            return 1
        except Exception as e:
            conexion.rollback()
            print(f"Error al agregar justificacion: {e}")
            return None
        finally:
            if conexion:
                conexion.close()