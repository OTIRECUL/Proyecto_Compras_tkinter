"""
Sistema de Compras con Presupuesto - versión corta (tkinter + SQLite)

Mismo estilo del ejemplo de clase: menú lateral, una función por acción
y un diccionario de páginas que se muestran u ocultan con mostrar_pagina().
"""

import math
import sqlite3
import tkinter
from tkinter import messagebox

# ---------------------------------------------------------------
# BASE DE DATOS
# ---------------------------------------------------------------
conexion = sqlite3.connect("compras.db")
conexion.execute(
    "CREATE TABLE IF NOT EXISTS compras ("
    "id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT NOT NULL, presupuesto REAL NOT NULL)"
)
conexion.execute(
    "CREATE TABLE IF NOT EXISTS productos ("
    "id INTEGER PRIMARY KEY AUTOINCREMENT, compra_id INTEGER NOT NULL, nombre TEXT NOT NULL, "
    "precio REAL NOT NULL, cantidad INTEGER NOT NULL, FOREIGN KEY (compra_id) REFERENCES compras (id))"
)
conexion.commit()


def buscar_compra(compra_id):
    """Devuelve (cliente, presupuesto); lanza ValueError si la compra no existe."""
    cursor = conexion.execute("SELECT cliente, presupuesto FROM compras WHERE id = ?", (compra_id,))
    compra = cursor.fetchone()
    if compra is None:
        raise ValueError("No existe una compra con ese número.")
    return compra


def total_gastado(compra_id):
    """Suma el costo de todos los productos de una compra."""
    cursor = conexion.execute(
        "SELECT COALESCE(SUM(precio * cantidad), 0) FROM productos WHERE compra_id = ?", (compra_id,)
    )
    return cursor.fetchone()[0]


# ---------------------------------------------------------------
# CÁLCULOS Y VALIDACIONES
# ---------------------------------------------------------------
def dinero(monto):
    """Devuelve un monto con formato RD$1,234.56."""
    return f"RD${monto:,.2f}"


def calcular_descuento(subtotal):
    """Devuelve el porcentaje de descuento que corresponde al subtotal."""
    if subtotal >= 10000:
        return 10
    elif subtotal >= 5000:
        return 5
    else:
        return 0


def leer_texto(caja, nombre):
    """Lee una caja de texto; lanza ValueError si está vacía."""
    texto = caja.get().strip().title()
    if texto == "":
        raise ValueError(nombre + " no puede estar vacío.")
    return texto


def leer_numero(caja, convertir, nombre):
    """Lee una caja y la convierte a int o float; debe ser mayor que 0."""
    try:
        numero = convertir(caja.get().strip())
    except ValueError:
        raise ValueError(nombre + " debe ser un número válido.")
    if not math.isfinite(numero) or numero <= 0:
        raise ValueError(nombre + " debe ser mayor que 0.")
    return numero


def limpiar(*cajas):
    """Borra el contenido de las cajas indicadas."""
    for caja in cajas:
        caja.delete(0, "end")


def escribir(area, contenido):
    """Reemplaza el texto de un área de solo lectura."""
    area.config(state="normal")
    area.delete("1.0", "end")
    area.insert("1.0", contenido)
    area.config(state="disabled")


def ejecutar(accion):
    """Ejecuta una acción; si falla, muestra el error sin cerrar el programa."""
    try:
        accion()
    except (ValueError, sqlite3.Error) as error:
        messagebox.showerror("Error", str(error))


# ---------------------------------------------------------------
# ACCIONES DEL MENÚ
# ---------------------------------------------------------------
def registrar_compra():
    cliente = leer_texto(caja_cliente, "El nombre del cliente")
    presupuesto = leer_numero(caja_presupuesto, float, "El presupuesto")
    with conexion:
        cursor = conexion.execute(
            "INSERT INTO compras (cliente, presupuesto) VALUES (?, ?)", (cliente, presupuesto)
        )
    limpiar(caja_cliente, caja_presupuesto)
    messagebox.showinfo("Listo", "Compra registrada con el número " + str(cursor.lastrowid))


def agregar_producto():
    compra_id = leer_numero(caja_compra, int, "El número de la compra")
    compra = buscar_compra(compra_id)
    nombre = leer_texto(caja_nombre, "El nombre del producto")
    precio = leer_numero(caja_precio, float, "El precio")
    cantidad = leer_numero(caja_cantidad, int, "La cantidad")
    nuevo_total = total_gastado(compra_id) + precio * cantidad
    if nuevo_total > compra[1]:
        aviso = f"Supera el presupuesto por {dinero(nuevo_total - compra[1])}. ¿Agregarlo de todas formas?"
        if not messagebox.askyesno("Presupuesto superado", aviso):
            return
    with conexion:
        conexion.execute(
            "INSERT INTO productos (compra_id, nombre, precio, cantidad) VALUES (?, ?, ?, ?)",
            (compra_id, nombre, precio, cantidad),
        )
    limpiar(caja_nombre, caja_precio, caja_cantidad)
    messagebox.showinfo("Listo", f"Producto agregado: {nombre} ({dinero(precio * cantidad)})")


