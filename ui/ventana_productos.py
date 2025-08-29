import customtkinter as ctk
from tkinter import ttk, messagebox
import json
import os
from assets.styles import *

PRODUCTOS_FILE = "productos.json"

def abrir_gestion_productos(parent):
    try:
        win = ctk.CTkToplevel(parent)
        win.title("📦 Gestión de Productos")
        win.geometry("1100x750")
        win.grab_set()
        win.protocol("WM_DELETE_WINDOW", win.destroy)
        
        # Cargar productos
        productos = cargar_productos()
        
        # Frame principal
        main_frame = ctk.CTkFrame(win)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        ctk.CTkLabel(main_frame, text="📦 Gestión de Productos", font=TITLE_FONT).pack(pady=10)
        
        # Frame de búsqueda y filtros
        search_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        search_frame.pack(fill="x", pady=10)
        
        search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(search_frame, textvariable=search_var, 
                                   placeholder_text="🔍 Buscar producto...", 
                                   height=INPUT_HEIGHT, font=TEXT_FONT)
        search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        categorias = ["Todos", "Libros", "Papelería", "Material Oficina", "Electrónica", "Otros"]
        categoria_var = ctk.StringVar(value="Todos")
        
        # Opción de categoría
        categoria_menu = ctk.CTkOptionMenu(search_frame, variable=categoria_var, values=categorias,
                                          height=INPUT_HEIGHT, font=TEXT_FONT)
        categoria_menu.pack(side="right")
        
        # Tabla de productos
        table_frame = ctk.CTkFrame(main_frame)
        table_frame.pack(fill="both", expand=True, pady=10)
        
        # Crear treeview con scrollbar
        style = ttk.Style()
        style.configure("Custom.Treeview", rowheight=TABLE_ROW_HEIGHT, font=("Roboto", 10))
        style.configure("Custom.Treeview.Heading", font=("Roboto", 11, "bold"))
        
        columns = ("nombre", "precio", "stock", "categoria")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", 
                           style="Custom.Treeview", height=15)
        
        # Configurar columnas
        tree.heading("nombre", text="Nombre")
        tree.heading("precio", text="Precio")
        tree.heading("stock", text="Stock")
        tree.heading("categoria", text="Categoría")
        
        tree.column("nombre", width=300, anchor="w")
        tree.column("precio", width=100, anchor="e")
        tree.column("stock", width=80, anchor="center")
        tree.column("categoria", width=150, anchor="w")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Formulario de producto
        form_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        form_frame.pack(fill="x", pady=10)
        
        nombre_var = ctk.StringVar()
        precio_var = ctk.StringVar()
        stock_var = ctk.StringVar()
        categoria_form_var = ctk.StringVar(value="Libros")
        
        # Campos del formulario
        ctk.CTkLabel(form_frame, text="Nombre:", font=TEXT_FONT).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ctk.CTkEntry(form_frame, textvariable=nombre_var, width=250, 
                    height=INPUT_HEIGHT, font=TEXT_FONT).grid(row=0, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(form_frame, text="Precio:", font=TEXT_FONT).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        ctk.CTkEntry(form_frame, textvariable=precio_var, width=100, 
                    height=INPUT_HEIGHT, font=TEXT_FONT).grid(row=0, column=3, padx=5, pady=5)
        
        ctk.CTkLabel(form_frame, text="Stock:", font=TEXT_FONT).grid(row=0, column=4, padx=5, pady=5, sticky="w")
        ctk.CTkEntry(form_frame, textvariable=stock_var, width=80, 
                    height=INPUT_HEIGHT, font=TEXT_FONT).grid(row=0, column=5, padx=5, pady=5)
        
        ctk.CTkLabel(form_frame, text="Categoría:", font=TEXT_FONT).grid(row=0, column=6, padx=5, pady=5, sticky="w")
        categoria_form_menu = ctk.CTkOptionMenu(form_frame, variable=categoria_form_var, 
                                               values=categorias[1:], height=INPUT_HEIGHT, font=TEXT_FONT)
        categoria_form_menu.grid(row=0, column=7, padx=5, pady=5)
        
        # Botones de acción
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=10)
        
        def actualizar_tabla():
            tree.delete(*tree.get_children())
            
            filtro = search_var.get().lower()
            categoria = categoria_var.get()
            
            for producto in productos:
                # Aplicar filtros
                if filtro and filtro not in producto['nombre'].lower():
                    continue
                
                if categoria != "Todos" and producto.get('categoria', 'Otros') != categoria:
                    continue
                
                # Agregar a la tabla
                tree.insert("", "end", values=(
                    producto['nombre'],
                    f"${producto['precio']:.2f}",
                    producto['stock'],
                    producto.get('categoria', 'Otros')
                ))
        
        def guardar_producto():
            nombre = nombre_var.get().strip()
            try:
                precio = float(precio_var.get())
                stock = int(stock_var.get())
            except ValueError:
                messagebox.showerror("Error", "Precio y stock deben ser números válidos")
                return
            
            if not nombre:
                messagebox.showerror("Error", "El nombre no puede estar vacío")
                return
            
            categoria = categoria_form_var.get()
            
            # Verificar si ya existe
            for producto in productos:
                if producto['nombre'].lower() == nombre.lower():
                    if messagebox.askyesno("Confirmar", f"El producto {nombre} ya existe. ¿Desea actualizarlo?"):
                        producto['precio'] = precio
                        producto['stock'] = stock
                        producto['categoria'] = categoria
                        break
                    else:
                        return
            else:
                # Producto nuevo
                productos.append({
                    'nombre': nombre,
                    'precio': precio,
                    'stock': stock,
                    'categoria': categoria
                })
            
            if guardar_productos(productos):
                actualizar_tabla()
                limpiar_formulario()
                messagebox.showinfo("Éxito", "Producto guardado correctamente")
            else:
                messagebox.showerror("Error", "No se pudo guardar el producto")
        
        def eliminar_producto():
            seleccion = tree.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Seleccione un producto para eliminar")
                return
            
            producto = tree.item(seleccion[0], "values")
            nombre = producto[0]
            
            if messagebox.askyesno("Confirmar", f"¿Está seguro de que desea eliminar {nombre}?"):
                productos[:] = [p for p in productos if p['nombre'] != nombre]
                
                if guardar_productos(productos):
                    actualizar_tabla()
                    messagebox.showinfo("Éxito", "Producto eliminado correctamente")
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el producto")
        
        def cargar_producto_seleccionado(event):
            seleccion = tree.selection()
            if not seleccion:
                return
            
            producto = tree.item(seleccion[0], "values")
            nombre_var.set(producto[0])
            precio_var.set(producto[1].replace('$', ''))
            stock_var.set(producto[2])
            categoria_form_var.set(producto[3])
        
        def limpiar_formulario():
            nombre_var.set("")
            precio_var.set("")
            stock_var.set("")
            categoria_form_var.set("Libros")
            tree.selection_remove(tree.selection())
        
        # Botones con iconos y estilos
        ctk.CTkButton(buttons_frame, text="💾 Guardar", command=guardar_producto,
                     **PRIMARY_BUTTON_STYLE).pack(side="left", padx=5)
        ctk.CTkButton(buttons_frame, text="🗑️ Eliminar", command=eliminar_producto,
                     **ACCENT_BUTTON_STYLE).pack(side="left", padx=5)
        ctk.CTkButton(buttons_frame, text="🧹 Limpiar", command=limpiar_formulario,
                     **BUTTON_STYLE).pack(side="left", padx=5)
        ctk.CTkButton(buttons_frame, text="❌ Cerrar", command=win.destroy,
                     **BUTTON_STYLE).pack(side="right", padx=5)
        
        # Eventos
        tree.bind("<<TreeviewSelect>>", cargar_producto_seleccionado)
        search_var.trace_add("write", lambda *args: actualizar_tabla())
        categoria_var.trace_add("write", lambda *args: actualizar_tabla())
        
        # Inicializar tabla
        actualizar_tabla()
        
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir la ventana: {str(e)}")

# Funciones auxiliares
def cargar_productos():
    if not os.path.exists(PRODUCTOS_FILE):
        return []
    try:
        with open(PRODUCTOS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def guardar_productos(productos):
    try:
        with open(PRODUCTOS_FILE, "w", encoding="utf-8") as f:
            json.dump(productos, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error al guardar productos: {e}")
        return False