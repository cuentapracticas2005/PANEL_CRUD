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

// FUNCION PARA SALIR DE MODALS CON TECLA DE ESCAPE
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

// FUNCION PARA VERIFICAR QUE EL IDENTIFICADOR DEL PLANO NO SEA IGUAL QUE UNO QUE ESTA EN LA BASE DE DATOS
function validarReutilizacion(id_registro, tamanioOriginal, revisionOriginal, subRevisionOriginal) {
    const tamano = document.getElementById(`tamano_reutilizar${id_registro}`).value;
    const revision = document.getElementById(`revision_reutilizar${id_registro}`).value;
    const subRevision = document.getElementById(`sub_revision_reutilizar${id_registro}`).value;

    if (tamano === tamanioOriginal && revision === revisionOriginal && subRevision === subRevisionOriginal) {
        alert("ESO NO SE HACE : \nEL IDENTIFICADOR DE PLANO DEBE SER DIFERENTE \nCAMBIA LA MENOS TAMAÑO, REVISION O SUB-REVISION.");
        return false;
    }
    return true;
}

// FUNCION PARA VERIFICAR QUE EL IDENTIFICADOR DEL PLANO NO SEA IGUAL QUE UNO QUE ESTA EN LA BASE DE DATOS A EXCEPCION DE EL MISMO
function validarIdentificadorEdit(codTipo, numPlano, tamanio, revision, subRevision, idActual) {
    let identificador = `${codTipo}-${numPlano}-${tamanio}${revision}`;
    if (subRevision && subRevision !== "0" && subRevision.trim() !== "") {
        identificador += subRevision;
    }

    const idNum = parseInt(idActual, 10);

    const existeDuplicado = identificadoresExistentes.some(item =>
        item.identificador === identificador && Number(item.id) !== idNum
    );

    if (existeDuplicado) {
        alert(`El identificador ${identificador} ya existe en otro registro.`);
        return false;
    }
    return true;
}


