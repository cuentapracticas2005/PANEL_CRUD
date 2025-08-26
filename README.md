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
  - CAMBIO: Filtros opcionales por `anio`, `mes`, `descripcion`, `numero_plano`, `tamano`, `version`, `dibujante`, `dibujado_en` usando método GET, con persistencia de valores en el formulario.
  - CAMBIO: En el modal de edición, los `select` ahora conservan el valor actual del registro mediante `selected` condicional en Jinja.

- Estructura de estáticos
  - Logo movido a `src/static/img/HIDROSTAL3.png`.

- Limpieza de archivos
  - Eliminadas plantillas no usadas: `src/templates/modals/*`.
  - Eliminada `src/templates/img/` (tras mover el logo).
  - Eliminada carpeta `src/__pycache__/`.

- Dependencias
  - Añadido `requirements.txt` con Flask y mysql-connector-python.

## Documentación de nuevas funcionalidades

1) Filtros opcionales en la página de inicio
- Backend (`src/app.py` ruta `/`): Se construye la consulta SQL dinámicamente, agregando condiciones solo para los parámetros presentes. Se usa parametrización para evitar inyección SQL. Campos admitidos: `anio` (igual), `mes` (igual), `descripcion` (LIKE), `numero_plano` (LIKE), `tamano` (igual), `version` (LIKE), `dibujante` (LIKE), `dibujado_en` (igual).
- Frontend (`src/templates/index.html`): El formulario usa `method="get"` y los inputs se rellenan con `request.args`. Las listas desplegables muestran opción "Todos" y mantienen selección.

2) Retención de selección en modal de edición
- En `index.html`, los `select` de Año, Mes, Tamaño y Dibujado en utilizan variables temporales (`anio_sel`, `mes_actual`, `tam_actual`, `dib_actual`) para marcar la opción correspondiente con `selected`.

## Requisitos

La base de datos debe incluir las columnas:
`id_plano, anio, mes, descripcion, num_plano, tamanio, version, dibujante, dibujado_en`.

## Ejecución

```bash
pip install -r requirements.txt
python /workspace/src/app.py
```

