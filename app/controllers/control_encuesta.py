from app.database.db import get_connection

class ControlEncuesta:
    # Métodos para el menú de encuestas
    @staticmethod
    def filtro_1():
        try:
            sql = """
                select count(*) from encuesta
            """
            conexion = get_connection()
            total = 0
            with conexion.cursor() as cursor:
                cursor.execute(sql)
                total = cursor.fetchone()[0]
            conexion.close()
            return total
        except Exception as e:
            print(f"Error al agregar encuesta: {e}")
            return -1
        
    @staticmethod
    def filtro_2():
        try:
            sql = """
                select count(*) from encuesta where estado = true
            """
            conexion = get_connection()
            total = 0
            with conexion.cursor() as cursor:
                cursor.execute(sql)
                total = cursor.fetchone()[0]
            conexion.close()
            return total
        except Exception as e:
            print(f"Error al agregar encuesta: {e}")
            return -1
    
    @staticmethod
    def filtro_3():
        try:
            sql = """
                select count(*) from encuesta where tipo_publico = 'c'
            """
            conexion = get_connection()
            total = 0
            with conexion.cursor() as cursor:
                cursor.execute(sql)
                total = cursor.fetchone()[0]
            conexion.close()
            return total            
        except Exception as e:
            print(f"Error al agregar encuesta: {e}")
            return -1
    
    @staticmethod
    def filtro_4():
        try:
            sql = """
                select count(*) from encuesta where tipo_publico = 'e'
            """
            conexion = get_connection()
            total = 0
            with conexion.cursor() as cursor:
                cursor.execute(sql)
                total = cursor.fetchone()[0]
            conexion.close()
            return total            
        except Exception as e:
            print(f"Error al agregar encuesta: {e}")
            return -1
        
    @staticmethod
    def mostrar_encuestas():
        try:
            sql = """
                select 
                    e.id_encuesta, 
                    e.nombre || ' - ' || m.nombre as encuesta_completo, 
                    e.estado, 
                    e.tipo_publico, 
                    e.fecha_registro, 
                    e.fecha_inicio, 
                    e.fecha_fin
                from 
                    encuesta e
                inner join
                    metrica m on e.id_metrica = m.id_metrica;
            """
            conexion = get_connection()
            encuestas = []
            with conexion.cursor() as cursor:
                cursor.execute(sql)
                encuestas = cursor.fetchall()
            conexion.close()
            
            return encuestas
        except Exception as e:
            print(f"Error al mostrar las encuestas: {e}")
            return None
        
        
    # Métodos para las encuestas individuales
    @staticmethod
    def obtener_encuesta(id_encuesta):
        try:
            sql = """
                select e.id_encuesta, e.nombre as encuesta, m.nombre as metrica, e.tipo_publico 
                from encuesta e
                inner join metrica m on e.id_metrica = m.id_metrica
                where e.id_encuesta = %s;
            """
            conexion = get_connection()
            encuesta = None
            with conexion.cursor() as cursor:
                cursor.execute(sql, (id_encuesta,))
                encuesta = cursor.fetchone()
            conexion.close()
            return encuesta
        except Exception as e:
            print(f"Error al obtener datos de una encuesta: {e}")
            return None
    
    @staticmethod
    def obtener_preguntas_encuesta(id_encuesta):
        try:
            sql = """
                select * from pregunta p 
                inner join encuesta_pregunta ep on ep.id_pregunta = p.id_pregunta 
                where ep.id_encuesta = %s
            """
            conexion = get_connection()
            preguntas = []
            with conexion.cursor() as cursor:
                cursor.execute(sql, (id_encuesta,))
                preguntas = cursor.fetchall()
            conexion.close()
            return preguntas
        except Exception as e:
            print(f"Error al obtener preguntas de la encuesta: {e}")
            return None
        
        
    # Métodos para guardar encuestas (cliente y empleado)
    @staticmethod
    def guardar_encuesta_cliente(id_evaluacion, puntaje):
        try:
            sql = """
                select sp_guardar_evaluacion_cliente(
                    p_id_evaluacion := %s,
                    puntaje := %s
                );
            """
            conexion = get_connection()
            respuesta = None
            with conexion.cursor() as cursor:
                cursor.execute(sql, (id_evaluacion, puntaje))
                respuesta = cursor.fetchone()[0]
            conexion.commit()
            conexion.close()
            
            return respuesta
        except Exception as e:
            print(f"Error al guardar encuesta del cliente: {e}")
            return None
        
    @staticmethod
    def guardar_encuesta_empleado(id_evaluacion, id_empleado, puntaje):
        try:
            sql = """
                select sp_guardar_evaluacion_empleado(
                    p_id_evaluacion := %s,
                    p_id_empleado := %s,
                    puntaje := %s
                );
            """
            conexion = get_connection()
            respuesta = None
            with conexion.cursor() as cursor:
                cursor.execute(sql, (id_evaluacion, id_empleado, puntaje))
                respuesta = cursor.fetchone()[0]
            conexion.commit()
            conexion.close()
            
            return respuesta            
        except Exception as e:
            print(f"Error al guardar encuesta del empleado: {e}")
            return None