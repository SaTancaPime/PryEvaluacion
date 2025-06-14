import os
from dotenv import load_dotenv
import uuid
import logging
from datetime import datetime
from werkzeug.utils import secure_filename
from PIL import Image
from io import BytesIO
import dropbox
from dropbox.exceptions import ApiError, AuthError
import requests

load_dotenv()

class DropboxService:
    FORMATO_PERMITIDO = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_TAMANO = 5 * 1024 * 1024  # 5MB
    
    def __init__(self):
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """Inicializa el cliente de Dropbox usando refresh token o access token legacy"""
        try:
            refresh_token = os.getenv('DROPBOX_REFRESH_TOKEN')
            app_key = os.getenv('DROPBOX_APP_KEY')
            app_secret = os.getenv('DROPBOX_APP_SECRET')
            
            if refresh_token and app_key and app_secret:
                logging.info("Inicializando Dropbox con refresh token")
                self.client = dropbox.Dropbox(
                    oauth2_refresh_token=refresh_token,
                    app_key=app_key,
                    app_secret=app_secret
                )
            else:
                access_token = os.getenv('DROPBOX_ACCESS_TOKEN')
                if not access_token:
                    logging.error("No se encontró DROPBOX_REFRESH_TOKEN ni DROPBOX_ACCESS_TOKEN en .env")
                    print("Error: Configure DROPBOX_REFRESH_TOKEN + APP_KEY + APP_SECRET o DROPBOX_ACCESS_TOKEN en .env")
                    return
                
                logging.info("Inicializando Dropbox con access token legacy")
                self.client = dropbox.Dropbox(access_token)
            
            # Verificar que el cliente funciona
            self.client.users_get_current_account()
            logging.info("Cliente Dropbox inicializado correctamente")
            
        except AuthError as e:
            logging.error(f"Error de autenticación con Dropbox: {str(e)}")
            if "token is malformed" in str(e).lower() or "expired" in str(e).lower():
                logging.error("El token parece estar expirado. Considere usar refresh token.")
            self.client = None
        except Exception as e:
            logging.error(f"Error al inicializar Dropbox: {str(e)}")
            self.client = None
    
    def _refresh_access_token_manual(self):
        """
        Método para renovar manualmente el access token usando refresh token.
        Solo necesario si no usas el SDK con refresh token automático.
        """
        try:
            refresh_token = os.getenv('DROPBOX_REFRESH_TOKEN')
            app_key = os.getenv('DROPBOX_APP_KEY')
            app_secret = os.getenv('DROPBOX_APP_SECRET')
            
            if not all([refresh_token, app_key, app_secret]):
                logging.error("Faltan credenciales para refresh token")
                return None
            
            # Hacer petición manual al endpoint de Dropbox
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': app_key,
                'client_secret': app_secret
            }
            
            response = requests.post('https://api.dropbox.com/oauth2/token', data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                new_access_token = token_data['access_token']
                expires_in = token_data.get('expires_in', 14400)  # 4 horas por defecto
                
                logging.info(f"Access token renovado exitosamente. Expira en {expires_in} segundos")
                return new_access_token
            else:
                logging.error(f"Error al renovar token: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"Error en refresh token manual: {str(e)}")
            return None
    
    def _retry_with_refresh(self, func, *args, **kwargs):
        """
        Envoltorio para reintentar operaciones si el token expira.
        Solo útil si usas access tokens manuales en lugar del SDK con refresh automático.
        """
        try:
            return func(*args, **kwargs)
        except AuthError as e:
            if "token" in str(e).lower() and ("expired" in str(e).lower() or "invalid" in str(e).lower()):
                logging.warning("Token expirado, intentando renovar...")
                
                new_token = self._refresh_access_token_manual()
                if new_token:
                    # Reinicializar cliente con nuevo token
                    self.client = dropbox.Dropbox(new_token)
                    # Reintentar operación
                    return func(*args, **kwargs)
                else:
                    raise AuthError("No se pudo renovar el token")
            else:
                raise e
    
    @staticmethod
    def es_archivo_permitido(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in DropboxService.FORMATO_PERMITIDO
    
    @staticmethod
    def generar_nombre_unico(filename):
        nombre_seguro = secure_filename(filename)
        extension = nombre_seguro.rsplit('.', 1)[1].lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"{timestamp}_{unique_id}.{extension}"
    
    def optimizar_imagen(self, archivo):
        try:
            # Abrir imagen
            img = Image.open(archivo)
            
            # Convertir a RGB si es necesario
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            # Redimensionar manteniendo proporción (máximo 1920x1080)
            img.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
            
            # Guardar optimizada en buffer
            buffer = BytesIO()
            img.save(buffer, format='JPEG', optimize=True, quality=85)
            
            # Obtener tamaño y reiniciar posición
            tamaño = buffer.tell()
            buffer.seek(0)
            
            return buffer, tamaño
            
        except Exception as e:
            logging.error(f"Error al optimizar imagen: {str(e)}")
            return None, 0
    
    def subir_imagen(self, modulo, carpeta, archivo):
        try:
            # Verificar cliente
            if not self.client:
                return {
                    'success': False,
                    'message': 'Servicio de Dropbox no disponible. Verifique la configuración.'
                }
            
            # Verificaciones básicas
            if not archivo or archivo.filename == '':
                return {'success': False, 'message': 'No se seleccionó archivo'}
            
            if not self.es_archivo_permitido(archivo.filename):
                return {
                    'success': False,
                    'message': f'Tipo de archivo no permitido. Use: {", ".join(self.FORMATO_PERMITIDO)}'
                }
            
            # Verificar tamaño del archivo original
            archivo.seek(0, 2)
            file_size = archivo.tell()
            archivo.seek(0)
            
            if file_size > self.MAX_TAMANO:
                return {
                    'success': False,
                    'message': f'Archivo muy grande. Máximo: {self.MAX_TAMANO // (1024*1024)}MB'
                }
            
            # Generar nombre único
            nombre_archivo = self.generar_nombre_unico(archivo.filename)
            
            # Optimizar imagen
            buffer_optimizado, tamaño_optimizado = self.optimizar_imagen(archivo)
            if not buffer_optimizado:
                return {'success': False, 'message': 'Error al procesar la imagen'}
            
            # Ruta en Dropbox
            ruta_dropbox = f"/{modulo}/{carpeta}/{nombre_archivo}"
            
            # Subir archivo a Dropbox (con retry automático si usa refresh token en SDK)
            resultado = self.client.files_upload(
                buffer_optimizado.getvalue(),
                ruta_dropbox,
                mode=dropbox.files.WriteMode.overwrite
            )
            
            # Crear enlace compartido para descarga
            try:
                shared_link = self.client.sharing_create_shared_link_with_settings(
                    ruta_dropbox,
                    settings=dropbox.sharing.SharedLinkSettings(
                        requested_visibility=dropbox.sharing.RequestedVisibility.public
                    )
                )
                url_descarga = shared_link.url.replace('?dl=0', '?dl=1')
                url_vista = shared_link.url
            except ApiError as e:
                # Si ya existe un enlace compartido, obtenerlo
                if 'shared_link_already_exists' in str(e):
                    links = self.client.sharing_list_shared_links(path=ruta_dropbox).links
                    if links:
                        url_descarga = links[0].url.replace('?dl=0', '?dl=1')
                        url_vista = links[0].url
                    else:
                        url_descarga = ""
                        url_vista = ""
                else:
                    logging.error(f"Error al crear enlace compartido: {str(e)}")
                    url_descarga = ""
                    url_vista = ""
            
            return {
                'success': True,
                'nombre_archivo': nombre_archivo,
                'nombre_original': archivo.filename,
                'ruta_dropbox': ruta_dropbox,
                'url_descarga': url_descarga,
                'url_vista': url_vista,
                'tamaño': tamaño_optimizado,
                'message': 'Imagen subida exitosamente a Dropbox'
            }
            
        except AuthError as e:
            logging.error(f"Error de autenticación con Dropbox: {str(e)}")
            return {'success': False, 'message': 'Error de autenticación con Dropbox. Token expirado o inválido.'}
        except ApiError as e:
            logging.error(f"Error de API de Dropbox: {str(e)}")
            return {'success': False, 'message': f'Error de Dropbox: {str(e)}'}
        except Exception as e:
            logging.error(f"Error inesperado al subir a Dropbox: {str(e)}")
            return {'success': False, 'message': f'Error interno: {str(e)}'}

    @staticmethod
    def generar_instrucciones_oauth():
        """
        Método estático para generar instrucciones de cómo obtener un refresh token.
        Útil para la primera configuración.
        """
        app_key = os.getenv('DROPBOX_APP_KEY', '<TU_APP_KEY>')
        
        instrucciones = f"""
=== INSTRUCCIONES PARA OBTENER REFRESH TOKEN ===

1. Ve a este URL (reemplaza <TU_APP_KEY> con tu App Key real):
   https://www.dropbox.com/oauth2/authorize?client_id={app_key}&token_access_type=offline&response_type=code

2. Autoriza la aplicación y copia el código de autorización

3. Ejecuta este curl comando (reemplaza los valores):
   curl -X POST https://api.dropboxapi.com/oauth2/token \\
     -u "<TU_APP_KEY>:<TU_APP_SECRET>" \\
     -H "Content-Type: application/x-www-form-urlencoded" \\
     --data-urlencode "code=<CODIGO_AUTORIZACION>" \\
     --data-urlencode "grant_type=authorization_code"

4. Del JSON resultado, guarda estos valores en tu .env:
   DROPBOX_REFRESH_TOKEN=<refresh_token_del_resultado>
   DROPBOX_APP_KEY=<tu_app_key>
   DROPBOX_APP_SECRET=<tu_app_secret>

5. Elimina DROPBOX_ACCESS_TOKEN de tu .env (ya no lo necesitas)

El refresh token NO EXPIRA hasta que lo revokes manualmente.
        """
        
        return instrucciones