// Función para cargar el modal desde m_editar_archivo.html y agregarlo al DOM
document.addEventListener("DOMContentLoaded", function () {
    fetch('../../components/modal_editar_archivo/m_editar_archivo.html')
        .then(response => response.text())
        .then(html => {
            // Insertar el modal en el contenedor
            const container = document.getElementById('modalContainerEditar');
            if (container) {
                container.innerHTML = html;
            }
        });
});

// Función para mostrar el modal (puedes llamarla desde un botón)
function mostrarModalEditar() {
    const modal = document.getElementById('modalEditar');
    if (modal) {
        modal.classList.remove('hidden');
    }
}
