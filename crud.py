import sqlite3

DB_NAME = "bingo.db"

def execute_query(query, params=(), fetch=False, fetchone=False):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(query, params)
    if fetch:
        data = cursor.fetchall() if not fetchone else cursor.fetchone()
    else:
        conn.commit()
        data = None
    conn.close()
    return data

def obtener_datos_partida():
    # Conectar a la base de datos
    conn = sqlite3.connect('bingo.db')
    cursor = conn.cursor()

    # Crear la consulta para obtener el dato específico
    cursor.execute("SELECT estatus, partida, recompensa, precio_de_carton, precio_dolar, zelle, modalidad_carton_regalo FROM partida WHERE id = 1")
    resultado = cursor.fetchone()
    conn.commit()
    
    if resultado[0] == "Venta finalizada":

        cursor.execute("""DELETE FROM cartones_disponibles WHERE 1 = 1""")
        conn.commit()

        cursor.executemany("""
        INSERT OR IGNORE INTO cartones_disponibles (carton_disponible) VALUES (?);
        """, [(i,) for i in range(1, 1501)])
        conn.commit()



    conn.close()

    return resultado if resultado else None




def actualizar_partida(fecha_enunciado=None, recompensa=None, precio_carton=None, tipo_carton=None, action=None, precio_dolares=None, zelle=None):
    import sqlite3

    # Conectar a la base de datos
    conn = sqlite3.connect('bingo.db')
    cursor = conn.cursor()

    # Verificar si la tabla tiene al menos una fila
    cursor.execute("SELECT COUNT(*) FROM partida;")
    count = cursor.fetchone()[0]

    if count == 0:
        # Insertar una fila inicial con valores por defecto si no hay registros
        cursor.execute("""
            INSERT INTO partida (partida, recompensa, precio_de_carton, modalidad_carton_regalo, estatus) 
            VALUES (?, ?, ?, ?, ?);
        """, ("", "", 0.0, "", "Venta finalizada"))
        conn.commit()

    # Construcción dinámica de los campos y valores para el comando UPDATE
    fields = []
    values = []

    if fecha_enunciado:
        fields.append("partida = ?")
        values.append(fecha_enunciado)

    if recompensa:
        fields.append("recompensa = ?")
        values.append(recompensa)

    if precio_carton:  # precio_carton puede ser 0, por eso se usa `is not None`
        fields.append("precio_de_carton = ?")
        values.append(precio_carton)

    if precio_dolares:  # precio_carton puede ser 0, por eso se usa `is not None`
        fields.append("precio_dolar = ?")
        values.append(precio_dolares)

    if zelle:  # precio_carton puede ser 0, por eso se usa `is not None`
        fields.append("zelle = ?")
        values.append(zelle)

    if tipo_carton:
        fields.append("modalidad_carton_regalo = ?")
        values.append(tipo_carton)

    if action:
        fields.append("estatus = ?")
        values.append(action)

    # Actualizar la fila solo si hay campos a modificar
    if fields:
        update_query = f"UPDATE partida SET {', '.join(fields)} WHERE id = 1;"
        cursor.execute(update_query, values)

    # Confirmar los cambios y cerrar conexión
    conn.commit()
    conn.close()




def partida(C=None, read=None, U=None, D=None):
    if C:
        query = """
        INSERT OR REPLACE INTO partida (id, partida, hora_de_partida, precio_de_carton, estatus, mensaje)
        VALUES (1, ?, ?, ?, ?, ?);
        """
        execute_query(query, C)
    elif read:
        query = "SELECT * FROM partida WHERE id = 1;"
        return execute_query(query, fetch=True)
    elif U:
        query = """
        UPDATE partida
        SET partida = ?, hora_de_partida = ?, precio_de_carton = ?, estatus = ?, mensaje = ?
        WHERE id = 1;
        """
        execute_query(query, U)
    elif D:
        query = "DELETE FROM partida WHERE id = 1;"
        execute_query(query)

def cartones_disponibles(C=None, read=None, U=None, D=None):
    if C:
        query = "SELECT carton FROM cartones_usados;"
        return execute_query(query, fetch=True)
    elif read:
        if read == "*":  # Si `read` es "*", obten todos los registros
            query = "SELECT carton_disponible FROM cartones_disponibles;"
            return execute_query(query, fetch=True)
        else:
            query = "SELECT * FROM cartones_disponibles WHERE carton_disponible = ?;"
            return execute_query(query, (read,), fetch=True)



def cartones_usados(C=None, read=None, U=None, D=None):
    if C:
        query = "INSERT INTO cartones_usados (carton, usuario) VALUES (?, ?);"
        execute_query(query, C)
    elif read:
        query = "SELECT * FROM cartones_usados WHERE carton = ?;"
        return execute_query(query, (read,), fetch=True)
    elif U:
        query = """
        UPDATE cartones_usados
        SET usuario = ?
        WHERE carton = ?;
        """
        execute_query(query, U)
    elif D:
        query = "DELETE FROM cartones_usados WHERE carton = ?;"
        execute_query(query, (D,))

