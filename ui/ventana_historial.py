import customtkinter as ctk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
from assets.styles import *

def abrir_historial(parent):
    ventana = ctk.CTkToplevel(parent)
    ventana.title("🧾 Historial de Ventas")
    ventana.geometry("1200x700")
    ventana.grab_set()
    ventana.transient(parent)
    ventana.protocol("WM_DELETE_WINDOW", ventana.destroy)
    
    # Centrar ventana
    ventana.update_idletasks()
    x = parent.winfo_x() + (parent.winfo_width() - ventana.winfo_width()) // 2
    y = parent.winfo_y() + (parent.winfo_height() - ventana.winfo_height()) // 2
    ventana.geometry(f"+{x}+{y}")

    # Frame principal
    main_frame = ctk.CTkFrame(ventana)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Título
    ctk.CTkLabel(main_frame, text="📋 Historial de Ventas", font=TITLE_FONT).pack(pady=10)

    # Frame para filtros
    filter_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    filter_frame.pack(fill="x", pady=10)
    
    # Filtros por fecha
    ctk.CTkLabel(filter_frame, text="Desde:", font=TEXT_FONT).pack(side="left", padx=5)
    fecha_inicio = ctk.CTkEntry(filter_frame, placeholder_text="YYYY-MM-DD", width=120)
    fecha_inicio.pack(side="left", padx=5)
    
    ctk.CTkLabel(filter_frame, text="Hasta:", font=TEXT_FONT).pack(side="left", padx=5)
    fecha_fin = ctk.CTkEntry(filter_frame, placeholder_text="YYYY-MM-DD", width=120)
    fecha_fin.pack(side="left", padx=5)
    
    def aplicar_filtros():
        try:
            # Cargar ventas
            with open("ventas.json", "r", encoding="utf-8") as f:
                ventas = json.load(f)
            
            # Filtrar por fecha si se especificó
            fecha_inicio_val = fecha_inicio.get()
            fecha_fin_val = fecha_fin.get()
            
            if fecha_inicio_val and fecha_fin_val:
                ventas_filtradas = []
                for venta in ventas:
                    try:
                        fecha_venta = datetime.strptime(venta['fecha'], "%Y-%m-%d %H:%M:%S").date()
                        fecha_ini = datetime.strptime(fecha_inicio_val, "%Y-%m-%d").date()
                        fecha_f = datetime.strptime(fecha_fin_val, "%Y-%m-%d").date()
                        
                        if fecha_ini <= fecha_venta <= fecha_f:
                            ventas_filtradas.append(venta)
                    except:
                        continue
                
                llenar_tabla(ventas_filtradas)
            else:
                llenar_tabla(ventas)
                
        except (FileNotFoundError, json.JSONDecodeError):
            messagebox.showwarning("Sin datos", "No hay historial de ventas disponible.")
    
    ctk.CTkButton(filter_frame, text="🔍 Aplicar Filtros", command=aplicar_filtros).pack(side="left", padx=10)
    
    # Botón para exportar
    def exportar_historial():
        try:
            with open("ventas.json", "r", encoding="utf-8") as f:
                ventas = json.load(f)
            
            # Crear archivo de texto con el historial
            from tkinter import filedialog
            archivo = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
            )
            
            if archivo:
                with open(archivo, "w", encoding="utf-8") as f:
                    f.write("HISTORIAL DE VENTAS - Librería 24hs\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for venta in ventas:
                        f.write(f"Fecha: {venta.get('fecha', 'N/A')}\n")
                        f.write(f"Total: ${venta.get('total', 0):.2f}\n")
                        f.write(f"Método de pago: {venta.get('metodo_pago', 'N/A')}\n")
                        f.write("Productos:\n")
                        
                        for producto in venta.get('productos', []):
                            f.write(f"  - {producto['nombre']} x{producto['cantidad']} - ${producto['precio'] * producto['cantidad']:.2f}\n")
                        
                        f.write("-" * 30 + "\n\n")
                
                messagebox.showinfo("Éxito", f"Historial exportado a {archivo}")
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar el historial: {str(e)}")
    
    ctk.CTkButton(filter_frame, text="📄 Exportar", command=exportar_historial).pack(side="right", padx=5)

    # Crear Treeview con scrollbar
    tree_frame = ctk.CTkFrame(main_frame)
    tree_frame.pack(fill="both", expand=True, pady=10)

    scrollbar = ttk.Scrollbar(tree_frame)
    scrollbar.pack(side="right", fill="y")

    tree = ttk.Treeview(tree_frame, 
                       columns=("fecha", "total", "metodo_pago", "productos"), 
                       show="headings", 
                       height=20,
                       yscrollcommand=scrollbar.set)
    
    scrollbar.config(command=tree.yview)

    # Configurar columnas
    column_config = {
        "fecha": {"text": "Fecha y Hora", "width": 150},
        "total": {"text": "Total", "width": 100},
        "metodo_pago": {"text": "Método de Pago", "width": 120},
        "productos": {"text": "Productos", "width": 400}
    }
    
    for col, config in column_config.items():
        tree.heading(col, text=config["text"])
        tree.column(col, width=config["width"], anchor="center")

    tree.column("productos", anchor="w")

    tree.pack(fill="both", expand=True)

    # Estilo para la tabla
    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Arial", 12, "bold"))
    style.configure("Treeview", font=("Arial", 11), rowheight=25)

    def llenar_tabla(ventas):
        # Limpiar tabla
        for item in tree.get_children():
            tree.delete(item)
        
        # Llenar tabla
        for venta in reversed(ventas):  # Mostrar las más recientes primero
            productos_texto = ", ".join(f"{p['nombre']} x{p['cantidad']}" for p in venta.get("productos", []))
            tree.insert("", "end", values=(
                venta.get("fecha", "N/A"),
                f"${venta.get('total', 0):.2f}",
                venta.get('metodo_pago', 'N/A'),
                productos_texto
            ))

    # Cargar ventas inicialmente
    try:
        with open("ventas.json", "r", encoding="utf-8") as f:
            ventas = json.load(f)
        llenar_tabla(ventas)
    except (FileNotFoundError, json.JSONDecodeError):
        messagebox.showwarning("Sin datos", "No hay historial de ventas disponible.")

    # Botón para cerrar
    ctk.CTkButton(main_frame, text="Cerrar", command=ventana.destroy).pack(pady=10)