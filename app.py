from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit
from crud import cartones_disponibles,cartones_usados,get_data,actualizar_partida,obtener_datos_partida, get_enunciado, get_premio, insertar_comprador, get_estatus, get_precio, vendidos, get_modalidad, get_dolar, get_zelle
import sqlite3
import os
from werkzeug.utils import secure_filename
from functools import wraps
from flask import redirect, url_for, session

# Decorador para proteger las rutas
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):  # Verifica si el usuario está autenticado
            return redirect(url_for('admin_index'))  # Redirige al login si no está autenticado
        return f(*args, **kwargs)
    return decorated_function

app = Flask(__name__)
UPLOAD_FOLDER = 'static/comprobantes'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'supersecretkey' 
socketio = SocketIO(app, manage_session=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=["GET"])
def index():
    return render_template('index.html', enunciado=get_enunciado())


@app.route("/cartones", methods=["GET"])
def imprimir_cartones():


    estatus = get_estatus()
    if estatus == "Venta finalizada":
        return redirect(url_for('index'))  # redirigir a un panel de administración


    cartones_tuplas = cartones_disponibles(read="*")

    cartones = [carton[0] for carton in cartones_tuplas]


    return render_template("seleccion_cartones.html", cartones=cartones, precio = int(get_precio()), modalidad = get_modalidad(), precio_dolares=get_dolar())

@socketio.on('cartones_seleccionados')
def handle_cartones_seleccionados(data):

    global cartones_seleccionados
    global total_price
    global total_price_2
    
    cartones_seleccionados = data.get('cartones', [])  # Recuperar los cartones seleccionados
    total_price = data.get('total', 0)  # Recuperar el precio total en bolívares
    total_price_2 = data.get('total2', 0)  # Recuperar el precio total en dólares
    
    # Almacenar en la sesión para su uso posterior
    session['cartones_user'] = cartones_seleccionados
    session['total_price'] = total_price
    session['total_price_2'] = total_price_2




@app.route("/compra")
def pago():
    return render_template("comprar.html", cartones_seleccionados=', '.join(map(str, cartones_seleccionados)), total_price = total_price, premio=get_premio(), precio = int(get_precio()), enunciado=get_enunciado(), total_price2 = total_price_2, zelle = get_zelle(), precio_dolares=get_dolar())


@app.route("/registrar_compra", methods=["POST", "GET"])
def registrar():
    if request.method == "POST":
        nombre = request.form["nombre"]
        cedula = request.form["cedula"]
        nmr_te = request.form["telefono"]
        nmr_r = request.files["referencia"]
                # Verificar si el archivo es válido

        # Verificar si el archivo es válido
        if nmr_r and allowed_file(nmr_r.filename):
            # Asegurarse de que el nombre del archivo es seguro
            filename = secure_filename(nmr_r.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Guardar el archivo en la carpeta estática
            nmr_r.save(filepath)

            # Obtener la ruta del archivo para guardarla en la base de datos
            referencia_ruta = os.path.join('/static/comprobantes', filename)
            referencia_ruta = referencia_ruta.replace("\\", "/")
            fecha = get_enunciado()
        
        cartones_seleccionados_str = ','.join(map(str, cartones_seleccionados))


        link = f"/descargar_cartones?cartones={cartones_seleccionados_str}"


        insertar_comprador(nombre, cedula, nmr_te, nmr_r.filename, cartones_seleccionados, f"{total_price}bs/{total_price_2}$", fecha, referencia_ruta, link)



        return render_template('confirmacion.html')

@app.route('/descargar_cartones')
def descargar_cartones():
    cartones = request.args.get('cartones', '')
    cartones_lista = cartones.split(',')
    
    # Puedes devolver una vista donde se muestran las imágenes de los cartones
    return render_template('descargar_cartones.html', cartones=cartones_lista)


from flask import session

@app.route("/admin", methods=["GET", "POST"])
def admin_index():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        if username == "admin" and password == "admin123":
            session['logged_in'] = True  # Establece que el usuario está autenticado
            return redirect(url_for('admin_dashboard'))  # redirigir a un panel de administración
        else:
            error_message = "Usuario o contraseña incorrectos"
            return render_template("login.html", error_message=error_message)

    return render_template("login.html")

"""elimine las rutas puente de carton y usuario y usuario requerido a usuario verificado porque NO SE PORQUE NO OBTENGO EL CARTON SI LO ESTA ENVIADNO AL SERVIDOR"""
@app.route("/admin/dashboard")
@login_required  # Ruta protegida por login

def admin_dashboard():
    return render_template("panel_admin.html")


@app.route("/admin/dashboard/partida" , methods = ["POST" , "GET"])
@login_required  # Ruta protegida por login

def admin_dashboard_partida():
    datos = obtener_datos_partida()

    if request.method == "POST":
        action = request.form.get("action")  # "reiniciar" o "detener"
        fecha_enunciado = request.form.get("fechaEnunciado")
        recompensa = request.form.get("recompensa")
        precio_carton = request.form.get("precioCarton")
        tipo_carton = request.form.get("tipoCarton")
        precio_dolares = request.form.get("precioCarton$")
        zelle = request.form.get("zelle")
        actualizar_partida(fecha_enunciado, recompensa, precio_carton, tipo_carton, action, precio_dolares, zelle)
        return redirect(url_for('admin_dashboard_partida'))  # redirigir a un panel de administración
    return render_template("admin_partida.html", datos=datos)



@app.route("/admin/dashboard/solicitudes")
@login_required  # Ruta protegida por login
def admin_dashboard_solicitudes():
    solicitudes = get_data()  # Recupera los datos de la tabla
    return render_template("admin_solicitudes.html", solicitudes=solicitudes) 


"""ELIMINE ESTA SECCION AUNQUE CON EL MISMO PROTOCOLO MUESTRO TODO Y YA , SOLO ESE PROBLEMA DE CARTONES """

@app.route("/admin/dashboard/solicitudes/message/", methods=["POST"])
def message():
    data = request.get_json()
    solicitud_id = data.get("id")

    # Conectar a la base de datos
    conn = sqlite3.connect('bingo.db')
    cursor = conn.cursor()

    # Verificar si la solicitud existe
    cursor.execute("""UPDATE requeridos SET estatus = "enviado" WHERE id = ?""", (solicitud_id,))
    conn.commit()

    # Extraer los cartones vendidos como texto
    cursor.execute("""SELECT cartones_solicitados FROM requeridos WHERE id = ?""", (solicitud_id,))
    cartones_vendidos = cursor.fetchone()[0]  # Obtener el primer resultado
    conn.close()

    # Limpieza y conversión del string a lista de enteros
    if isinstance(cartones_vendidos, str):
        # Eliminar caracteres no deseados y dividir el string
        cartones = [int(carton.strip()) for carton in cartones_vendidos.strip('[]').split(',') if carton.strip().isdigit()]
    else:
        # Si no es un string, manejarlo como un único valor
        cartones = [int(cartones_vendidos)]

    print(cartones)  # Verifica los valores

    # Llamar a la función para insertar los cartones
    vendidos(cartones)

    return redirect(url_for('admin_dashboard_solicitudes'))  # redirigir a un panel de administración



@app.route("/admin/dashboard/vendidos")
@login_required  # Ruta protegida por login
def mostrar_cartones():

    cartones_tuplas = cartones_disponibles(C=True)

    cartones = [carton[0] for carton in cartones_tuplas]

    return render_template("disponibles_no.html", cartones=cartones)



if __name__ == '__main__':
    socketio.run(app, debug=True)