def requeridos(C=None, read=None, U=None, D=None, table="requeridos"):
    if C:
        query = f"""
        INSERT INTO {table} 
        (nombre_apellidos, cedula, telefono, referencia, cartones_solicitados, monto, fecha)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        execute_query(query, C)
    elif read:
        query = f"SELECT * FROM {table} WHERE cedula = ?;"
        return execute_query(query, (read,), fetch=True)
    elif U:
        query = f"""
        UPDATE {table}
        SET nombre_apellidos = ?, telefono = ?, referencia = ?,
            cartones_solicitados = ?, monto = ?, fecha = ?
        WHERE cedula = ?;
        """
        execute_query(query, U)
    elif D:
        query = f"DELETE FROM {table} WHERE cedula = ?;"
        execute_query(query, (D,))

def usuarios_aceptados(C=None, read=None, U=None, D=None):
    requeridos(C, read, U, D, table="usuarios_aceptados")

# Función para la tabla "cartones_usados"
def cartones_usados(C=None, read=None, U=None, D=None):
    if C:  # Insertar un nuevo cartón
        query = "INSERT OR IGNORE INTO cartones_usados (carton, usuario) VALUES (?, ?);"
        execute_query(query, C)
    elif read:  # Leer registros
        if read == "*":  # Leer todos los registros
            query = "SELECT carton FROM cartones_usados;"
            return execute_query(query, fetch=True)
        else:  # Leer un registro específico
            query = "SELECT * FROM cartones_usados WHERE carton = ?;"
            return execute_query(query, (read,), fetch=True)
    elif U:  # Actualizar un registro
        query = """
        UPDATE cartones_usados
        SET usuario = ?
        WHERE carton = ?;
        """
        execute_query(query, U)
    elif D:  # Eliminar un registro
        query = "DELETE FROM cartones_usados WHERE carton = ?;"
        execute_query(query, (D,))
        
        
        
        
def get_data():
    conn = sqlite3.connect('bingo.db')
    cursor = conn.cursor()

    # Consulta todos los datos de la tabla
    cursor.execute("SELECT * FROM requeridos")
    rows = cursor.fetchall()
    conn.close()

    # Convertir los resultados en una lista de diccionarios
    solicitudes = []
    for row in rows:
        solicitud = {
            "id": row[0],
            "nombre": row[1],
            "cedula": row[2],
            "telefono": row[3],
            "referencia": row[4],
            "cartones": row[5],
            "monto": row[6],
            "fecha": row[7],
            "estatus": row[8],
            "link": row[9]
        }
        solicitudes.append(solicitud)

    return solicitudes


def get_enunciado():
    conn = sqlite3.connect('bingo.db')
    cursor = conn.cursor()

    cursor.execute("SELECT estatus FROM partida WHERE id = 1")
    estatus = cursor.fetchone()[0]
    conn.commit()

    if estatus == "Venta en curso":

        cursor.execute("SELECT partida FROM partida")
        data = cursor.fetchone()  # Recupera todos los datos de la tabla
        conn.close()
    
    else:

        data = ["No hay cartones disponibles"]

    return data[0] if data else None

def get_premio():
    conn = sqlite3.connect('bingo.db')
    cursor = conn.cursor()
    cursor.execute("SELECT recompensa FROM partida")
    data = cursor.fetchone()  # Recupera todos los datos de la tabla
    conn.close()
    return data[0] if data else None

def get_precio():
    conn = sqlite3.connect('bingo.db')
    cursor = conn.cursor()
    cursor.execute("SELECT precio_de_carton FROM partida")
    data = cursor.fetchone()  # Recupera todos los datos de la tabla
    conn.close()
    return data[0] if data else None


def insertar_comprador(nombre_apellido, cedula, telefono, referencia, cartones_solicitados, monto, fecha, referencia_ruta, link):
    # Conectar a la base de datos
    conn = sqlite3.connect('bingo.db')
    cursor = conn.cursor()

    # Ejecutar el comando
    cursor.execute("""
        INSERT INTO requeridos (
            nombre_apellidos, 
            cedula, 
            telefono, 
            referencia, 
            cartones_solicitados, 
            monto, 
            fecha,
            link
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, (nombre_apellido, cedula, telefono, referencia_ruta, str(cartones_solicitados), monto, fecha, link))
    conn.commit()



    placeholders = ', '.join('?' for _ in cartones_solicitados)

    # Ejecutar el comando
    cursor.execute(f"DELETE FROM cartones_disponibles WHERE carton_disponible IN ({placeholders});", cartones_solicitados)


    conn.commit()
    # Confirmar cambios y cerrar conexión
    conn.close()

def get_estatus():
    conn = sqlite3.connect('bingo.db')
    cursor = conn.cursor()
    cursor.execute("SELECT estatus FROM partida WHERE id = 1")
    estatus = cursor.fetchone()[0]
    conn.close()
    return estatus if estatus else None

def get_modalidad():
    conn = sqlite3.connect('bingo.db')
    cursor = conn.cursor()
    cursor.execute("SELECT modalidad_carton_regalo FROM partida WHERE id = 1")
    modalidad = cursor.fetchone()[0]
    conn.close()
    return modalidad if modalidad else None

def vendidos(cartones):
    # Conectar a la base de datos
    conn = sqlite3.connect('bingo.db')
    cursor = conn.cursor()

    # Convertir los valores del array en tuplas (executemany espera una lista de tuplas)
    cartones_tuplas = [(carton,) for carton in cartones]

    try:
        # Ejecutar el comando para insertar múltiples valores
        cursor.executemany("""
            INSERT INTO cartones_usados (carton) VALUES (?);
        """, cartones_tuplas)

        # Confirmar cambios
        conn.commit()
        print(f"Cartones insertados: {cartones}")
    except sqlite3.IntegrityError as e:
        print(f"Error al insertar cartones: {e}")
    finally:
        # Cerrar la conexión
        conn.close()

def get_dolar():
    conn = sqlite3.connect('bingo.db')
    cursor = conn.cursor()
    cursor.execute("SELECT precio_dolar FROM partida WHERE id = 1")
    dolar = cursor.fetchone()[0]
    conn.close()
    return dolar if dolar else None

def get_zelle():
    conn = sqlite3.connect('bingo.db')
    cursor = conn.cursor()
    cursor.execute("SELECT zelle FROM partida WHERE id = 1")
    zelle = cursor.fetchone()[0]
    conn.close()
    return zelle if zelle else None