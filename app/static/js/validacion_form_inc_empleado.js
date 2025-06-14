document.addEventListener('DOMContentLoaded', function () {
    const fechaIncidente = document.getElementById('fecha-incidente-empleado');
    const tipoDocRadios = document.querySelectorAll('input[name="tipo-doc-empleado"]');
    const numDocumentoInput = document.getElementById('num-documento-empleado');
    const sucursalesSelect = document.getElementById('sucursales');
    const areasSelect = document.getElementById('areas');
    const empleadoSelect = document.getElementById('empleado');
    const evidenciaInput = document.getElementById('evidencia');
    
    // Asignar fecha actual al campo de fecha del incidente
    const actual = new Date().toISOString().split('T')[0];
    fechaIncidente.value = actual;

    // Deshabilitar campos inicialmente
    numDocumentoInput.disabled = true;
    areasSelect.disabled = true;
    empleadoSelect.disabled = true;

    // Validación de tipo de documento (habilitar el número de documento cuando se seleccione)
    tipoDocRadios.forEach(radio => {
        radio.addEventListener('change', function () {
            numDocumentoInput.value = '';
            numDocumentoInput.disabled = false;
            numDocumentoInput.removeEventListener('input', validarNroDocumento);

            const tipoDoc = this.value;
            if (tipoDoc === 'dni') {
                numDocumentoInput.placeholder = 'Ingrese su número de DNI';
                validarNroDocumento(numDocumentoInput, 8);
            } else if (tipoDoc === 'carne') {
                numDocumentoInput.placeholder = 'Ingrese su número de carnet de extranjería';
                validarNroDocumento(numDocumentoInput, 9);
            } else if (tipoDoc === 'ruc') {
                numDocumentoInput.placeholder = 'Ingrese su número de RUC';
                validarNroDocumento(numDocumentoInput, 11);
            }
        });
    });

    // Validación de sucursal (habilitar área cuando se seleccione una sucursal)
    sucursalesSelect.addEventListener('change', function () {
        areasSelect.disabled = false;
        areasSelect.selectedIndex = 0;
        empleadoSelect.disabled = true;
        empleadoSelect.selectedIndex = 0;
    });

    // Validación de área (habilitar empleado cuando se seleccione un área)
    areasSelect.addEventListener('change', function () {
        empleadoSelect.disabled = false;
        empleadoSelect.selectedIndex = 0;

        const id_sucursal = sucursalesSelect.value;
        const id_area = this.value;

        fetch(`/obtener-empleados/${id_sucursal}/${id_area}`)
            .then(response => response.json())
            .then(data => {
                empleadoSelect.innerHTML = '<option value="" disabled selected>Seleccionar Empleado---</option>';
                data.data.forEach(empleado => {
                    const option = document.createElement('option');
                    option.value = empleado.id_empleado;
                    option.textContent = empleado.nombre;
                    empleadoSelect.appendChild(option);
                });
            })
            .catch(error => console.error('Error al cargar empleados:', error));
    });

    // Validación para aceptar solo imágenes en el campo de archivo
    evidenciaInput.addEventListener('change', function () {
        const file = evidenciaInput.files[0];
        if (file) {
            const fileType = file.type;
            const validImageTypes = ['image/jpeg', 'image/png', 'image/jpg', 'image/gif'];
            if (!validImageTypes.includes(fileType)) {
                alert("Por favor, sube un archivo de imagen (JPG, PNG, GIF).");
                evidenciaInput.value = '';
            }
        }
    });
});

function validarNroDocumento(campo, maxCaracteres) {
    campo.addEventListener('input', function() {
        campo.value = campo.value.replace(/\D/g, '');
        if (this.value.length > maxCaracteres) {
            campo.value = campo.value.slice(0, maxCaracteres);
        }
    });
}