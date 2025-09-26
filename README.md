## SISTEMA DE GESTION DE PLANOS
Este sistema esta siendo desarrollado con la finalidad de poder administrar los planos de una manera eficaz
y organizada de tal manera que podamos tener un acceso mas rapido a todos ellos, se a implementado las funcionalidades
CRUD y un filtro de busqueda, de esa manera se facilita el poder encontrar los registros/planos que se necesiten.

Tambien tiene una funcionalidad de roles, la cual es util para poder asignar privilegios a determinados usuarios junto 
a ello tambien tiene un panel de administracion de usuarios(unicamente para administradores), el cual va a permitir
funcionalidades CRUD y poder habilitar o deshabilitar usuarios, de esta manera el/los administradores podran tener un
mayor control de los usuarios y una mejor administracion de ellos.

### CARACTERISTICAS:
- CRUD para registros de planos y administracion de usuarios.
- Filtros para registro de planos y administracion de usuarios.
- Habilitar/deshabilitar usuarios(disponible solo para administradores)
- Tres tipos de usuarios, cada uno con privilegios particulares:
    1. Administrador: Control y acceso total.
    2. Dibujante: Todo menos administar usuarios y eliminar registros.
    3. Trabajador: Solo va a poder ver planos.

### PREREQUISITOS:
Tener instalado los modulos necesarios:
- Python v3.13.6
- node.js
- Base de datos MySQL

### INSTALACION:
- Crear entorno virtual:\
```py -m venv nombre_entorno```
- Instalar dependencias:\
```pip install -r requirements.txt```

### USO:
- Archivo principal: run.py

### ESTRUCTURA DEL PROYECTO:
```
proyecto/
|--app/
|    |--admin/
|    |   |--__init__.py
|    |   |--routes.py
|    |
|    |--archivos/
|    |   |--__init__.py
|    |   |--routes.py
|    |   |--utils.py
|    |
|    |--auth/
|    |   |--__init__.py
|    |   |--routes.py
|    |
|    |--main/
|    |   |--__init__.py
|    |   |--routes.py
|    |
|    |--models/
|    |   |--__init__.py
|    |   |--user.py
|    |
|    |--planos/
|    |   |--__init__.py
|    |   |--routes
|    |   |--utils.py
|    |
|    |--SQL/
|    |   |--data.sql
|    |
|    |--static/
|    |   |--img/
|    |   |   |--bombas2.jpg
|    |   |   |--HIDROSTAL3.png
|    |   |   |--icono.png
|    |   |--javascript/
|    |       |--script.js
|    |   
|    |--templates/
|    | |--admin/
|    | |--auth/
|    | |   |--login.html
|    | |--main/
|    | |   |--home.html
|    | |--pages/
|    | |   |--admin_users.html
|    | |--partials/
|    | |   |--modal_agregar.html
|    | |   |--modal_editar_user.html
|    | |   |--modal_editar.html
|    | |   |--modal_eliminar_user.html
|    | |   |--modal_eliminar.html
|    | |   |--modal_registrar_usuario.html
|    | |   |--modal_reutilizar.html
|    | |--base.html
|    | 
|    |--__init__.py
|    |--config.py
|    |--extensions.py
|--.env
|--database.py
|--README.md
|--requirements.txt
|--run.py

```