def ver_factura():
    compra_id = leer_numero(caja_factura, int, "El número de la compra")
    compra = buscar_compra(compra_id)
    cursor = conexion.execute(
        "SELECT nombre, precio, cantidad FROM productos WHERE compra_id = ?", (compra_id,)
    )
    productos = cursor.fetchall()
    if len(productos) == 0:
        messagebox.showinfo("Factura", "Esta compra todavía no tiene productos.")
        return
    subtotal = 0
    unidades = 0
    lineas = [f"===== FACTURA DE LA COMPRA {compra_id} =====", "Cliente: " + compra[0]]
    for nombre, precio, cantidad in productos:
        subtotal += precio * cantidad
        unidades += cantidad
        lineas.append(f"{nombre} - {cantidad} x {dinero(precio)} = {dinero(precio * cantidad)}")
    porcentaje = calcular_descuento(subtotal)
    descuento = subtotal * porcentaje / 100
    diferencia = compra[1] - (subtotal - descuento)
    mas_caro = max(productos, key=lambda producto: producto[1])
    lineas.append(f"\nTotal de unidades: {unidades}")
    lineas.append(f"Producto de mayor precio: {mas_caro[0]} ({dinero(mas_caro[1])})")
    lineas.append(f"Subtotal: {dinero(subtotal)}")
    lineas.append(f"Descuento ({porcentaje}%): {dinero(descuento)}")
    lineas.append(f"Total a pagar: {dinero(subtotal - descuento)}")
    lineas.append(f"Presupuesto: {dinero(compra[1])}")
    lineas.append(
        "Presupuesto suficiente. Sobra " + dinero(diferencia)
        if diferencia >= 0
        else "Presupuesto insuficiente. Faltan " + dinero(-diferencia)
    )
    escribir(area_factura, "\n".join(lineas))


def listar_compras():
    filas = conexion.execute("SELECT id, cliente, presupuesto FROM compras ORDER BY id").fetchall()
    if len(filas) == 0:
        escribir(area_lista, "No hay compras registradas.")
        return
    lineas = []
    for fila in filas:
        lineas.append(f"Compra {fila[0]} | Cliente: {fila[1]} | Presupuesto: {dinero(fila[2])}")
    escribir(area_lista, "\n".join(lineas))


def eliminar_compra():
    compra_id = leer_numero(caja_eliminar, int, "El número de la compra")
    compra = buscar_compra(compra_id)
    if messagebox.askyesno("Confirmar", "¿Eliminar la compra de " + compra[0] + "?"):
        with conexion:
            conexion.execute("DELETE FROM productos WHERE compra_id = ?", (compra_id,))
            conexion.execute("DELETE FROM compras WHERE id = ?", (compra_id,))
        limpiar(caja_eliminar)
        messagebox.showinfo("Listo", "Compra eliminada correctamente.")


# ---------------------------------------------------------------
# VENTANA, MENÚ LATERAL Y PÁGINAS
# ---------------------------------------------------------------
ventana = tkinter.Tk()
ventana.title("Sistema de Compras con Presupuesto")
ventana.geometry("800x500")

sidebar = tkinter.Frame(ventana, bg="#2c3e50", width=180)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

contenido = tkinter.Frame(ventana, bg="white")
contenido.pack(side="right", fill="both", expand=True)

paginas = {}


def mostrar_pagina(nombre):
    """Oculta todas las páginas y muestra la elegida."""
    for pagina in paginas.values():
        pagina.pack_forget()
    paginas[nombre].pack(fill="both", expand=True)
    if nombre == "Listar compras":
        ejecutar(listar_compras)


def crear_pagina(nombre):
    """Crea una página con su título y la guarda en el diccionario."""
    pagina = tkinter.Frame(contenido, bg="white")
    tkinter.Label(pagina, text=nombre, font=("Arial", 20), bg="white").pack(pady=10)
    paginas[nombre] = pagina
    return pagina


def crear_campo(pagina, texto):
    """Agrega una etiqueta con su caja de texto y devuelve la caja."""
    tkinter.Label(pagina, text=texto, bg="white").pack()
    caja = tkinter.Entry(pagina, width=30)
    caja.pack(pady=3)
    return caja


def crear_boton(pagina, texto, accion):
    """Agrega un botón que ejecuta la acción protegida contra errores."""
    tkinter.Button(pagina, text=texto, command=lambda: ejecutar(accion)).pack(pady=8)


def crear_area(pagina):
    """Agrega un área de texto de solo lectura y la devuelve."""
    area = tkinter.Text(pagina, width=65, height=14, state="disabled")
    area.pack(padx=10, pady=5)
    return area


pagina = crear_pagina("Nueva compra")
caja_cliente = crear_campo(pagina, "Nombre del cliente")
caja_presupuesto = crear_campo(pagina, "Presupuesto disponible (RD$)")
crear_boton(pagina, "Registrar compra", registrar_compra)

pagina = crear_pagina("Agregar producto")
caja_compra = crear_campo(pagina, "Número de la compra")
caja_nombre = crear_campo(pagina, "Nombre del producto")
caja_precio = crear_campo(pagina, "Precio unitario (RD$)")
caja_cantidad = crear_campo(pagina, "Cantidad")
crear_boton(pagina, "Agregar producto", agregar_producto)

pagina = crear_pagina("Ver factura")
caja_factura = crear_campo(pagina, "Número de la compra")
crear_boton(pagina, "Mostrar factura", ver_factura)
area_factura = crear_area(pagina)

pagina = crear_pagina("Listar compras")
area_lista = crear_area(pagina)

pagina = crear_pagina("Eliminar compra")
caja_eliminar = crear_campo(pagina, "Número de la compra")
crear_boton(pagina, "Eliminar compra", eliminar_compra)

tkinter.Label(sidebar, text="MENÚ PRINCIPAL", bg="#2c3e50", fg="white").pack(pady=20)
for nombre_pagina in paginas:
    tkinter.Button(
        sidebar, text=nombre_pagina, command=lambda destino=nombre_pagina: mostrar_pagina(destino)
    ).pack(fill="x", padx=10, pady=5)
tkinter.Button(sidebar, text="Salir", command=ventana.destroy).pack(fill="x", padx=10, pady=25)

mostrar_pagina("Nueva compra")
ventana.mainloop()
conexion.close()
