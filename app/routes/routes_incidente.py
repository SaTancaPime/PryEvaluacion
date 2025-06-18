from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.controllers.control_incidente import ControlIncidente
from app.controllers.control_empleado import ControlEmpleado
from app.controllers.control_tipo_doc import ControlTipoDoc
from app.controllers.control_sucursal import ControlSucursal
from app.controllers.control_area import ControlArea
from app.services.service_cliente import ClienteService
from app.services.service_dropbox import DropboxService
from app.utils.generador_qr import GeneradorQR

incidente_bp = Blueprint('incidente_bp', __name__)

dropbox_service = DropboxService()

@incidente_bp.route('/obtener-empleados/<int:id_sucursal>/<int:id_area>')
def obtener_empleados(id_sucursal, id_area):
    rpta = dict()
    empleados = ControlEmpleado.obtener_empleados(id_sucursal, id_area)
    
    if empleados is not None:
        rpta['status'] = 1
        rpta['data'] = []
        rpta['message'] = 'Empleados encontrado exitosamente'
        for empleado in empleados:
            empleadoDict = dict()
            empleadoDict['id_empleado'] = empleado[0]
            empleadoDict['nombre'] = empleado[1]
            rpta['data'].append(empleadoDict)
    else:
        rpta['status'] = 0
        rpta['data'] = []
        rpta['message'] = 'No se encontró el rol solicitado'
        
    return jsonify(rpta)

@incidente_bp.route('/incidente-cliente', methods=['GET', 'POST'])
def incidente_cliente():
    if request.method == 'GET':
        try:
            sucursales = ControlSucursal.obtener_sucursales()
            areas = ControlArea.obtener_areas()
            tipos_doc = ControlTipoDoc.obtener_tipo_doc()
            tipos = ControlIncidente.obtener_tipo_incidente_cliente()
            
            if sucursales is None or areas is None or tipos_doc is None or tipos is None:
                flash('Error al cargar datos necesarios para el formulario.', 'error')
                
            return render_template('form_incidencia_cliente.html', 
                                 sucursales=sucursales, 
                                 areas=areas, 
                                 tipos_doc=tipos_doc, 
                                 tipos=tipos)
        except Exception as e:
            flash('Error inesperado al cargar el formulario. Por favor, intente nuevamente.', 'error')
            return redirect(url_for('incidente_bp.incidente_cliente'))
    
    if request.method == 'POST':
        try:
            # Validación de datos del cliente
            tipo_doc_cliente = request.form.get('tipo-doc-cliente')
            nro_doc_cliente = request.form.get('num-documento-cliente')
            
            if not tipo_doc_cliente or not nro_doc_cliente:
                flash('Debe seleccionar un tipo de documento y proporcionar el número.', 'error')
                return redirect(url_for('incidente_bp.incidente_cliente'))
            
            if not nro_doc_cliente.strip():
                flash('El número de documento no puede estar vacío.', 'error')
                return redirect(url_for('incidente_bp.incidente_cliente'))
            
            # Procesar cliente
            resultado_cliente = ClienteService.obtener_o_crear_cliente(tipo_doc_cliente, nro_doc_cliente)
            if not resultado_cliente['success']:
                if 'Documento no encontrado o inválido en el sistema de consulta' in resultado_cliente['message']:
                    flash('El cliente con el documento proporcionado no existe en el sistema.', 'error')
                else:
                    flash('Error al procesar los datos del cliente. Intente nuevamente.', 'error')
                return redirect(url_for('incidente_bp.incidente_cliente'))
            
            id_cliente = resultado_cliente['cliente_id']
            flash(f'Cliente verificado exitosamente. {resultado_cliente["message"]}', 'success')
            
            
            # Validar evidencia Dropbox
            evidencia_cliente = None
            if 'evidencia' not in request.files:
                flash('Debe proporcionar evidencia del incidente.', 'error')
                return redirect(url_for('incidente_bp.incidente_cliente'))
            
            archivo_evidencia = request.files['evidencia']
            if not archivo_evidencia or archivo_evidencia.filename == '':
                flash('No se seleccionó ninguna imagen o el nombre del archivo es inválido.', 'error')
                return redirect(url_for('incidente_bp.incidente_cliente'))
            
            # Subir evidencia a Dropbox
            resultado_evidencia = dropbox_service.subir_imagen('incidecias', 'cliente', archivo_evidencia)
            if resultado_evidencia['success']:
                evidencia_cliente = resultado_evidencia['url_descarga']
                flash('Evidencia subida exitosamente.', 'success')
            else:
                flash('Error al subir la imagen a Dropbox. Intente nuevamente.', 'error')
                return redirect(url_for('incidente_bp.incidente_cliente'))
            
            
            # Validación de campos del formulario
            id_sucursal = request.form.get('sucursales')
            id_area = request.form.get('areas')
            id_empleado_reportado = request.form.get('empleado-reportado')
            id_tipo_incidencia = request.form.get('tipo-incidencia')
            descripcion = request.form.get('descripcion')
            
            # Validaciones de campos requeridos
            if not id_sucursal or not id_area:
                flash('Debe seleccionar tanto la sucursal como el área.', 'error')
                return redirect(url_for('incidente_bp.incidente_cliente'))
                
            if not id_empleado_reportado:
                flash('Debe seleccionar un empleado reportado.', 'error')
                return redirect(url_for('incidente_bp.incidente_cliente'))
                
            if not id_tipo_incidencia:
                flash('Debe seleccionar un tipo de incidencia.', 'error')
                return redirect(url_for('incidente_bp.incidente_cliente'))
            
            # Procesar incidente
            resultado_incidencia_cliente = ControlIncidente.agregar_incidente_cliente(
                id_cliente, evidencia_cliente, descripcion, 
                id_empleado_reportado, id_tipo_incidencia, id_area, id_sucursal
            )
            
            if resultado_incidencia_cliente == 0:
                flash('¡Incidencia registrada exitosamente! Gracias por reportar esta situación.', 'success')
                return redirect(url_for('incidente_bp.exito_incidente'))
            else:
                flash('Ocurrió un error al procesar la incidencia. Intente nuevamente.', 'error')
                return redirect(url_for('incidente_bp.incidente_cliente'))
                
        except Exception as e:
            flash('Error inesperado al procesar la incidencia. Por favor, intente nuevamente.', 'error')
            print(f"Error en POST incidente cliente: {str(e)}")
            return redirect(url_for('incidente_bp.incidente_cliente'))
        
