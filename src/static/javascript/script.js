
// FUNCION PARA GENERAR CODIGO MODAL AGREGAR
function generarCodigo() {
    const numeroPlano = document.getElementById("numero_plano");

    // Obtener valores de los selects
    const tipoPlano = document.getElementById("tipo_plano").value.trim();
    const tamano = document.getElementById("tamano").value.trim();
    const revision = document.getElementById("revision").value.trim();
    const sub_revision = document.getElementById("sub_revision").value.trim();

    // Verificar si al menos un select tiene valor (sin contar sub_revision porque es opcional)
    const algunSelectLleno = tipoPlano || tamano || revision;

    // Si hay algún select lleno pero faltan otros requeridos → mostrar alerta
    if (algunSelectLleno && (!tipoPlano || !tamano || !revision)) {
        alert("Por favor selecciona todas las opciones antes de generar el código.");
        return;
    }

    // Si no hay ningún select seleccionado → no hace nada
    if (!algunSelectLleno) {
        return;
    }

    // Construcción del código: TIPO - 300000 - TAMAÑO - REVISION - SUB_REVISION (opcional)
    const codigo = `${tipoPlano}-300000-${tamano}${revision}${sub_revision || ""}`;

    // Insertar en el input de número de plano
    numeroPlano.value = codigo;
}

//FUNCION PARA GENERAR CODIGO MODAL REUTILIZAR
function generarCodigoReutilizar(id_plano) {
    // Buscar el input de número de plano del modal correspondiente
    const numeroPlano = document.querySelector(`#modalReutilizar${id_plano} #numero_plano_reutilizar`);

    // Obtener valores de los selects dentro del modal correspondiente
    const tipoPlano = document.querySelector(`#modalReutilizar${id_plano} #tipo_plano_reutilizar${id_plano}`).value;
    const tamano = document.querySelector(`#modalReutilizar${id_plano} #tamano_reutilizar${id_plano}`).value;
    const revision = document.querySelector(`#modalReutilizar${id_plano} #revision_reutilizar${id_plano}`).value;
    const sub_revision = document.querySelector(`#modalReutilizar${id_plano} #sub_revision_reutilizar${id_plano}`).value;

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
    const numeroPlano = document.querySelector(`#modal${id_plano} #numero_plano_edit`);

    const tipoPlano = document.querySelector(`#modal${id_plano} #tipo_plano_edit${id_plano}`).value;
    const tamano = document.querySelector(`#modal${id_plano} #tamano_edit${id_plano}`).value;
    const revision = document.querySelector(`#modal${id_plano} #revision_edit${id_plano}`).value;
    const sub_revision = document.querySelector(`#modal${id_plano} #sub_revision_edit${id_plano}`).value;

    if (!tipoPlano || !tamano || !revision) {
        alert("Por favor selecciona Tipo, Tamaño y Revisión (la Sub-Revisión es opcional).");
        return;
    }

    const nuevoCodigo = `${tipoPlano}-300000-${tamano}${revision}${sub_revision || ""}`;
    numeroPlano.value = nuevoCodigo;
}


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
