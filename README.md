# Documentación de cambios

Este documento describe los cambios realizados para limpiar y corregir el proyecto.

## Cambios principales

- src/app.py
  - Simplificación de `template_dir` y configuración de `static_folder`.
  - Validaciones corregidas usando `all([...])` en creación y edición.
  - Cierre explícito de cursores en delete/update.
  - `app.run(host='0.0.0.0', ...)` para permitir acceso externo.

- src/templates/index.html
  - Rutas con `url_for` para inicio y estáticos.
  - Corrección de IDs: uso de `d.id_plano` en modales y enlaces.
  - Corrección de `tamanio` en selección de tamaño.
  - Eliminación de enlaces a HTMLs inexistentes y recursos externos para cerrar modales.

- Estructura de estáticos
  - Logo movido a `src/static/img/HIDROSTAL3.png`.

- Limpieza de archivos
  - Eliminadas plantillas no usadas: `src/templates/modals/*`.
  - Eliminada `src/templates/img/` (tras mover el logo).
  - Eliminada carpeta `src/__pycache__/`.

- Dependencias
  - Añadido `requirements.txt` con Flask y mysql-connector-python.

## Requisitos

La base de datos debe incluir las columnas:
`id_plano, anio, mes, descripcion, num_plano, tamanio, version, dibujante, dibujado_en`.

## Ejecución

```bash
pip install -r requirements.txt
python /workspace/src/app.py
```

