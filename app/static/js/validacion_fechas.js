let fechasSeleccionadas = [];
let flatpickrInstance = null;
   
// Función para generar fechas futuras
function generarFechasFuturas() {
    const fechasFuturas = [];
    const fechaActual = new Date();
    for (let i = 0; i < 7; i++) {
        const fecha = new Date(fechaActual);
        fecha.setDate(fechaActual.getDate() + i);
        fechasFuturas.push(fecha);
    }
    return fechasFuturas;
}

// Convertir fechas String a formato Date
function convertirFechasStringADate(fechasString) {
    return fechasString.map(fechaStr => {
        const fecha = new Date(fechaStr);
        fecha.setHours(0, 0, 0, 0);
        return fecha;
    });
}

// Función para convertir fecha de dd/mm/yyyy a yyyy-mm-dd
function convertirFechaAFormatoISO(fechaStr) {
    const partes = fechaStr.split('/');
    if (partes.length === 3) {
        const dia = partes[0].padStart(2, '0');
        const mes = partes[1].padStart(2, '0');
        const año = partes[2];
        return `${año}-${mes}-${dia}`;
    }
    return fechaStr;
}

// Función para convertir fecha de yyyy-mm-dd a dd/mm/yyyy
function convertirFechaAFormatoDisplay(fechaISO) {
    const fecha = new Date(fechaISO);
    const dia = fecha.getDate().toString().padStart(2, '0');
    const mes = (fecha.getMonth() + 1).toString().padStart(2, '0');
    const año = fecha.getFullYear();
    return `${dia}/${mes}/${año}`;
}

// Combinar fechas pasadas y futuras
function combinarFechasHabilitadas(fechasBD = []) {
    const fechasFuturas = generarFechasFuturas();
    let fechasCombinadas = [...fechasFuturas]; // Empezar con fechas futuras
    
    console.log('Fechas futuras generadas:', fechasFuturas.map(f => f.toLocaleDateString('es-ES')));
    
    // Si hay fechas de la BD, convertirlas y agregarlas
    if (fechasBD && fechasBD.length > 0) {
        const fechasBDConvertidas = convertirFechasStringADate(fechasBD);
        console.log('Fechas BD convertidas:', fechasBDConvertidas.map(f => f.toLocaleDateString('es-ES')));
        fechasCombinadas = [...fechasCombinadas, ...fechasBDConvertidas];
    }
    
    // Eliminar duplicados y ordenar
    const fechasUnicas = fechasCombinadas.filter((fecha, index, array) => {
        return array.findIndex(f => f.getTime() === fecha.getTime()) === index;
    });
    
    const fechasOrdenadas = fechasUnicas.sort((a, b) => a - b);
    console.log('Fechas finales habilitadas:', fechasOrdenadas.map(f => f.toLocaleDateString('es-ES')));
    
    return fechasOrdenadas;
}

// Configuración del datepicker con Flatpickr
function inicializarFlatpickr(fechasBD = []) {
    // Si ya existe una instancia, la destruimos
    if (flatpickrInstance) {
        flatpickrInstance.destroy();
    }

    const fechasHabilitadas = combinarFechasHabilitadas(fechasBD);
    
    flatpickrInstance = flatpickr("#fechas-justificar-input", {
        mode: "single", // Modo single para seleccionar una fecha a la vez
        dateFormat: "d/m/Y",
        locale: "es",
        allowInput: false,
        clickOpens: true,
        enable: fechasHabilitadas, // Fechas habilitadas dinámicamente
        onChange: function(selectedDates, dateStr, instance) {
            if (selectedDates.length > 0) {
                agregarFecha(dateStr);
                instance.clear();
            }
        }
    });
}

// Funciones para APIs
async function obtenerIdEmpleado(tipoDocumento, numDocumento) {
    const response = await fetch(`/obtener-empleado/${tipoDocumento}/${numDocumento}`);
    const data = await response.json();
    return data.id_empleado;
}

async function obtenerFechasDesdeAPI(idEmpleado, tipoEvento) {
    try {
        const response = await fetch(`/obtener-fechas/${idEmpleado}/${tipoEvento}`);
        const data = await response.json();
        
        if (data.status === 1 && data.data && data.data.length > 0) {
            console.log(data.data)
            return data.data
        } else {
            console.log('No se encontraron fechas:', data.message);
            return [];
        }
    } catch (error) {
        console.error('Error al obtener fechas:', error);
        return [];
    }
}

