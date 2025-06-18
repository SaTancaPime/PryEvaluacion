from flask import send_file, flash, redirect, url_for
import qrcode
import io

class GeneradorQR:
    @staticmethod
    def generar_qr(url_formulario, nombre_archivo, redirect_blueprint='encuesta_bp.index'):
        try:
            # Crear el código QR
            qr = qrcode.QRCode(
                version=1,                                          # tamaño del QR
                error_correction=qrcode.constants.ERROR_CORRECT_L,  # nivel de corrección de errores
                box_size=10,                                        # Tamaño de caja del QR en px
                border=4,                                           # Borde
            )
            qr.add_data(url_formulario)   # Agregar la URL al QR
            qr.make(fit=True)           # Ajustar el QR al contenido
            
            # Crear la imagen del QR
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convertir la imagen a bytes para enviar como archivo
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            # Enviar el archivo para descarga
            return send_file(
                img_buffer, 
                mimetype='image/png',
                as_attachment=True,
                download_name=nombre_archivo
            )
        except Exception as e:
            flash(f'Error al generar el código QR: {str(e)}', 'error')
            return redirect(url_for(redirect_blueprint))
        
    @staticmethod
    def qr_encuesta(id_encuesta):
        from flask import url_for
        url_encuesta = url_for('encuesta_bp.encuesta', id_encuesta=id_encuesta, _external=True)
        return GeneradorQR.generar_qr(
            url_encuesta, 
            f'qr_encuesta_{id_encuesta}.png'
        )

    @staticmethod
    def qr_asistencia():
        from flask import url_for
        url_encuesta = url_for('asistencia_bp.asistencia_empleados', _external=True)
        return GeneradorQR.generar_qr(
            url_encuesta, 
            'qr_asistencia_empleados.png'
        )
        
    @staticmethod
    def qr_incidentes_clientes():
        from flask import url_for
        url_incidentes = url_for('incidente_bp.incidente_cliente', _external=True)
        return GeneradorQR.generar_qr(
            url_incidentes, 
            'qr_incidentes_clientes.png'
        )
    
    @staticmethod
    def qr_incidentes_empleados():
        from flask import url_for
        url_incidentes = url_for('incidente_bp.incidente_empleado', _external=True)
        return GeneradorQR.generar_qr(
            url_incidentes, 
            'qr_incidentes_empleados.png'
        )
    
    @staticmethod
    def qr_justificaciones():
        from flask import url_for
        url_justificaciones = url_for('justificacion_bp.justificacion_empleado', _external=True)
        return GeneradorQR.generar_qr(
            url_justificaciones, 
            'qr_justificaciones_empleados.png'
        )