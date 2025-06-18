from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from app.controllers.control_encuesta import ControlEncuesta
from app.controllers.control_empleado import ControlEmpleado
from app.controllers.control_tipo_doc import ControlTipoDoc
from app.utils.generador_qr import GeneradorQR

encuesta_bp = Blueprint('encuesta_bp', __name__)

@encuesta_bp.route('/')
def index():
    total_encuestas = ControlEncuesta.filtro_1()
    habilitadas = ControlEncuesta.filtro_2()
    para_clientes = ControlEncuesta.filtro_3()
    para_empleados = ControlEncuesta.filtro_4()
    encuestas = ControlEncuesta.mostrar_encuestas()
    return render_template('menu_encuestas.html', 
                           total_encuestas=total_encuestas, 
                           habilitadas=habilitadas, 
                           para_clientes=para_clientes, 
                           para_empleados=para_empleados, 
                           encuestas=encuestas)
    

@encuesta_bp.route('/encuesta/<int:id_encuesta>', methods=['GET', 'POST'])
def encuesta(id_encuesta):
    if request.method == 'GET':
        try:
            encuesta = ControlEncuesta.obtener_encuesta(id_encuesta)
            if not encuesta:
                flash('La encuesta solicitada no existe o no está disponible.', 'error')
                return redirect(url_for('encuesta_bp.index'))
            
            preguntas = ControlEncuesta.obtener_preguntas_encuesta(id_encuesta)
            tipos_doc = ControlTipoDoc.obtener_tipo_doc()
            return render_template('form_encuesta.html', encuesta=encuesta, preguntas=preguntas, tipos_doc=tipos_doc)
        except Exception as e:
            flash('Error al cargar la encuesta. Por favor, intente nuevamente.', 'error')
            print('No se encontró la encuesta:', str(e))
            return redirect(url_for('encuesta_bp.index'))
    
    if request.method == 'POST':
        try:
            # Campos para el empleado (si la encuesta fuese para empleados)
            id_tipo_doc = request.form.get('tipo-doc-empleado')
            nro_doc = request.form.get('num-documento-empleado')
            
            # Campos generales
            puntaje = request.form.get('promedio-encuesta')
            if not puntaje:
                flash('Error: No se pudo calcular el puntaje de la encuesta. Por favor, responda todas las preguntas.', 'error')
                return redirect(url_for('encuesta_bp.encuesta', id_encuesta=id_encuesta))
            
            try:
                promedio = float(puntaje)
            except ValueError:
                flash('Error: Puntaje inválido. Por favor, intente nuevamente.', 'error')
                return redirect(url_for('encuesta_bp.encuesta', id_encuesta=id_encuesta))
            
            if id_tipo_doc and nro_doc:
                if not nro_doc.strip():
                    flash('Por favor, ingrese un número de documento válido.', 'error')
                    return redirect(url_for('encuesta_bp.encuesta', id_encuesta=id_encuesta))
                
                id_empleado = ControlEmpleado.buscar_empleado(id_tipo_doc, nro_doc)
                if id_empleado == -1:
                    flash('Empleado no encontrado. Verifique el tipo y número de documento ingresado.', 'error')
                    return redirect(url_for('encuesta_bp.encuesta', id_encuesta=id_encuesta))
                else:
                    resultado_encuesta = ControlEncuesta.guardar_encuesta_empleado(id_encuesta, id_empleado, promedio)
                    
                    if resultado_encuesta == 0:
                        flash('¡Encuesta enviada exitosamente! Gracias por su participación.', 'success')
                    else:
                        flash('Error al guardar la encuesta. Por favor, intente nuevamente.', 'error')
                        return redirect(url_for('encuesta_bp.encuesta', id_encuesta=id_encuesta))
                    
                    return redirect(url_for('encuesta_bp.exito_encuesta', id_encuesta=id_encuesta))
            else:
                resultado_encuesta = ControlEncuesta.guardar_encuesta_cliente(id_encuesta, promedio)
                print(resultado_encuesta)
                
                if resultado_encuesta == 0:
                    flash('¡Encuesta enviada exitosamente! Gracias por su participación.', 'success')
                else:
                    flash('Error al guardar la encuesta. Por favor, intente nuevamente.', 'error')
                    return redirect(url_for('encuesta_bp.encuesta', id_encuesta=id_encuesta))
                
                return redirect(url_for('encuesta_bp.exito_encuesta', id_encuesta=id_encuesta))
                
        except Exception as e:
            flash('Error inesperado al procesar la encuesta. Por favor, intente nuevamente.', 'error')
            print(f"Error en POST encuesta: {str(e)}")
            return redirect(url_for('encuesta_bp.encuesta', id_encuesta=id_encuesta))
        
@encuesta_bp.route('/exito-encuesta/<int:id_encuesta>')
def exito_encuesta(id_encuesta):
    try:
        encuesta = ControlEncuesta.obtener_encuesta(id_encuesta)
        if not encuesta:
            flash('La encuesta solicitada no existe o no está disponible.', 'error')
            return redirect(url_for('encuesta_bp.encuesta', id_encuesta=id_encuesta))
            
        return render_template('agrad_encuesta.html', encuesta=encuesta)
    except Exception as e:
        flash('Error al cargar la encuesta. Por favor, intente nuevamente.', 'error')
        return redirect(url_for('encuesta_bp.encuesta', id_encuesta=id_encuesta))   
    

@encuesta_bp.route('/qr/<int:id_encuesta>')
def generar_qr_encuesta(id_encuesta):
    return GeneradorQR.qr_encuesta(id_encuesta)