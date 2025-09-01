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
    const revision = document.getElementById("revision").value;
    const sub_revision = document.getElementById("sub_revision").value;

    // 🔹 Verificar si al menos uno de los selects tiene un valor
    const algunSelectLleno = tipoPlano || tamano || revision || sub_revision;

    // 🔹 Si hay algún select lleno pero faltan otros → mostrar alerta
    if (algunSelectLleno && (!tipoPlano || !tamano || !revision || !sub_revision)) {
        alert("Por favor selecciona todas las opciones antes de generar el código.");
        return;
    }

    // 🔹 Si no hay ningún select seleccionado, simplemente no hace nada
    if (!algunSelectLleno) {
        return;
    }

    // Construcción del código con la lógica solicitada
    // Formato: TIPO - 300000 - TAMAÑO - REVISION - SUB_REVISION
    const codigo = `${tipoPlano}-300000-${tamano}${revision}${sub_revision}`;

    // Insertar en el input de número de plano
    numeroPlano.value = codigo;

    // Al generar un código, bloqueamos el input extraOpciones
    extraOpciones.disabled = true;
}


function generarCodigoReutilizar(id_plano) {
    // Buscar el input de número de plano del modal correspondiente
    const numeroPlano = document.querySelector(`#modalReutilizar${id_plano} #numero_plano`);

    // Obtener valores de los selects dentro del modal correspondiente
    const tamano = document.querySelector(`#modalReutilizar${id_plano} #tamano`).value;
    const revision = document.querySelector(`#modalReutilizar${id_plano} #revision`).value;
    const sub_revision = document.querySelector(`#modalReutilizar${id_plano} #sub_revision`).value;

    // Verificar si se llenaron todos los selects
    if (!tamano || !revision || !sub_revision) {
        alert("Por favor selecciona todas las opciones (Tamaño, Revisión y Sub-Revisión).");
        return;
    }

    // Dividir el código actual en partes usando el separador "-"
    let partes = numeroPlano.value.split("-");

    // Si el código no tiene el formato esperado, no lo modificamos
    if (partes.length < 3) {
        alert("El número de plano no tiene un formato válido.");
        return;
    }

    // Reemplazar SOLO la última parte con los nuevos valores
    partes[2] = `${tamano}${revision}${sub_revision}`;

    // Reconstruir el código
    const nuevoCodigo = partes.join("-");

    // Insertar en el input
    numeroPlano.value = nuevoCodigo;
}


// FUNCION PARA GENERAR CODIGO MODAL EDITAR
function generarCodigoEditar(id_plano) {
    // Input de número de plano dentro del modal correspondiente
    const numeroPlano = document.querySelector(`#modal${id_plano} input[name="numero_plano"]`);

    // Valores de los selects dentro del modal correspondiente
    const tipoPlano = document.querySelector(`#modal${id_plano} #tipo_plano`).value;
    const tamano = document.querySelector(`#modal${id_plano} select[name="tamano"]`).value;
    const revision = document.querySelector(`#modal${id_plano} #revision`).value;
    const sub_revision = document.querySelector(`#modal${id_plano} #sub_revision`).value;

    // Validar que todos los campos estén completos
    if (!tipoPlano || !tamano || !revision || !sub_revision) {
        alert("Por favor selecciona todas las opciones (Tipo, Tamaño, Revisión y Sub-Revisión).");
        return;
    }

    // Construir el nuevo código (se mantiene fijo el 300000 en medio)
    const nuevoCodigo = `${tipoPlano}-300000-${tamano}${revision}${sub_revision}`;

    // Insertar el nuevo código en el input
    numeroPlano.value = nuevoCodigo;
}


// LOGICA DE VALIDACION PARA DESHABILITAR Y HABILITAR INPUTS
document.addEventListener("input", () => {
    const extraOpciones = document.getElementById("extraOpciones");
    const selects = document.querySelectorAll("#tipo_plano, #tamano, #revision, #sub_revision");

    // Si el usuario escribe en extraOpciones → bloquear selects
    if (extraOpciones.value.trim() !== "") {
        selects.forEach(sel => sel.disabled = true);
        extraOpciones.disabled = false; // nunca se bloquea al escribir
    } else {
        // Si el input está vacío, se revisan los selects
        let algunSelectLleno = Array.from(selects).some(sel => sel.value.trim() !== "" && sel.value !== " ");
        if (algunSelectLleno) {
            extraOpciones.disabled = true;
        } else {
            // Si no hay nada ni en el input ni en los selects → todos habilitados
            selects.forEach(sel => sel.disabled = false);
            extraOpciones.disabled = false;
        }
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

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
        const modales = document.querySelectorAll(".modal");
        modales.forEach(modal => {
            if (!modal.classList.contains("hidden")) {
                modal.classList.add("hidden");
            }
        });
    }
});
