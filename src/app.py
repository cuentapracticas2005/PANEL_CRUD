from flask import Flask, render_template, request, redirect, url_for
import os
import database as db

# Accedemos al archivo index.html para poder lanzarlo a un puerto del servidor
template_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))#Con este comando accedemos al archivo del proyecto
template_dir = os.path.join(template_dir,'src','templates')#Con el join unimos los directorios par aacceder a nuestro index.html

#Inicializamos Flask en la variable app
app = Flask(__name__, template_folder = template_dir)

#Rutas de la app
@app.route('/')
def home():
    # Consulta en la base de datos
    cursor = db.database.cursor() # Usamos la funcion cursor para la conexion a la base de datos
    cursor.execute("SELECT * FROM planos")
    myresult = cursor.fetchall() # fetchall() obtiene todos los registros de la consulta
    # Convertir los datos a diccionario
    insertObject = [] # Declaramos un array vacio para poder almacenar los registros de planos
    columnNames = [column[0] for column in cursor.description] # Obtenemos los nombres de las columnas de la tabla
    for record in myresult:
        insertObject.append(dict(zip(columnNames, record))) # Convertimos cada registro en un diccionario
    cursor.close()
    return render_template('index.html', data=insertObject) # Pasamos el array de diccionarios a la plantilla index.html


# Ruta para guardar usuarios en la db_h
@app.route('/user', methods=['POST'])
def addUser():
    # A traves de request.form obtenemos los datos del formulario
    anio = request.form['anio']
    mes = request.form['mes']
    descripcion = request.form['descripcion']
    numero_plano = request.form['numero_plano']
    tamano = request.form['tamano']
    version = request.form['version']
    dibujante = request.form['dibujante']
    dibujado_en = request.form['dibujado_en']

    # Si tenemos todos los datos hacemos la consulta INSERT en la db_h
    if anio and mes and descripcion and numero_plano and tamano and version and dibujante and dibujado_en:
        cursor = db.database.cursor()
        sql = "INSERT INTO planos (anio, mes, descripcion, num_plano, tamanio, version, dibujante, dibujado_en) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        data = (anio, mes, descripcion, numero_plano, tamano, version, dibujante, dibujado_en)
        cursor.execute(sql, data)
        db.database.commit()
        cursor.close()
    return redirect(url_for('home'))


# Ruta para eliminar documentos de la db_h
@app.route('/delete/<string:id>')
def delete(id):
    cursor = db.database.cursor()
    sql = "DELETE FROM planos WHERE id_plano=%s"
    data = (id,)
    cursor.execute(sql, data)
    db.database.commit()
    cursor.close()
    return redirect(url_for('home'))

# Ruta para actualizar documentos en la db_h
@app.route('/edit/<string:id>', methods=['POST'])
def edit (id):
    anio = request.form['anio']
    mes = request.form['mes']
    descripcion = request.form['descripcion']
    numero_plano = request.form['numero_plano']
    tamano = request.form['tamano']
    version = request.form['version']
    dibujante = request.form['dibujante']
    dibujado_en = request.form['dibujado_en']

    if id and anio and mes and descripcion and numero_plano and tamano and version and dibujante and dibujado_en:
        cursor = db.database.cursor()
        sql = "UPDATE planos SET anio=%s, mes=%s, descripcion=%s, num_plano=%s, tamanio=%s, version=%s, dibujante=%s, dibujado_en=%s WHERE id_plano=%s"
        data = (anio, mes, descripcion, numero_plano, tamano, version, dibujante, dibujado_en, id)
        cursor.execute(sql, data)
        db.database.commit()
        cursor.close()
    return redirect(url_for('home'))

#Lanzamos la app
if __name__ == '__main__':
    app.run(debug=True, port=4000)