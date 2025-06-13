// Sistema dinámico de calificaciones - Detecta automáticamente todos los grupos de estrellas
const calificaciones = {};

// Textos descriptivos para cada calificación
const textosCalificacion = {
    1: "Muy malo",
    2: "Malo", 
    3: "Regular",
    4: "Bueno",
    5: "Excelente"
};

// Inicializar el sistema de preguntas 'Si o No'
function inicializarSiNo() {
    const preguntasSiNo = document.querySelectorAll('input[type="radio"][name^="pregunta"]');

    preguntasSiNo.forEach(input => {
        input.addEventListener('change', function() {
            const group = this.name;
            const value = this.value;
            
            if (value === "si") {
                calificaciones[group] = 5;
            } else {
                calificaciones[group] = 0;
            }
            
            removerMensajeError(group);
        });
    });
}

// Inicializar el sistema de preguntas estrellas
function inicializarEstrellas() {
    const gruposEstrella = document.querySelectorAll('[data-rating-group]');
    
    gruposEstrella.forEach(grupo => {
        const nombreGrupo = grupo.dataset.ratingGroup;
        calificaciones[nombreGrupo] = 0;
    });

    const starButtons = document.querySelectorAll('.star-btn');
    
    starButtons.forEach(button => {
        button.addEventListener('click', function() {
            const rating = parseInt(this.dataset.rating);
            const group = this.dataset.group;
            seleccionarCalificacion(group, rating);
        });

        button.addEventListener('mouseenter', function() {
            const rating = parseInt(this.dataset.rating);
            const group = this.dataset.group;
            previsualizarCalificacion(group, rating);
        });
    });

    gruposEstrella.forEach(grupo => {
        grupo.addEventListener('mouseleave', function() {
            const groupName = this.dataset.ratingGroup;
            actualizarEstrellas(groupName, calificaciones[groupName]);
        });
    });
}

// Función para seleccionar una calificación
function seleccionarCalificacion(group, rating) {
    calificaciones[group] = rating;
    actualizarEstrellas(group, rating);
    
    const hiddenInput = document.getElementById(group + '-value');
    if (hiddenInput) {
        hiddenInput.value = rating;
    }
    
    const textoElemento = document.getElementById(group + '-text');
    if (textoElemento) {
        textoElemento.textContent = `${rating} estrella${rating > 1 ? 's' : ''} - ${textosCalificacion[rating]}`;
        textoElemento.className = 'text-sm text-blue-600 font-medium';
    }
    
    removerMensajeError(group);
}

// Función para previsualizar calificación en hover
function previsualizarCalificacion(group, rating) {
    actualizarEstrellas(group, rating);
}

// Función para actualizar la visualización de las estrellas
function actualizarEstrellas(group, rating) {
    const groupContainer = document.querySelector(`[data-rating-group="${group}"]`);
    if (!groupContainer) return;
    
    const stars = groupContainer.querySelectorAll('.star-btn');
    
    stars.forEach((star, index) => {
        const starRating = index + 1;
        const svg = star.querySelector('svg');
        
        if (starRating <= rating) {
            svg.classList.remove('text-gray-300');
            svg.classList.add('text-yellow-400');
        } else {
            svg.classList.remove('text-yellow-400');
            svg.classList.add('text-gray-300');
        }
    });
}

// Función para validar que todas las preguntas estén respondidas
function validarFormulario() {
    let esValido = true;
    const errores = [];
    
    // Obtener todas las preguntas de estrellas
    const gruposEstrella = document.querySelectorAll('[data-rating-group]');
    gruposEstrella.forEach(grupo => {
        const nombreGrupo = grupo.dataset.ratingGroup;
        if (!calificaciones[nombreGrupo] || calificaciones[nombreGrupo] === 0) {
            mostrarMensajeError(nombreGrupo, 'Por favor seleccione una calificación');
            errores.push(`Pregunta ${nombreGrupo} sin responder`);
            esValido = false;
        }
    });
    
    // Obtener todas las preguntas de Sí/No
    const preguntasSiNo = document.querySelectorAll('input[type="radio"][name^="pregunta"]');
    const gruposSiNo = new Set();
    
    preguntasSiNo.forEach(input => {
        gruposSiNo.add(input.name);
    });
    
    gruposSiNo.forEach(nombreGrupo => {
        const radioSeleccionado = document.querySelector(`input[name="${nombreGrupo}"]:checked`);
        if (!radioSeleccionado) {
            mostrarMensajeError(nombreGrupo, 'Por favor seleccione una opción');
            errores.push(`Pregunta ${nombreGrupo} sin responder`);
            esValido = false;
        }
    });
    
    if (!esValido) {
        // Hacer scroll al primer error
        const primerError = document.querySelector('.mensaje-error');
        if (primerError) {
            primerError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
    
    return esValido;
}

// Función para mostrar mensaje de error
function mostrarMensajeError(nombrePregunta, mensaje) {
    // Remover mensaje de error previo si existe
    removerMensajeError(nombrePregunta);
    
    // Buscar el contenedor de la pregunta
    let contenedor = null;
    
    // Para preguntas de estrellas
    const grupoEstrella = document.querySelector(`[data-rating-group="${nombrePregunta}"]`);
    if (grupoEstrella) {
        contenedor = grupoEstrella.closest('.mb-5');
    } else {
        // Para preguntas de Sí/No
        const radioInput = document.querySelector(`input[name="${nombrePregunta}"]`);
        if (radioInput) {
            contenedor = radioInput.closest('.mb-5');
        }
    }
    
    if (contenedor) {
        const mensajeError = document.createElement('div');
        mensajeError.className = 'mensaje-error text-red-600 text-sm mt-2 font-medium';
        mensajeError.id = `error-${nombrePregunta}`;
        mensajeError.textContent = mensaje;
        contenedor.appendChild(mensajeError);
        
        // Agregar borde rojo al contenedor
        contenedor.classList.add('border', 'border-red-300', 'rounded-lg', 'p-3', 'bg-red-50');
    }
}

// Función para remover mensaje de error
function removerMensajeError(nombrePregunta) {
    const mensajeError = document.getElementById(`error-${nombrePregunta}`);
    if (mensajeError) {
        mensajeError.remove();
        
        // Remover estilos de error del contenedor
        const contenedor = mensajeError.closest('.mb-5');
        if (contenedor) {
            contenedor.classList.remove('border', 'border-red-300', 'rounded-lg', 'p-3', 'bg-red-50');
        }
    }
}

// Función para manejar el envío del formulario
function manejarEnvioFormulario(event) {
    event.preventDefault(); // Prevenir envío automático
    
    if (validarFormulario()) {
        // Calcular y asignar el promedio al campo oculto antes de enviar
        const promedioCalculado = calcularPromedio();
        const campoPromedio = document.getElementById('promedio-encuesta');
        if (campoPromedio) {
            campoPromedio.value = promedioCalculado;
        }
        
        // Si la validación pasa, enviar el formulario
        document.getElementById('formulario-encuesta').submit();
    }
}

// Función para calcular el promedio de calificaciones
function calcularPromedio() {
    const valores = Object.values(calificaciones);
    if (valores.length === 0) return 0;
    
    const suma = valores.reduce((acc, val) => acc + val, 0);
    return (suma / valores.length).toFixed(2);
}

// Inicializar cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    inicializarEstrellas();
    inicializarSiNo();
    
    // Agregar evento de validación al formulario
    const formulario = document.getElementById('formulario-encuesta');
    if (formulario) {
        formulario.addEventListener('submit', manejarEnvioFormulario);
    }
});