@incidente_bp.route('/incidente-empleado', methods=['GET', 'POST'])
def incidente_empleado():
    if request.method == 'GET':
        try:
            sucursales = ControlSucursal.obtener_sucursales()
            areas = ControlArea.obtener_areas()
            tipos_doc = ControlTipoDoc.obtener_tipo_doc()
            tipos = ControlIncidente.obtener_tipo_incidente_empleado()
            
            if sucursales is None or areas is None or tipos_doc is None or tipos is None:
                flash('Error al cargar datos necesarios para el formulario.', 'error')
                
            return render_template('form_incidencia_empleado.html', 
                                 sucursales=sucursales, 
                                 areas=areas, 
                                 tipos_doc=tipos_doc, 
                                 tipos=tipos)
        except Exception as e:
            flash('Error inesperado al cargar el formulario. Por favor, intente nuevamente.', 'error')
            return redirect(url_for('incidente_bp.incidente_empleado'))
    
    if request.method == 'POST':
        try:
            # Validar datos del empleado reportante
            tipo_doc_empleado = request.form.get('tipo-doc-empleado')
            nro_doc_empleado = request.form.get('num-documento-empleado')
            
            if not tipo_doc_empleado or not nro_doc_empleado:
                flash('Debe seleccionar un tipo de documento y proporcionar el número.', 'error')
                return redirect(url_for('incidente_bp.incidente_empleado'))
            
            if not nro_doc_empleado.strip():
                flash('El número de documento no puede estar vacío.', 'error')
                return redirect(url_for('incidente_bp.incidente_empleado'))
            
            # Buscar empleado reportante
            id_empleado = ControlEmpleado.buscar_empleado(tipo_doc_empleado, nro_doc_empleado)
            if id_empleado == -1:
                flash('El empleado con el documento proporcionado no fue encontrado.', 'error')
                return redirect(url_for('incidente_bp.incidente_empleado'))
            else:
                flash('Empleado verificado exitosamente.', 'success')
            
            # Validar evidencia
            evidencia_empleado = None
            if 'evidencia' not in request.files:
                flash('Debe proporcionar evidencia del incidente.', 'error')
                return redirect(url_for('incidente_bp.incidente_empleado'))
            
            archivo_evidencia = request.files['evidencia']
            if not archivo_evidencia or archivo_evidencia.filename == '':
                flash('No se seleccionó ninguna imagen o el nombre del archivo es inválido.', 'error')
                return redirect(url_for('incidente_bp.incidente_empleado'))
            
            # Subir evidencia a Dropbox
            resultado_evidencia = dropbox_service.subir_imagen('incidecias', 'empleado', archivo_evidencia)
            if resultado_evidencia['success']:
                evidencia_empleado = resultado_evidencia['url_descarga']
                flash('Evidencia subida exitosamente.', 'success')
            else:
                flash('Error al subir la imagen a Dropbox. Intente nuevamente.', 'error')
                return redirect(url_for('incidente_bp.incidente_empleado'))
            
            # Validar campos del formulario
            id_sucursal = request.form.get('sucursales')
            id_area = request.form.get('areas')
            id_empleado_reportado = request.form.get('empleado-reportado')
            id_tipo_incidencia = request.form.get('tipo-incidencia')
            descripcion = request.form.get('descripcion')
            
            # Validaciones de campos requeridos
            if not id_sucursal or not id_area:
                flash('Debe seleccionar tanto la sucursal como el área.', 'error')
                return redirect(url_for('incidente_bp.incidente_empleado'))
                
            if not id_empleado_reportado:
                flash('Debe seleccionar un empleado reportado.', 'error')
                return redirect(url_for('incidente_bp.incidente_empleado'))
                
            if not id_tipo_incidencia:
                flash('Debe seleccionar un tipo de incidencia.', 'error')
                return redirect(url_for('incidente_bp.incidente_empleado'))
            
            # Procesar incidente
            resultado_incidencia_empleado = ControlIncidente.agregar_incidente_empleado(
                id_empleado, evidencia_empleado, descripcion, 
                id_empleado_reportado, id_tipo_incidencia, id_area, id_sucursal
            )
            
            if resultado_incidencia_empleado == 0:
                flash('¡Incidencia registrada exitosamente! Gracias por reportar esta situación.', 'success')
                return redirect(url_for('incidente_bp.exito_incidente'))
            elif resultado_incidencia_empleado == 6:
                flash('No se puede reportar el mismo empleado como reportado.', 'error')
                return redirect(url_for('incidente_bp.incidente_empleado'))
            else:
                flash('Ocurrió un error al procesar la incidencia. Intente nuevamente.', 'error')
                return redirect(url_for('incidente_bp.incidente_empleado'))
                
        except Exception as e:
            flash('Error inesperado al procesar la incidencia. Por favor, intente nuevamente.', 'error')
            print(f"Error en POST incidente empleado: {str(e)}")
            return redirect(url_for('incidente_bp.incidente_empleado'))

@incidente_bp.route('/exito-incidente')
def exito_incidente():
    return render_template('agrad_incidencia.html')


@incidente_bp.route('/qr-incidentes-clientes')
def generar_qr_incidentes_clientes():
    return GeneradorQR.qr_incidentes_clientes()

@incidente_bp.route('/qr-incidentes-empleados')
def generar_qr_incidentes_empleados():
    return GeneradorQR.qr_incidentes_empleados()