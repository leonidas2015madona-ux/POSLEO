import json
import os

PRODUCTOS_FILE = "productos.json"

def cargar_productos():
    try:
        with open(PRODUCTOS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Si el archivo no existe o está corrupto, crear uno nuevo
        with open(PRODUCTOS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2, ensure_ascii=False)
        return []

def guardar_productos(productos):
    try:
        with open(PRODUCTOS_FILE, "w", encoding="utf-8") as f:
            json.dump(productos, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error al guardar productos: {e}")
        return False

def actualizar_producto(nombre, nuevos_datos):
    productos = cargar_productos()
    for producto in productos:
        if producto['nombre'] == nombre:
            producto.update(nuevos_datos)
            return guardar_productos(productos)
    return False

def agregar_producto(nuevo_producto):
    productos = cargar_productos()
    productos.append(nuevo_producto)
    return guardar_productos(productos)

def eliminar_producto(nombre):
    productos = cargar_productos()
    productos = [p for p in productos if p['nombre'] != nombre]
    return guardar_productos(productos)

def buscar_productos(termino):
    productos = cargar_productos()
    return [p for p in productos if termino.lower() in p['nombre'].lower()]

def obtener_productos_por_categoria(categoria):
    productos = cargar_productos()
    if categoria == "Todos":
        return productos
    return [p for p in productos if p.get('categoria', 'Otros') == categoria]