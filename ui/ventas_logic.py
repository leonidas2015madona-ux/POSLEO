def calcular_total(productos_seleccionados):
    try:
        return sum(p['precio'] * p['cantidad'] for p in productos_seleccionados)
    except (TypeError, KeyError):
        return 0

def calcular_iva(subtotal, porcentaje_iva):
    try:
        return subtotal * (porcentaje_iva / 100)
    except TypeError:
        return 0

def calcular_total_con_iva(subtotal, porcentaje_iva):
    try:
        iva = calcular_iva(subtotal, porcentaje_iva)
        return subtotal + iva
    except TypeError:
        return subtotal

def calcular_vuelto(total, entregado):
    try:
        return max(0, round(entregado - total, 2))
    except TypeError:
        return 0

def aplicar_descuento(total, porcentaje_descuento):
    try:
        return total * (1 - porcentaje_descuento / 100)
    except TypeError:
        return total

def procesar_venta(venta_data):
    """
    Procesa una venta y actualiza el stock de productos
    """
    try:
        # Cargar productos
        from ui.productos_logic import cargar_productos, guardar_productos
        productos = cargar_productos()
        
        # Actualizar stock
        for item in venta_data['productos']:
            for producto in productos:
                if producto['nombre'] == item['nombre']:
                    producto['stock'] -= item['cantidad']
        
        # Guardar productos actualizados
        guardar_productos(productos)
        
        # Guardar venta
        try:
            with open("ventas.json", "r", encoding="utf-8") as f:
                ventas = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            ventas = []
        
        ventas.append(venta_data)
        
        with open("ventas.json", "w", encoding="utf-8") as f:
            json.dump(ventas, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"Error al procesar venta: {e}")
        return False