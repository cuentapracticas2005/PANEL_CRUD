// Mostrar / ocultar el input extraOpciones
function toggleOpciones() {
    const opciones = document.getElementById('extraOpciones');
    opciones.classList.toggle('hidden');
}

// Función de generar código automático
function generarCodigo() {
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
    const revision = document.getElementById("revision").value;
    const subrevision = document.getElementById("subrevision").value;

    // Validación: si falta algún campo, avisamos
    if (!tipoPlano || !tamano || !revision || !subrevision) {
        alert("Por favor selecciona todas las opciones antes de generar el código.");
        return;
    }

    // Construcción del código con la lógica solicitada
    // Formato: TIPO - 300000 - TAMAÑO - REVISION - SUBREVISION
    const codigo = `${tipoPlano}-300000-${tamano}${revision}${subrevision}`;

    // Insertar en el input de número de plano
    numeroPlano.value = codigo;

    // Al generar un código, bloqueamos el input extraOpciones
    extraOpciones.disabled = true;
}


// Lógica de validación dinámica (se ejecuta cada vez que se escribe en los inputs)
document.addEventListener("input", () => {
    const numeroPlano = document.getElementById("numero_plano");
    const extraOpciones = document.getElementById("extraOpciones");
    const btnGenerar = document.getElementById("btnGenerarCodigo");

    // 🔹 Si el campo numero_plano NO está vacío → bloquear extraOpciones
    if (numeroPlano.value.trim() !== "") {
        extraOpciones.disabled = true;
    } else {
        extraOpciones.disabled = false;
    }

    // 🔹 Si hay algo escrito en extraOpciones → deshabilitar botón de generar
    if (extraOpciones.value.trim() !== "") {
        btnGenerar.disabled = true;
        btnGenerar.classList.add("opacity-50", "cursor-not-allowed");
    } else {
        btnGenerar.disabled = false;
        btnGenerar.classList.remove("opacity-50", "cursor-not-allowed");
    }
});
