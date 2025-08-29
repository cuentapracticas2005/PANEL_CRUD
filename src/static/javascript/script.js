// Mostrar / ocultar el input extraOpciones
function toggleOpciones() {
    const opciones = document.getElementById('extraOpciones');
    opciones.classList.toggle('hidden');
}

// FUNCION PARA GENERAR CODIGO MODAL AGREGAR
function generarCodigo() {
    const numeroPlano = document.getElementById("numero_plano");
    const extraOpciones = document.getElementById("extraOpciones");

    // Obtener valores de los selects
    const tipoPlano = document.getElementById("tipo_plano").value;
    const tamano = document.getElementById("tamano").value;
    const version = document.getElementById("version").value;
    const subrevision = document.getElementById("subrevision").value;

    // 🔹 Verificar si al menos uno de los selects tiene un valor
    const algunSelectLleno = tipoPlano || tamano || version || subrevision;

    // 🔹 Si hay algún select lleno pero faltan otros → mostrar alerta
    if (algunSelectLleno && (!tipoPlano || !tamano || !version || !subrevision)) {
        alert("Por favor selecciona todas las opciones antes de generar el código.");
        return;
    }

    // 🔹 Si no hay ningún select seleccionado, simplemente no hace nada
    if (!algunSelectLleno) {
        return;
    }

    // Construcción del código con la lógica solicitada
    // Formato: TIPO - 300000 - TAMAÑO - VERSION - SUBREVISION
    const codigo = `${tipoPlano}-300000-${tamano}${version}${subrevision}`;

    // Insertar en el input de número de plano
    numeroPlano.value = codigo;

    // Al generar un código, bloqueamos el input extraOpciones
    extraOpciones.disabled = true;
}



// FUNCION PARA GENERAR CODIGO EN MODAL REUTILIZAR
function generarCodigoReutilizar() {
    const numeroPlano = document.getElementById("numero_plano");
    const extraOpciones = document.getElementById("extraOpciones");

    // Si ya hay algo escrito en extraOpciones no se permite generar
    if (extraOpciones.value.trim() !== "") {
        alert("No puedes generar código si has escrito en Extra Opciones.");
        return;
    }

    // Obtener valores de los selects
    const tipoPlano = document.getElementById("tipo_plano").value;
    const tamano = document.getElementById("tamano").value;
    const version = document.getElementById("version").value;
    const subrevision = document.getElementById("subrevision").value;

    // Validación: si falta algún campo, avisamos
    if (!tamano || !version || !subrevision) {
        alert("Por favor selecciona todas las opciones antes de generar el código.");
        return;
    }

    // Construcción del código con la lógica solicitada
    // Formato: TIPO - 300000 - TAMAÑO - VERSION - SUBREVISION
    const codigo = `${tipoPlano}-300000-${tamano}${version}${subrevision}`;

    // Insertar en el input de número de plano
    numeroPlano.value = codigo;

    // Al generar un código, bloqueamos el input extraOpciones
    extraOpciones.disabled = true;
}


// LOGICA DE VALIDACION PARA DESHABILITAR Y HABILITAR INPUTS
document.addEventListener("input", () => {
    const extraOpciones = document.getElementById("extraOpciones");
    const selects = document.querySelectorAll("#tipo_plano, #tamano, #version, #subrevision");

    // 🔹 Si el usuario escribe en extraOpciones → bloquear selects
    if (extraOpciones.value.trim() !== "") {
        selects.forEach(sel => sel.disabled = true);
    } else {
        selects.forEach(sel => sel.disabled = false);
    }

    // 🔹 Si cualquiera de los selects tiene un valor → bloquear extraOpciones
    let algunSelectLleno = Array.from(selects).some(sel => sel.value.trim() !== "" || sel.value === " ");
    if (algunSelectLleno) {
        extraOpciones.disabled = true;
    } else {
        extraOpciones.disabled = false;
    }
});


//FUNCION PARA AGREGAR FECHA ACTUAL
function colocarFechaActual(checkbox) {
    const fechaInput = checkbox.closest("div").querySelector(".fecha-input");

    if (checkbox.checked) {
        const hoy = new Date();
        const year = hoy.getFullYear();
        const month = String(hoy.getMonth() + 1).padStart(2, "0");
        const day = String(hoy.getDate()).padStart(2, "0");
        fechaInput.value = `${year}-${month}-${day}`;
    } else {
        fechaInput.value = "";
    }
}