async function manejarCambioTipoEvento() {
    const tipoEventoSeleccionado = document.querySelector('input[name="tipo-evento"]:checked');
    const numDocumento = document.getElementById('num-documento-empleado').value;
    const tipoDocumento = document.querySelector('input[name="tipo-documento-empleado"]:checked');
    
    if (!tipoEventoSeleccionado || !numDocumento || !tipoDocumento) {
        inicializarFlatpickr([]);
        return;
    }
    
    try {
        const idEmpleado = await obtenerIdEmpleado(tipoDocumento.value, numDocumento);
        const fechasHabilitadas = await obtenerFechasDesdeAPI(idEmpleado, tipoEventoSeleccionado.value);
        
        inicializarFlatpickr(fechasHabilitadas);
        
        fechasSeleccionadas = [];
        actualizarDisplayFechas();
        actualizarInputHidden();
        actualizarValidacionFormulario();
        
    } catch (error) {
        console.error('Error al procesar cambio de tipo de evento:', error);
        inicializarFlatpickr([]);
    }
}

// Función para agregar una fecha
function agregarFecha(fechaStr) {
    // Verificar si la fecha ya está seleccionada
    if (!fechasSeleccionadas.includes(fechaStr)) {
        fechasSeleccionadas.push(fechaStr);
        actualizarDisplayFechas();
        actualizarInputHidden();
        actualizarValidacionFormulario();
    }
}
            
// Función para eliminar una fecha
function eliminarFecha(fechaStr) {
    const index = fechasSeleccionadas.indexOf(fechaStr);
    if (index > -1) {
        fechasSeleccionadas.splice(index, 1);
        actualizarDisplayFechas();
        actualizarInputHidden();
        actualizarValidacionFormulario();
    }
}
            
// Función para actualizar la visualización de fechas
function actualizarDisplayFechas() {
    const container = document.getElementById('fechas-seleccionadas-list');
    container.innerHTML = '';
    
    fechasSeleccionadas.forEach(fecha => {
        const fechaTag = document.createElement('div');
        fechaTag.className = 'inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800 border border-blue-200';
        fechaTag.innerHTML = `
            <span class="mr-2">${fecha}</span>
            <button 
                type="button" 
                onclick="eliminarFecha('${fecha}')" 
                class="ml-1 text-blue-600 hover:text-blue-800 focus:outline-none"
                aria-label="Eliminar fecha ${fecha}">
                <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                </svg>
            </button>
        `;
        container.appendChild(fechaTag);
    });
    
    // Mostrar mensaje si no hay fechas seleccionadas
    if (fechasSeleccionadas.length === 0) {
        const mensajeVacio = document.createElement('div');
        mensajeVacio.className = 'text-gray-500 text-sm italic';
        mensajeVacio.textContent = 'No hay fechas seleccionadas';
        container.appendChild(mensajeVacio);
    }
}
            
// Función para actualizar el input hidden - CORREGIDA
function actualizarInputHidden() {
    const hiddenInput = document.getElementById('fechas-justificar-hidden');
    // Convertir todas las fechas a formato ISO antes de enviarlas
    const fechasISO = fechasSeleccionadas.map(fecha => convertirFechaAFormatoISO(fecha));
    hiddenInput.value = fechasISO.join(', ');
}
            
// Función para actualizar la validación del formulario
function actualizarValidacionFormulario() {
    const inputVisible = document.getElementById('fechas-justificar-input');
    if (fechasSeleccionadas.length > 0) {
        inputVisible.removeAttribute('required');
        inputVisible.setCustomValidity('');
    } else {
        inputVisible.setAttribute('required', 'required');
        inputVisible.setCustomValidity('Debe seleccionar al menos una fecha');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar Flatpickr sin fechas específicas
    inicializarFlatpickr([]);
    
    // Inicializar la vista
    actualizarDisplayFechas();
    actualizarValidacionFormulario();
    
    // Event listeners para cambios en tipo de evento
    document.querySelectorAll('input[name="tipo-evento"]').forEach(radio => {
        radio.addEventListener('change', manejarCambioTipoEvento);
    });
    
    // Event listener para cambios en número de documento
    document.getElementById('num-documento-empleado').addEventListener('blur', manejarCambioTipoEvento);
    
    // Event listeners para cambios en tipo de documento
    document.querySelectorAll('input[name="tipo-documento-empleado"]').forEach(radio => {
        radio.addEventListener('change', manejarCambioTipoEvento);
    });
});