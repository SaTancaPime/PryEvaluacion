import requests
import logging
import os
from dotenv import load_dotenv
from app.controllers.control_cliente import ControlCliente

# Cargar variables de entorno
load_dotenv()

class ClienteService:
    @staticmethod
    def validar_documento_api(id_tipo_doc, nro_doc):
        try:
            id_tipo_doc = int(id_tipo_doc)
            tipo_doc_nombre = ''
            if id_tipo_doc == 1:
                tipo_doc_nombre = 'dni'
            elif id_tipo_doc == 2:
                tipo_doc_nombre = 'cee'
            elif id_tipo_doc == 3:
                tipo_doc_nombre = 'ruc'
            else:
                return None
            
            url = f"https://api.factiliza.com/v1/{tipo_doc_nombre}/info/{nro_doc}"
            token = os.getenv('FACTILIZA_API_TOKEN')
            if not token:
                print("Token de API no configurado en .env")
                return None
            
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.request("GET", url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                cliente_data = data.get('data')
                
                if id_tipo_doc == 1:
                    return {
                        'nombre': cliente_data.get('nombre_completo', ''),
                        'documento': nro_doc,
                        'tipo_doc': id_tipo_doc
                    }
                elif id_tipo_doc == 2:
                    return {
                        'nombre': cliente_data.get('nombres', '') + ' ' + cliente_data.get('apellido_paterno', '') + ' ' + cliente_data.get('apellido_materno', ''),
                        'documento': nro_doc,
                        'tipo_doc': id_tipo_doc
                    }
                elif id_tipo_doc == 3:
                    return {
                        'nombre': cliente_data.get('nombre_o_razon_social', ''),
                        'documento': nro_doc,
                        'tipo_doc': id_tipo_doc
                    }
            elif response.status == 404:
                print(f"Documento no encontrado: {nro_doc}")
                return None
            else:
                print(f"Error en API: {response.status} - {response.message}")
                return None
                
        except requests.exceptions.Timeout:
            print("Timeout al consultar API externa")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión con API: {str(e)}")
            return None
        except Exception as e:
            print(f"Error inesperado al validar documento: {str(e)}")
            return None

    @staticmethod
    def obtener_o_crear_cliente(id_tipo_doc, nro_doc):
        try:
            # Buscar si el cliente existe en la BD
            cliente_existente = ControlCliente.buscar_cliente(id_tipo_doc, nro_doc)
            if cliente_existente not in (0, -1):
                return {
                    'success': True,
                    'cliente_id': cliente_existente,
                    'message': 'Cliente encontrado en base de datos',
                    'es_nuevo': False
                }
            
            # Si no existe el cliente, validar documento con la API
            info_api = ClienteService.validar_documento_api(id_tipo_doc, nro_doc)
            if not info_api:
                return {
                    'success': False,
                    'cliente_id': None,
                    'message': 'Documento no encontrado o inválido en el sistema de consulta',
                    'es_nuevo': False
                }
            
            # Si el documento es válido, registrar el nuevo cliente
            cliente_id = ControlCliente.registrar_cliente(id_tipo_doc, nro_doc, info_api['nombre'].strip())
            if cliente_id not in (0, -1):
                return {
                    'success': True,
                    'cliente_id': cliente_id,
                    'message': f'Cliente registrado exitosamente: {info_api["nombre"]}',
                    'es_nuevo': True
                }
            else:
                return {
                    'success': False,
                    'cliente_id': None,
                    'message': 'Error al registrar cliente en base de datos',
                    'es_nuevo': False
                }
                
        except Exception as e:
            return {
                'success': False,
                'cliente_id': None,
                'message': f'Error interno: {str(e)}',
                'es_nuevo': False
            }