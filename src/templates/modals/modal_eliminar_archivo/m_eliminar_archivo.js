// Función para cargar el modal para aviso de si desea eliminar archivo
document.addEventListener("DOMContentLoaded", function () {
    fetch('../../components/modal_eliminar_archivo/m_eliminar_archivo.html')
        .then(response => response.text())
        .then(html => {
            // Insertar el modal en el contenedor
            const container = document.getElementById('modalContainerEliminar');
            if (container) {
                container.innerHTML = html;
            }
        });
});

// Función global para mostrar el modal de eliminación
function mostrarModalEliminar() {
    const modal = document.getElementById('modalEliminarArchivo');
    if (modal) {
        modal.classList.remove('hidden');
    }
}
window.mostrarModalEliminar = mostrarModalEliminar;