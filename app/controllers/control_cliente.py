from app.database.db import get_connection

class ControlCliente:
    @staticmethod
    def buscar_cliente(id_tipo_doc, nro_doc):
        try:
            sql = """
                SELECT sp_buscar_cliente(
                    p_id_tipo_documento := %s,
                    p_nro_documento := %s
                );
            """
            conexion = get_connection()
            cliente = 0
            with conexion.cursor() as cursor:
                cursor.execute(sql, (id_tipo_doc, nro_doc))
                cliente = cursor.fetchone()[0]
            conexion.close()
            
            return cliente
        except Exception as e:
            print(f"Error al buscar cliente: {e}")
            return -1
        

    @staticmethod
    def registrar_cliente(id_tipo_doc, nro_doc, nombre):
        try:
            sql = """
                SELECT sp_registrar_cliente(
                    p_id_tipo_documento := %s,
                    p_nro_documento := %s,
                    p_nombre_cliente := %s
                );
            """
            conexion = get_connection()
            empleado = 0
            with conexion.cursor() as cursor:
                cursor.execute(sql, (id_tipo_doc, nro_doc, nombre))
                empleado = cursor.fetchone()[0]
            conexion.commit()
            conexion.close()
            
            return empleado
        except Exception as e:
            print(f"Error al registrar cliente: {e}")
            return -1