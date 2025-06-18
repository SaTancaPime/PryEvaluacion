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
    def guardar_encuesta_empleado(id_encuesta, id_empleado, puntaje):
        from datetime import date
        conexion = get_connection()
        cursor = None
        try:
            cursor = conexion.cursor()
            
            # Paso 1: Verificar en evaluacion_encuesta si ya respondió hoy
            sql_verificar_hoy = """
                SELECT puntaje FROM evaluacion_encuesta 
                WHERE id_encuesta = %s AND id_empleado = %s AND fecha_evaluacion = CURRENT_DATE
            """
            cursor.execute(sql_verificar_hoy, (id_encuesta, id_empleado))
            resultado_hoy = cursor.fetchone()
            
            if not resultado_hoy:
                raise Exception(f"No se encontró registro de evaluación para hoy")
            
            puntaje_actual = resultado_hoy[0]
            
            # Si el puntaje es diferente de 0, ya respondió la encuesta
            if puntaje_actual != 0:
                raise Exception("Ya ha respondido la encuesta para el día de hoy")
            
            # Paso 2: Actualizar el puntaje en evaluacion_encuesta
            sql_actualizar_encuesta = """
                UPDATE evaluacion_encuesta 
                SET puntaje = %s 
                WHERE id_encuesta = %s AND id_empleado = %s AND fecha_evaluacion = CURRENT_DATE
            """
            cursor.execute(sql_actualizar_encuesta, (puntaje, id_encuesta, id_empleado))
            
            # Paso 3: Obtener el id_evaluacion_empleado y su fecha_registro
            sql_buscar_evaluacion = """
                SELECT id_evaluacion_empleado, fecha_registro FROM evaluacion_empleado 
                WHERE id_empleado = %s AND estado = true AND extract(month from fecha_registro) = extract(month from current_date)
            """
            cursor.execute(sql_buscar_evaluacion, (id_empleado,))
            resultado_evaluacion = cursor.fetchone()
            
            if not resultado_evaluacion:
                raise Exception(f"No se encontró evaluación activa para el empleado {id_empleado}")
            
            id_evaluacion_empleado, fecha_registro = resultado_evaluacion
            
            # Paso 4: Obtener fechas de inicio y fin de la encuesta
            sql_fechas_encuesta = """
                SELECT fecha_inicio, fecha_fin FROM encuesta 
                WHERE id_encuesta = %s
            """
            cursor.execute(sql_fechas_encuesta, (id_encuesta,))
            fechas_encuesta = cursor.fetchone()
            
            if not fechas_encuesta:
                raise Exception(f"No se encontró la encuesta {id_encuesta}")
            
            fecha_inicio, fecha_fin = fechas_encuesta
            
            # Paso 5: Determinar el rango de fechas usando fecha_registro
            from datetime import date
            fecha_actual = date.today()
            
            # Verificar que estamos dentro del período de la encuesta
            if fecha_actual < fecha_inicio or fecha_actual > fecha_fin:
                raise Exception("La fecha actual está fuera del período de la encuesta")
            
            # Usar fecha_registro como punto de inicio para el promedio
            # Si fecha_registro es del mes actual, usarla como inicio
            # Si es de un mes anterior, usar el día 1 del mes actual
            if fecha_registro.month == fecha_actual.month and fecha_registro.year == fecha_actual.year:
                # Mismo mes: desde fecha_registro hasta hoy
                fecha_desde = fecha_registro
            else:
                # Mes diferente: desde el día 1 del mes actual hasta hoy
                fecha_desde = fecha_actual.replace(day=1)
            
            fecha_hasta = fecha_actual
            
            # Asegurar que no se salga del rango de la encuesta
            if fecha_desde < fecha_inicio:
                fecha_desde = fecha_inicio
            if fecha_hasta > fecha_fin:
                fecha_hasta = fecha_fin
            
            # Paso 6: Obtener todos los puntajes del período y calcular promedio
            sql_puntajes_periodo = """
                SELECT puntaje FROM evaluacion_encuesta 
                WHERE id_encuesta = %s AND id_empleado = %s 
                AND fecha_evaluacion BETWEEN %s AND %s
            """
            cursor.execute(sql_puntajes_periodo, (id_encuesta, id_empleado, fecha_desde, fecha_hasta))
            puntajes = cursor.fetchall()
            
            if not puntajes:
                # Si no hay puntajes previos, usar el puntaje actual
                puntaje_promedio = float(puntaje)
            else:
                # Calcular promedio de todos los puntajes del período
                suma_puntajes = sum(float(p[0]) for p in puntajes)
                cantidad_dias = len(puntajes)
                puntaje_promedio = suma_puntajes / cantidad_dias
            
            # Paso 7: Verificar y actualizar/insertar en evaluacion_empleado_metrica
            sql_buscar_metrica = """
                SELECT puntaje FROM evaluacion_empleado_metrica 
                WHERE id_evaluacion_empleado = %s AND id_metrica = 4
            """
            cursor.execute(sql_buscar_metrica, (id_evaluacion_empleado,))
            resultado_metrica = cursor.fetchone()
            
            if resultado_metrica:
                # Si existe, actualizar directamente con el puntaje calculado
                sql_actualizar_metrica = """
                    UPDATE evaluacion_empleado_metrica 
                    SET puntaje = %s 
                    WHERE id_evaluacion_empleado = %s AND id_metrica = 4
                """
                cursor.execute(sql_actualizar_metrica, (puntaje_promedio, id_evaluacion_empleado))
            else:
                # Si no existe, crear nuevo registro
                sql_insertar_metrica = """
                    INSERT INTO evaluacion_empleado_metrica (id_evaluacion_empleado, id_metrica, puntaje)
                    VALUES (%s, 4, %s)
                """
                cursor.execute(sql_insertar_metrica, (id_evaluacion_empleado, puntaje_promedio))
            
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