document.addEventListener('DOMContentLoaded', function() {
        // Obtener la fecha y hora actuales
        const fechaActual = new Date();
        
        // Formatear la fecha
        const opcionesFecha = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        const fechaFormateada = fechaActual.toLocaleDateString('es-PE', opcionesFecha);
        
        // Formatear la hora
        const opcionesHora = { hour: '2-digit', minute: '2-digit', second: '2-digit' };
        const horaFormateada = fechaActual.toLocaleTimeString('es-PE', opcionesHora);
        
        // Actualizar los elementos HTML con la fecha y hora actuales
        document.getElementById('fecha').textContent = fechaFormateada;
        document.getElementById('hora').textContent = horaFormateada;
    });