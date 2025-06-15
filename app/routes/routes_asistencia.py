from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.controllers.control_asistencia import ControlAsistencia
from app.controllers.control_empleado import ControlEmpleado
from app.controllers.control_tipo_doc import ControlTipoDoc
from datetime import datetime

asistencia_bp = Blueprint('asistencia_bp', __name__)

@asistencia_bp.route('/asistencia-empleados', methods=['GET', 'POST'])
def asistencia_empleados():
    if request.method == 'GET':
        try:
            tipos_doc = ControlTipoDoc.obtener_tipo_doc()
            
            if tipos_doc is None:
                flash('Error al cargar datos necesarios para el formulario.', 'error')
                
            return render_template('form_asistencia.html', tipos_doc=tipos_doc)
        except Exception as e:
            flash('Error inesperado al cargar el formulario. Por favor, intente nuevamente.', 'error')
            return redirect(url_for('asistencia_bp.asistencia_empleados'))
    
    if request.method == 'POST':
        try:
            # Validar datos del empleado
            id_tipo_doc = request.form.get('tipo-doc-empleado-asistencia')
            nro_doc = request.form.get('num-documento-asistencia')
            
            if not id_tipo_doc or not nro_doc:
                flash('Debe seleccionar un tipo de documento y proporcionar el número.', 'error')
                return redirect(url_for('asistencia_bp.asistencia_empleados'))
            
            if not nro_doc.strip():
                flash('El número de documento no puede estar vacío.', 'error')
                return redirect(url_for('asistencia_bp.asistencia_empleados'))
            
            # Buscar empleado
            id_empleado = ControlEmpleado.buscar_empleado(id_tipo_doc, nro_doc)
            if id_empleado == 0:
                flash('El empleado con el documento proporcionado no existe en el sistema.', 'error')
                return redirect(url_for('asistencia_bp.asistencia_empleados'))
            elif id_empleado == -1:
                flash('Error al buscar el empleado en el sistema. Intente nuevamente.', 'error')
                return redirect(url_for('asistencia_bp.asistencia_empleados'))
            
            # Obtener hora actual
            hora_actual = datetime.now().strftime('%H:%M:%S')
            
            # Registrar asistencia
            resultado_asistencia = ControlAsistencia.registrar_asistencia(id_empleado, hora_actual)
            if resultado_asistencia == 1:
                flash('¡Entrada registrada exitosamente! Asistencia presente.', 'success')
                return redirect(url_for('asistencia_bp.asistencia_empleados'))
            elif resultado_asistencia == 2:
                flash('Entrada registrada con tardanza. Recuerde ser más puntual.', 'warning')
                return redirect(url_for('asistencia_bp.asistencia_empleados'))
            elif resultado_asistencia == 4:
                flash('¡Salida temprana registrada exitosamente!', 'success')
                return redirect(url_for('asistencia_bp.asistencia_empleados'))
            elif resultado_asistencia == 5:
                flash('¡Salida registrada exitosamente! Horario normal cumplido.', 'success')
                return redirect(url_for('asistencia_bp.asistencia_empleados'))
            elif resultado_asistencia == 6:
                flash('Salida registrada fuera del horario ideal, pero dentro del rango permitido.', 'warning')
                return redirect(url_for('asistencia_bp.asistencia_empleados'))
            elif resultado_asistencia == 7:
                flash('Registro de asistencia automático creado. Marque su entrada en el horario correspondiente.', 'info')
                return redirect(url_for('asistencia_bp.asistencia_empleados'))
            elif resultado_asistencia == 8:
                flash('Ya ha registrado su entrada y salida para el día de hoy.', 'warning')
                return redirect(url_for('asistencia_bp.asistencia_empleados'))
            elif resultado_asistencia == 9:
                flash('La hora de salida está fuera del rango permitido (16:30 - 18:00).', 'error')
                return redirect(url_for('asistencia_bp.asistencia_empleados'))
            elif resultado_asistencia == 10:
                flash('Hora de entrada actualizada para registro previamente justificado.', 'info')
                return redirect(url_for('asistencia_bp.asistencia_empleados'))
            elif resultado_asistencia == 11:
                flash('Hora de salida actualizada para registro previamente justificado.', 'info')
                return redirect(url_for('asistencia_bp.asistencia_empleados'))
            elif resultado_asistencia == 12:
                flash('No se puede marcar salida sin haber registrado una entrada válida o justificada.', 'error')
                return redirect(url_for('asistencia_bp.asistencia_empleados'))
            elif resultado_asistencia == 3:
                flash('La hora de entrada está fuera del rango permitido (09:40 - 12:00).', 'error')
                return redirect(url_for('asistencia_bp.asistencia_empleados'))
            else:
                flash(f'Código de respuesta no reconocido: {resultado_asistencia}. Contacte al administrador.', 'error')
                return redirect(url_for('asistencia_bp.asistencia_empleados'))
                
        except Exception as e:
            flash('Error inesperado al procesar la asistencia. Por favor, intente nuevamente.', 'error')
            print(f"Error en POST asistencia: {str(e)}")
            return redirect(url_for('asistencia_bp.asistencia_empleados'))