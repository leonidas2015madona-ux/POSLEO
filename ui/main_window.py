import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os
from PIL import Image, ImageTk
import math

from ui.productos_logic import cargar_productos, guardar_productos
from ui.ventas_logic import calcular_total, calcular_vuelto
from ui.ventana_productos import abrir_gestion_productos
from ui.ventana_historial import abrir_historial
from ui.ventana_reportes import abrir_reportes
from assets.styles import *


class MainPOS(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Punto de Venta - Librería 24hs")
        self.geometry("1400x800")
        self.minsize(1200, 700)
        
        # Configurar tema
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Cargar productos
        self.productos = cargar_productos()
        self.venta_actual = []
        self.categoria_actual = "Todos"
        self.iva_porcentaje = 21  # IVA modificable, valor por defecto 21%
        
        # Verificar si existen los archivos necesarios
        self.verificar_archivos()
        
        # Configurar grid
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.construir_interfaz()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def verificar_archivos(self):
        archivos = ["productos.json", "ventas.json", "cierres.json"]
        for archivo in archivos:
            if not os.path.exists(archivo):
                with open(archivo, "w", encoding="utf-8") as f:
                    json.dump([], f, indent=2, ensure_ascii=False)

    def construir_interfaz(self):
        # Panel principal dividido en dos partes
        self.left_frame = ctk.CTkFrame(self, fg_color=LIGHT_BG)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.right_frame = ctk.CTkFrame(self, fg_color="white")
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        
        # Configurar grid de los frames
        self.left_frame.grid_rowconfigure(1, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)
        
        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)
        
        # Construir secciones
        self.construir_header()
        self.construir_busqueda()
        self.construir_productos()
        self.construir_carrito()
        self.construir_totales()

    def construir_header(self):
        # Header con logo, reloj y botones de acción
        header_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent", height=60)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Logo o título
        title_label = ctk.CTkLabel(header_frame, text="📚 Librería 24hs", 
                                  font=TITLE_FONT, text_color=PRIMARY_COLOR)
        title_label.grid(row=0, column=0, sticky="w")
        
        # Reloj
        self.clock_label = ctk.CTkLabel(header_frame, text="", font=SUBHEADER_FONT, 
                                       text_color=DARK_TEXT)
        self.clock_label.grid(row=0, column=1, sticky="e", padx=20)
        self.update_clock()
        
        # Botones de acción rápida
        action_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        action_frame.grid(row=0, column=2, sticky="e")

        # Botones con iconos y texto más descriptivos
        ctk.CTkButton(action_frame, text="🔄 Reiniciar", width=100, command=self.resetear_venta,
                     **ACCENT_BUTTON_STYLE).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="📦 Productos", width=100, command=self.abrir_gestion_productos,
                     **PRIMARY_BUTTON_STYLE).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="📊 Reportes", width=100, command=lambda: abrir_reportes(self),
                     **PRIMARY_BUTTON_STYLE).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="📋 Historial", width=100, command=lambda: abrir_historial(self),
                     **PRIMARY_BUTTON_STYLE).pack(side="left", padx=5)

    def construir_busqueda(self):
        # Barra de búsqueda en la parte superior izquierda
        search_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent", height=50)
        search_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        search_frame.grid_columnconfigure(0, weight=1)
        
        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var, 
                                   placeholder_text="🔍 Buscar productos...", 
                                   height=INPUT_HEIGHT, font=TEXT_FONT)
        search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        search_entry.bind("<KeyRelease>", self.buscar_productos)
        
        # Filtros por categoría
        categorias = ["Todos", "Libros", "Papelería", "Material Oficina", "Electrónica", "Otros"]
        categoria_menu = ctk.CTkOptionMenu(search_frame, values=categorias, 
                                          command=self.filtrar_categoria,
                                          height=INPUT_HEIGHT, font=TEXT_FONT)
        categoria_menu.grid(row=0, column=1, sticky="e")

    def construir_productos(self):
        # Frame principal de productos debajo de la barra de búsqueda
        products_main_frame = ctk.CTkFrame(self.left_frame, fg_color="white")
        products_main_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        products_main_frame.grid_rowconfigure(0, weight=1)
        products_main_frame.grid_columnconfigure(0, weight=1)
        
        # Grid de productos
        self.products_frame = ctk.CTkScrollableFrame(products_main_frame, fg_color="white")
        self.products_frame.grid(row=0, column=0, sticky="nsew")
        
        # Mostrar productos inicialmente
        self.mostrar_productos(self.productos)

    def construir_carrito(self):
        # Carrito debajo de los productos
        cart_main_frame = ctk.CTkFrame(self.left_frame, fg_color="white")
        cart_main_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0, 10))
        cart_main_frame.grid_rowconfigure(1, weight=1)
        cart_main_frame.grid_columnconfigure(0, weight=1)
        
        # Header del carrito
        cart_header = ctk.CTkFrame(cart_main_frame, fg_color="transparent", height=40)
        cart_header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        cart_title = ctk.CTkLabel(cart_header, text="🛒 Carrito de Compra", 
                                 font=SUBHEADER_FONT, text_color=PRIMARY_COLOR)
        cart_title.pack(side="left")
        
        clear_btn = ctk.CTkButton(cart_header, text="🗑️ Limpiar", width=80,
                                 command=self.limpiar_carrito, **ACCENT_BUTTON_STYLE)
        clear_btn.pack(side="right")
        
        # Tabla del carrito
        cart_table_frame = ctk.CTkFrame(cart_main_frame, fg_color="transparent")
        cart_table_frame.grid(row=1, column=0, sticky="nsew")
        cart_table_frame.grid_rowconfigure(0, weight=1)
        cart_table_frame.grid_columnconfigure(0, weight=1)
        
        # Crear treeview con scrollbar
        style = ttk.Style()
        style.configure("Custom.Treeview", rowheight=TABLE_ROW_HEIGHT, font=("Roboto", 10))
        style.configure("Custom.Treeview.Heading", font=("Roboto", 11, "bold"))
        
        self.cart_tree = ttk.Treeview(cart_table_frame, columns=("qty", "name", "price", "total"), 
                                     show="headings", style="Custom.Treeview", height=8)
        
        self.cart_tree.heading("qty", text="Cant")
        self.cart_tree.heading("name", text="Producto")
        self.cart_tree.heading("price", text="Precio")
        self.cart_tree.heading("total", text="Total")
        
        self.cart_tree.column("qty", width=50, anchor="center")
        self.cart_tree.column("name", width=150, anchor="w")
        self.cart_tree.column("price", width=80, anchor="e")
        self.cart_tree.column("total", width=80, anchor="e")
        
        scrollbar = ttk.Scrollbar(cart_table_frame, orient="vertical", command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=scrollbar.set)
        
        self.cart_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Bind events
        self.cart_tree.bind("<Delete>", lambda e: self.eliminar_producto())
        self.cart_tree.bind("<Double-1>", lambda e: self.modificar_cantidad())

    def construir_totales(self):
        # Frame de totales y pago en el panel derecho
        totals_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        totals_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        totals_frame.grid_rowconfigure(8, weight=1)
        
        # Título
        ctk.CTkLabel(totals_frame, text="Resumen de Venta", 
                    font=HEADER_FONT, text_color=PRIMARY_COLOR).grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # IVA modificable
        ctk.CTkLabel(totals_frame, text="IVA (%):", font=TEXT_FONT).grid(row=1, column=0, sticky="w")
        self.iva_var = ctk.StringVar(value=str(self.iva_porcentaje))
        iva_entry = ctk.CTkEntry(totals_frame, textvariable=self.iva_var, width=60, **ENTRY_STYLE)
        iva_entry.grid(row=1, column=1, sticky="w", padx=(5, 0))
        self.iva_var.trace_add("write", self.actualizar_totales)
        
        # Subtotales
        ctk.CTkLabel(totals_frame, text="Subtotal:", font=SUBHEADER_FONT).grid(row=2, column=0, sticky="w", pady=(10, 0))
        self.subtotal_label = ctk.CTkLabel(totals_frame, text="$0.00", font=SUBHEADER_FONT)
        self.subtotal_label.grid(row=2, column=1, sticky="e", pady=(10, 0))
        
        ctk.CTkLabel(totals_frame, text="IVA:", font=SUBHEADER_FONT).grid(row=3, column=0, sticky="w", pady=(5, 0))
        self.iva_label = ctk.CTkLabel(totals_frame, text="$0.00", font=SUBHEADER_FONT)
        self.iva_label.grid(row=3, column=1, sticky="e", pady=(5, 0))
        
        ctk.CTkLabel(totals_frame, text="Total:", font=HEADER_FONT).grid(row=4, column=0, sticky="w", pady=(10, 0))
        self.total_label = ctk.CTkLabel(totals_frame, text="$0.00", font=HEADER_FONT, text_color=PRIMARY_COLOR)
        self.total_label.grid(row=4, column=1, sticky="e", pady=(10, 0))
        
        # Separador
        separator = ttk.Separator(totals_frame, orient="horizontal")
        separator.grid(row=5, column=0, columnspan=2, sticky="ew", pady=10)
        
        # Método de pago
        ctk.CTkLabel(totals_frame, text="Método de pago:", font=TEXT_FONT).grid(row=6, column=0, sticky="w")
        self.metodo_pago = ctk.StringVar(value="Efectivo")
        pago_menu = ctk.CTkOptionMenu(totals_frame, variable=self.metodo_pago,
                                     values=["Efectivo", "Tarjeta", "Transferencia"],
                                     height=INPUT_HEIGHT, font=TEXT_FONT)
        pago_menu.grid(row=6, column=1, sticky="ew", pady=(0, 10))
        
        # Efectivo entregado
        self.efectivo_frame = ctk.CTkFrame(totals_frame, fg_color="transparent")
        self.efectivo_frame.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        ctk.CTkLabel(self.efectivo_frame, text="Efectivo:", font=TEXT_FONT).grid(row=0, column=0, sticky="w")
        self.efectivo_var = ctk.StringVar()
        efectivo_entry = ctk.CTkEntry(self.efectivo_frame, textvariable=self.efectivo_var,
                                     placeholder_text="0.00", **ENTRY_STYLE)
        efectivo_entry.grid(row=0, column=1, sticky="e")
        self.efectivo_var.trace_add("write", self.calcular_vuelto)
        
        # Vuelto
        ctk.CTkLabel(self.efectivo_frame, text="Vuelto:", font=TEXT_FONT).grid(row=1, column=0, sticky="w", pady=(5, 0))
        self.vuelto_label = ctk.CTkLabel(self.efectivo_frame, text="$0.00", font=TEXT_FONT)
        self.vuelto_label.grid(row=1, column=1, sticky="e", pady=(5, 0))
        
        # Botón de pago
        pay_btn = ctk.CTkButton(totals_frame, text="💳 Realizar Pago", command=self.realizar_pago,
                               **SUCCESS_BUTTON_STYLE)
        pay_btn.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        # Actualizar visibilidad de efectivo según método de pago
        self.metodo_pago.trace_add("write", self.actualizar_metodo_pago)
        self.actualizar_metodo_pago()

    def actualizar_metodo_pago(self, *args):
        if self.metodo_pago.get() == "Efectivo":
            self.efectivo_frame.grid()
        else:
            self.efectivo_frame.grid_remove()

    def mostrar_productos(self, productos):
        # Limpiar frame
        for widget in self.products_frame.winfo_children():
            widget.destroy()
        
        # Organizar productos en grid
        row, col = 0, 0
        max_cols = 4
        
        for producto in productos:
            # Crear frame para cada producto
            product_frame = ctk.CTkFrame(self.products_frame, width=150, height=150, 
                                        fg_color="white", border_width=1, 
                                        border_color="#e0e0e0", corner_radius=8)
            product_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            product_frame.grid_propagate(False)
            
            # Configurar grid interno
            product_frame.grid_rowconfigure(1, weight=1)
            product_frame.grid_columnconfigure(0, weight=1)
            
            # Nombre del producto (truncado si es muy largo)
            name = producto['nombre']
            if len(name) > 20:
                name = name[:17] + "..."
            
            name_label = ctk.CTkLabel(product_frame, text=name, font=("Roboto", 10, "bold"),
                                     text_color=DARK_TEXT, wraplength=130)
            name_label.grid(row=0, column=0, sticky="nsew", padx=5, pady=(5, 0))
            
            # Precio
            price_label = ctk.CTkLabel(product_frame, text=f"${producto['precio']:.2f}", 
                                      font=("Roboto", 12, "bold"), text_color=SECONDARY_COLOR)
            price_label.grid(row=1, column=0, sticky="nsew", padx=5)
            
            # Stock
            stock_color = ACCENT_COLOR if producto['stock'] < 5 else "#7f8c8d"
            stock_label = ctk.CTkLabel(product_frame, text=f"Stock: {producto['stock']}", 
                                      font=("Roboto", 9), text_color=stock_color)
            stock_label.grid(row=2, column=0, sticky="nsew", padx=5)
            
            # Botón para agregar
            add_btn = ctk.CTkButton(product_frame, text="➕ Agregar", width=60, height=30,
                                   command=lambda p=producto: self.agregar_al_carrito(p),
                                   fg_color=SUCCESS_COLOR, hover_color="#27ae60", font=("Roboto", 10))
            add_btn.grid(row=3, column=0, sticky="se", padx=5, pady=5)
            
            # Actualizar posición
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def agregar_al_carrito(self, producto):
        # Verificar stock
        if producto['stock'] <= 0:
            messagebox.showwarning("Stock agotado", f"No hay stock de {producto['nombre']}")
            return
        
        # Buscar si el producto ya está en el carrito
        for item in self.venta_actual:
            if item['nombre'] == producto['nombre']:
                item['cantidad'] += 1
                self.actualizar_carrito()
                return
        
        # Agregar nuevo producto al carrito
        self.venta_actual.append({
            'nombre': producto['nombre'],
            'precio': producto['precio'],
            'cantidad': 1
        })
        
        self.actualizar_carrito()

    def actualizar_carrito(self):
        # Limpiar treeview
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        
        # Agregar items
        for item in self.venta_actual:
            total = item['precio'] * item['cantidad']
            self.cart_tree.insert("", "end", values=(
                item['cantidad'],
                item['nombre'],
                f"${item['precio']:.2f}",
                f"${total:.2f}"
            ))
        
        self.actualizar_totales()

    def actualizar_totales(self, *args):
        try:
            self.iva_porcentaje = float(self.iva_var.get())
        except ValueError:
            self.iva_porcentaje = 0
            
        subtotal = calcular_total(self.venta_actual)
        iva = subtotal * (self.iva_porcentaje / 100)
        total = subtotal + iva
        
        self.subtotal_label.configure(text=f"${subtotal:.2f}")
        self.iva_label.configure(text=f"${iva:.2f}")
        self.total_label.configure(text=f"${total:.2f}")
        
        self.calcular_vuelto()

    def calcular_vuelto(self, *args):
        if self.metodo_pago.get() == "Efectivo":
            try:
                efectivo = float(self.efectivo_var.get() or 0)
                subtotal = calcular_total(self.venta_actual)
                iva = subtotal * (self.iva_porcentaje / 100)
                total = subtotal + iva
                vuelto = efectivo - total
                
                if vuelto < 0:
                    self.vuelto_label.configure(text=f"${vuelto:.2f}", text_color=ACCENT_COLOR)
                else:
                    self.vuelto_label.configure(text=f"${vuelto:.2f}", text_color=SUCCESS_COLOR)
            except ValueError:
                self.vuelto_label.configure(text="$0.00", text_color=DARK_TEXT)
        else:
            self.vuelto_label.configure(text="$0.00", text_color=DARK_TEXT)

    def eliminar_producto(self):
        seleccion = self.cart_tree.selection()
        if not seleccion:
            return
        
        for item in seleccion:
            valores = self.cart_tree.item(item, "values")
            nombre = valores[1]
            
            # Eliminar de la venta actual
            self.venta_actual = [p for p in self.venta_actual if p['nombre'] != nombre]
        
        self.actualizar_carrito()

    def modificar_cantidad(self):
        seleccion = self.cart_tree.selection()
        if not seleccion:
            return
        
        item = seleccion[0]
        valores = self.cart_tree.item(item, "values")
        nombre = valores[1]
        
        # Buscar el producto en la venta actual
        for producto in self.venta_actual:
            if producto['nombre'] == nombre:
                # Ventana para modificar cantidad
                ventana = ctk.CTkToplevel(self)
                ventana.title("Modificar cantidad")
                ventana.geometry("300x150")
                ventana.resizable(False, False)
                ventana.grab_set()
                ventana.protocol("WM_DELETE_WINDOW", ventana.destroy)
                
                ctk.CTkLabel(ventana, text=f"Cantidad de {nombre}:").pack(pady=10)
                
                cantidad_var = ctk.StringVar(value=str(producto['cantidad']))
                cantidad_entry = ctk.CTkEntry(ventana, textvariable=cantidad_var, **ENTRY_STYLE)
                cantidad_entry.pack(pady=5)
                
                def actualizar_cantidad():
                    try:
                        nueva_cantidad = int(cantidad_var.get())
                        if nueva_cantidad <= 0:
                            messagebox.showerror("Error", "La cantidad debe ser mayor a 0")
                            return
                        
                        # Verificar stock
                        for p in self.productos:
                            if p['nombre'] == nombre and nueva_cantidad > p['stock']:
                                messagebox.showerror("Error", f"No hay suficiente stock. Disponible: {p['stock']}")
                                return
                        
                        producto['cantidad'] = nueva_cantidad
                        self.actualizar_carrito()
                        ventana.destroy()
                    except ValueError:
                        messagebox.showerror("Error", "Ingrese un número válido")
                
                ctk.CTkButton(ventana, text="Actualizar", command=actualizar_cantidad,
                             **PRIMARY_BUTTON_STYLE).pack(pady=10)
                
                break

    def limpiar_carrito(self):
        if not self.venta_actual:
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de que desea vaciar el carrito?"):
            self.venta_actual = []
            self.actualizar_carrito()

    def realizar_pago(self):
        if not self.venta_actual:
            messagebox.showwarning("Carrito vacío", "No hay productos en el carrito")
            return
        
        # Verificar stock
        for item in self.venta_actual:
            for producto in self.productos:
                if producto['nombre'] == item['nombre'] and producto['stock'] < item['cantidad']:
                    messagebox.showerror("Stock insuficiente", 
                                       f"No hay suficiente stock de {item['nombre']}. Disponible: {producto['stock']}")
                    return
        
        # Verificar pago en efectivo
        if self.metodo_pago.get() == "Efectivo":
            try:
                efectivo = float(self.efectivo_var.get() or 0)
                subtotal = calcular_total(self.venta_actual)
                iva = subtotal * (self.iva_porcentaje / 100)
                total = subtotal + iva
                
                if efectivo < total:
                    messagebox.showerror("Pago insuficiente", 
                                       f"El efectivo (${efectivo:.2f}) es menor al total (${total:.2f})")
                    return
            except ValueError:
                messagebox.showerror("Error", "Ingrese un valor válido para el efectivo")
                return
        
        # Procesar venta
        try:
            # Cargar ventas existentes
            try:
                with open("ventas.json", "r", encoding="utf-8") as f:
                    ventas = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                ventas = []
            
            # Crear objeto de venta
            subtotal = calcular_total(self.venta_actual)
            iva = subtotal * (self.iva_porcentaje / 100)
            total = subtotal + iva
            
            if self.metodo_pago.get() == "Efectivo":
                efectivo = float(self.efectivo_var.get())
                vuelto = efectivo - total
            else:
                efectivo = 0
                vuelto = 0
            
            venta = {
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "productos": self.venta_actual.copy(),
                "subtotal": subtotal,
                "iva": iva,
                "total": total,
                "metodo_pago": self.metodo_pago.get(),
                "efectivo": efectivo,
                "vuelto": vuelto,
                "iva_porcentaje": self.iva_porcentaje
            }
            
            # Agregar a historial
            ventas.append(venta)
            
            # Guardar en archivo
            with open("ventas.json", "w", encoding="utf-8") as f:
                json.dump(ventas, f, indent=2, ensure_ascii=False)
            
            # Actualizar stock
            for item in self.venta_actual:
                for producto in self.productos:
                    if producto['nombre'] == item['nombre']:
                        producto['stock'] -= item['cantidad']
            
            guardar_productos(self.productos)
            
            # Mostrar resumen
            self.mostrar_resumen_venta(venta)
            
            # Resetear venta
            self.resetear_venta()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar la venta: {str(e)}")

    def mostrar_resumen_venta(self, venta):
        ventana = ctk.CTkToplevel(self)
        ventana.title("Venta realizada")
        ventana.geometry("400x500")
        ventana.resizable(False, False)
        ventana.grab_set()
        ventana.protocol("WM_DELETE_WINDOW", ventana.destroy)
        
        # Título
        ctk.CTkLabel(ventana, text="✅ Venta realizada con éxito", 
                    font=HEADER_FONT, text_color=SUCCESS_COLOR).pack(pady=10)
        
        # Frame de resumen
        frame = ctk.CTkFrame(ventana, fg_color=LIGHT_BG)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Información de la venta
        ctk.CTkLabel(frame, text=f"Fecha: {venta['fecha']}", font=TEXT_FONT).pack(anchor="w", pady=5)
        ctk.CTkLabel(frame, text=f"Método de pago: {venta['metodo_pago']}", font=TEXT_FONT).pack(anchor="w", pady=5)
        ctk.CTkLabel(frame, text=f"IVA: {venta['iva_porcentaje']}%", font=TEXT_FONT).pack(anchor="w", pady=5)
        
        # Productos
        ctk.CTkLabel(frame, text="Productos:", font=SUBHEADER_FONT).pack(anchor="w", pady=(10, 5))
        
        for producto in venta['productos']:
            texto = f"{producto['nombre']} x{producto['cantidad']} - ${producto['precio'] * producto['cantidad']:.2f}"
            ctk.CTkLabel(frame, text=texto, font=SMALL_FONT).pack(anchor="w", padx=10)
        
        # Totales
        ctk.CTkLabel(frame, text="Totales:", font=SUBHEADER_FONT).pack(anchor="w", pady=(10, 5))
        ctk.CTkLabel(frame, text=f"Subtotal: ${venta['subtotal']:.2f}", font=TEXT_FONT).pack(anchor="w", padx=10)
        ctk.CTkLabel(frame, text=f"IVA ({venta['iva_porcentaje']}%): ${venta['iva']:.2f}", font=TEXT_FONT).pack(anchor="w", padx=10)
        ctk.CTkLabel(frame, text=f"Total: ${venta['total']:.2f}", font=SUBHEADER_FONT).pack(anchor="w", padx=10)
        
        if venta['metodo_pago'] == "Efectivo":
            ctk.CTkLabel(frame, text=f"Efectivo: ${venta['efectivo']:.2f}", font=TEXT_FONT).pack(anchor="w", padx=10)
            ctk.CTkLabel(frame, text=f"Vuelto: ${venta['vuelto']:.2f}", font=TEXT_FONT).pack(anchor="w", padx=10)
        
        # Botón para cerrar
        ctk.CTkButton(ventana, text="Cerrar", command=ventana.destroy,
                     **PRIMARY_BUTTON_STYLE).pack(pady=10)

    def resetear_venta(self):
        self.venta_actual = []
        self.efectivo_var.set("")
        self.metodo_pago.set("Efectivo")
        self.actualizar_carrito()

    def buscar_productos(self, event=None):
        query = self.search_var.get().lower()
        
        if not query:
            self.mostrar_productos(self.productos)
            return
        
        resultados = [p for p in self.productos if query in p['nombre'].lower()]
        self.mostrar_productos(resultados)

    def filtrar_categoria(self, categoria):
        self.categoria_actual = categoria
        
        if categoria == "Todos":
            self.mostrar_productos(self.productos)
        else:
            resultados = [p for p in self.productos if p.get('categoria', 'Otros') == categoria]
            self.mostrar_productos(resultados)

    def abrir_gestion_productos(self):
        # Abrir ventana de gestión de productos
        abrir_gestion_productos(self)
        # Recargar productos después de cerrar la ventana
        self.productos = cargar_productos()
        self.mostrar_productos(self.productos)

    def update_clock(self):
        now = datetime.now().strftime("%H:%M:%S - %d/%m/%Y")
        self.clock_label.configure(text=now)
        self.after(1000, self.update_clock)

    def on_closing(self):
        if messagebox.askokcancel("Salir", "¿Está seguro de que desea salir?"):
            self.destroy()


if __name__ == "__main__":
    app = MainPOS()
    app.mainloop()