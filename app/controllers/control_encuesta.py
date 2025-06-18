from app.database.db import get_connection
from decimal import Decimal

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
        conexion = get_connection()
        cursor = None
        try:
            cursor = conexion.cursor()
            
            # Obtener todas las evaluaciones
            sql_obtener_evaluaciones = """
                SELECT id_evaluacion_empleado FROM Evaluacion_empleado where estado = true
            """
            cursor.execute(sql_obtener_evaluaciones)
            evaluaciones = cursor.fetchall()
            
            if not evaluaciones:
                raise Exception("No se encontraron evaluaciones de empleados")
            
            # Recorrer cada evaluación y actualizar o insertar el puntaje
            for evaluacion_row in evaluaciones:
                evaluacion_id = evaluacion_row[0]
                
                sql_buscar_metrica = """
                    SELECT Puntaje FROM Evaluacion_empleado_Metrica 
                    WHERE id_evaluacion_empleado = %s AND Id_Metrica = 3
                """
                cursor.execute(sql_buscar_metrica, (evaluacion_id,))
                resultado_metrica = cursor.fetchone()
                
                if resultado_metrica:
                    puntaje_anterior = resultado_metrica[0]
                    nuevo_puntaje = (puntaje_anterior + Decimal(str(puntaje))) / 2
                    
                    sql_actualizar_metrica = """
                        UPDATE Evaluacion_empleado_Metrica 
                        SET Puntaje = %s 
                        WHERE id_evaluacion_empleado = %s AND Id_Metrica = 3
                    """
                    cursor.execute(sql_actualizar_metrica, (nuevo_puntaje, evaluacion_id))
                    
                else:
                    sql_insertar_metrica = """
                        INSERT INTO Evaluacion_empleado_Metrica (id_evaluacion_empleado, Id_Metrica, Puntaje)
                        VALUES (%s, 3, %s)
                    """
                    cursor.execute(sql_insertar_metrica, (evaluacion_id, puntaje))
            
            sql_sp = """
                SELECT sp_guardar_evaluacion_cliente(
                    p_id_evaluacion := %s,
                    puntaje := %s
                );
            """
            cursor.execute(sql_sp, (id_evaluacion, puntaje))
            respuesta_sp = cursor.fetchone()[0]
            
            conexion.commit()
            return 0
            
        except Exception as e:
            conexion.rollback()
            print(f"Error al guardar encuesta del cliente: {e}")
            return None
            
        finally:
            if cursor:
                cursor.close()
            conexion.close()
        
    @staticmethod
    def guardar_encuesta_empleado(id_evaluacion, id_empleado, puntaje):
        conexion = get_connection()
        cursor = None
        try:
            cursor = conexion.cursor()
            
            # Obtener todas las evaluaciones
            sql_buscar_evaluacion = """
                SELECT id_evaluacion_empleado FROM Evaluacion_empleado 
                WHERE Id_Empleado = %s and estado = true
            """
            cursor.execute(sql_buscar_evaluacion, (id_empleado,))
            resultado_evaluacion = cursor.fetchone()
            
            if not resultado_evaluacion:
                raise Exception(f"No se encontró evaluación para el empleado {id_empleado}")
            
            evaluacion_id = resultado_evaluacion[0]
            
            # Paso 2: Verificar si existe un registro en Evaluacion_empleado_Metrica
            sql_buscar_metrica = """
                SELECT Puntaje FROM Evaluacion_empleado_Metrica 
                WHERE id_evaluacion_empleado = %s AND Id_Metrica = 4
            """
            cursor.execute(sql_buscar_metrica, (evaluacion_id,))
            resultado_metrica = cursor.fetchone()
            
            if resultado_metrica:
                # Si existe, promediar el puntaje anterior con el nuevo
                puntaje_anterior = resultado_metrica[0]
                nuevo_puntaje = (puntaje_anterior + Decimal(str(puntaje))) / 2
                
                sql_actualizar_metrica = """
                    UPDATE Evaluacion_empleado_Metrica 
                    SET Puntaje = %s 
                    WHERE id_evaluacion_empleado = %s AND Id_Metrica = 4
                """
                cursor.execute(sql_actualizar_metrica, (nuevo_puntaje, evaluacion_id))
                
            else:
                # Si no existe, crear nuevo registro
                sql_insertar_metrica = """
                    INSERT INTO Evaluacion_empleado_Metrica (id_evaluacion_empleado, Id_Metrica, Puntaje)
                    VALUES (%s, 4, %s)
                """
                cursor.execute(sql_insertar_metrica, (evaluacion_id, puntaje))
            
            # Paso 3: Ejecutar el stored procedure original (si es necesario)
            sql_sp = """
                SELECT sp_guardar_evaluacion_empleado(
                    p_id_evaluacion := %s,
                    p_id_empleado := %s,
                    puntaje := %s
                );
            """
            cursor.execute(sql_sp, (id_evaluacion, id_empleado, puntaje))
            respuesta_sp = cursor.fetchone()[0]
            
            # Confirmar la transacción
            conexion.commit()
            
            return 0
            
        except Exception as e:
            # Revertir la transacción en caso de error
            conexion.rollback()
            print(f"Error al guardar encuesta del empleado: {e}")
            return None
            
        finally:
            if cursor:
                cursor.close()
            conexion.close()