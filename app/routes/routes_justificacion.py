from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.controllers.control_justificacion import ControlJustificacion
from app.controllers.control_empleado import ControlEmpleado
from app.controllers.control_tipo_doc import ControlTipoDoc
from app.services.service_dropbox import DropboxService
from app.utils.generador_qr import GeneradorQR
from datetime import datetime

justificacion_bp = Blueprint('justificacion_bp', __name__)

dropbox_service = DropboxService()

@justificacion_bp.route('/obtener-empleado/<int:tipo_doc>/<nro_doc>')
def obtener_empleado(tipo_doc, nro_doc):
    empleado = ControlEmpleado.buscar_empleado(tipo_doc, nro_doc)
    return jsonify({'id_empleado': empleado if empleado else 0})

@justificacion_bp.route('/obtener-fechas/<int:id_empleado>/<evento>')
def obtener_fechas(id_empleado, evento):
    rpta = dict()
    fechas = ControlJustificacion.buscar_fechas_evento(id_empleado, evento)
    
    if fechas is not None and len(fechas) > 0:
        rpta['status'] = 1
        rpta['data'] = fechas
        rpta['message'] = 'Fechas encontradas exitosamente'
    else:
        rpta['status'] = 0
        rpta['data'] = []
        rpta['message'] = 'No se encontraron fechas para el evento solicitado'
    
    return jsonify(rpta)

def procesar_fechas_justificacion(fechas_str):
    """
    Procesa la cadena de fechas y las convierte al formato correcto
    """
    if not fechas_str:
        return []
    
    fechas_lista = []
    fechas_raw = fechas_str.split(', ')
    
    for fecha_str in fechas_raw:
        fecha_str = fecha_str.strip()
        if not fecha_str:
            continue
            
        # Verificar si ya está en formato ISO (yyyy-mm-dd)
        if len(fecha_str) == 10 and fecha_str.count('-') == 2:
            try:
                # Validar que sea una fecha válida en formato ISO
                datetime.strptime(fecha_str, '%Y-%m-%d')
                fechas_lista.append(fecha_str)
                continue
            except ValueError:
                pass
        
        # Si no está en formato ISO, intentar convertir desde dd/mm/yyyy
        try:
            fecha_obj = datetime.strptime(fecha_str, '%d/%m/%Y')
            fecha_iso = fecha_obj.strftime('%Y-%m-%d')
            fechas_lista.append(fecha_iso)
        except ValueError:
            print(f"Error: No se pudo procesar la fecha: {fecha_str}")
            continue
    
    return fechas_lista

