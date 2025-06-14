document.addEventListener('DOMContentLoaded', function () {
    const tipoDocRadios = document.querySelectorAll('input[name="tipo-documento-empleado"]');
    const numDocumentoInput = document.getElementById('num-documento-empleado');
    const tipoEventoRadios = document.querySelectorAll('input[name="tipo-evento"]');
    const fechaInput = document.getElementById('fechas-justificar-input');
    const evidenciaInput = document.getElementById('evidencia');

    // Deshabilitar campos inicialmente
    numDocumentoInput.disabled = true;
    fechaInput.disabled = true;

    let tipoDocSeleccionado = false;
    let numDocLlenado = false;
    let tipoEventoSeleccionado = false;

    function verificarHabilitarFechas() {
        if (tipoDocSeleccionado && numDocLlenado && tipoEventoSeleccionado) {
            fechaInput.disabled = false;
        } else {
            fechaInput.disabled = true;
        }
    }

    // Activar número de documento cuando se seleccione el tipo de documento
    tipoDocRadios.forEach(radio => {
        radio.addEventListener('change', function () {
            tipoDocSeleccionado = true;
            numDocumentoInput.disabled = false;
            numDocumentoInput.value = '';
            verificarHabilitarFechas();
        });
    });

    // Validar que el número de documento esté lleno
    numDocumentoInput.addEventListener('input', function () {
        numDocLlenado = this.value.trim().length > 0;
        verificarHabilitarFechas();
    });

    // Verificar cuando se seleccione tipo de evento
    tipoEventoRadios.forEach(radio => {
        radio.addEventListener('change', function () {
            tipoEventoSeleccionado = true;
            verificarHabilitarFechas();
        });
    });

    // Validación de tipo de archivo (solo imágenes)
    evidenciaInput.addEventListener('change', function () {
        const file = evidenciaInput.files[0];
        if (file) {
            const fileType = file.type;
            const validImageTypes = ['image/jpeg', 'image/png', 'image/jpg', 'image/gif'];
            if (!validImageTypes.includes(fileType)) {
                alert("Por favor, sube un archivo de imagen válido (JPG, PNG, GIF).");
                evidenciaInput.value = '';
            }
        }
    });
});