@justificacion_bp.route('/justificacion-empleado', methods=['GET', 'POST'])
def justificacion_empleado():
    if request.method == 'GET':
        try:
            tipos_doc = ControlTipoDoc.obtener_tipo_doc()
            tipos_justificacion = ControlJustificacion.obtener_tipo_justificacion()
            
            if tipos_doc is None or tipos_justificacion is None:
                flash('Error al cargar datos necesarios para el formulario.', 'error')
                
            return render_template('form_justificacion.html', 
                                   tipos_doc=tipos_doc, 
                                   tipos_justificacion=tipos_justificacion)
        except Exception as e:
            flash('Error inesperado al cargar el formulario. Por favor, intente nuevamente.', 'error')
            return redirect(url_for('justificacion_bp.justificacion_empleado'))
        
    if request.method == 'POST':
        try:
            # Validar datos del empleado
            tipo_doc_empleado = request.form.get('tipo-documento-empleado')
            nro_doc_empleado = request.form.get('num-documento-empleado')
            
            if not tipo_doc_empleado or not nro_doc_empleado:
                flash('Debe seleccionar un tipo de documento y proporcionar el número.', 'error')
                return redirect(url_for('justificacion_bp.justificacion_empleado'))
            
            if not nro_doc_empleado.strip():
                flash('El número de documento no puede estar vacío.', 'error')
                return redirect(url_for('justificacion_bp.justificacion_empleado'))
            
            # Buscar empleado
            id_empleado = ControlEmpleado.buscar_empleado(tipo_doc_empleado, nro_doc_empleado)
            if id_empleado == -1:
                flash('El empleado con el documento proporcionado no existe en el sistema.', 'error')
                return redirect(url_for('justificacion_bp.justificacion_empleado'))
            else:
                flash('Empleado verificado exitosamente.', 'success')
            
            # Validar evidencia
            evidencia_empleado = None
            if 'evidencia' not in request.files:
                flash('Debe proporcionar evidencia para la justificación.', 'error')
                return redirect(url_for('justificacion_bp.justificacion_empleado'))
            
            archivo_evidencia = request.files['evidencia']
            if not archivo_evidencia or archivo_evidencia.filename == '':
                flash('No se seleccionó ninguna imagen o el nombre del archivo es inválido.', 'error')
                return redirect(url_for('justificacion_bp.justificacion_empleado'))
            
            # Subir evidencia a Dropbox
            resultado_evidencia = dropbox_service.subir_imagen('incidecias', 'empleado', archivo_evidencia)
            if resultado_evidencia['success']:
                evidencia_empleado = resultado_evidencia['url_descarga']
                flash('Evidencia subida exitosamente.', 'success')
            else:
                flash('Error al subir la imagen a Dropbox. Intente nuevamente.', 'error')
                return redirect(url_for('justificacion_bp.justificacion_empleado'))
                
            # Validar campos del formulario
            evento = request.form.get('tipo-evento')
            if not evento:
                flash('Debe seleccionar un tipo de evento (Tardanza o Inasistencia).', 'error')
                return redirect(url_for('justificacion_bp.justificacion_empleado'))
            
            tipo_evento = True if evento == '2' else False if evento == '3' else None
            if tipo_evento is None:
                flash('Tipo de evento inválido seleccionado.', 'error')
                return redirect(url_for('justificacion_bp.justificacion_empleado'))
            
            tipo_justificacion = request.form.get('tipo-justificacion')
            if not tipo_justificacion:
                flash('Debe seleccionar un tipo de justificación.', 'error')
                return redirect(url_for('justificacion_bp.justificacion_empleado'))
            
            fechas_str = request.form.get('fechasJustificar')
            if not fechas_str:
                flash('Debe seleccionar al menos una fecha para justificar.', 'error')
                return redirect(url_for('justificacion_bp.justificacion_empleado'))
            
            # Procesar las fechas correctamente
            fechas_iterable = procesar_fechas_justificacion(fechas_str)
            if not fechas_iterable:
                flash('No se encontraron fechas válidas para justificar.', 'error')
                return redirect(url_for('justificacion_bp.justificacion_empleado'))
            
            detalle = request.form.get('detalles-justificacion')
            
            # Debug: Imprimir las fechas procesadas
            print(f"Fechas procesadas para BD: {fechas_iterable}")
            
            # Procesar justificación
            resultado = ControlJustificacion.agregar_justificacion(
                tipo_justificacion, id_empleado, tipo_evento, 
                evidencia_empleado, detalle, fechas_iterable
            )
            
            if resultado == 1:
                flash('¡Justificación registrada exitosamente! Su solicitud ha sido enviada.', 'success')
                return redirect(url_for('justificacion_bp.exito_justificacion'))
            else:
                flash('Ocurrió un error al procesar la justificación. Intente nuevamente.', 'error')
                return redirect(url_for('justificacion_bp.justificacion_empleado'))
                
        except Exception as e:
            flash('Error inesperado al procesar la justificación. Por favor, intente nuevamente.', 'error')
            print(f"Error en POST justificación empleado: {str(e)}")
            return redirect(url_for('justificacion_bp.justificacion_empleado'))
    
@justificacion_bp.route('/exito-justificacion')
def exito_justificacion():
    return render_template('agrad_justificacion.html')

@justificacion_bp.route('/qr-justificaciones')
def generar_qr_justificaciones():
    return GeneradorQR.qr_justificaciones()