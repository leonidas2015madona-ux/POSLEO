import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
import json
from datetime import datetime, timedelta
from collections import defaultdict
from fpdf import FPDF
import os
from assets.styles import *

# Archivo para guardar cierres
CIERRES_FILE = "cierres.json"

def abrir_reportes(parent):
    win = ctk.CTkToplevel(parent)
    win.title("📊 Reportes y Estadísticas")
    win.geometry("1000x700")
    win.grab_set()
    win.protocol("WM_DELETE_WINDOW", win.destroy)
    
    # Frame principal
    main_frame = ctk.CTkFrame(win)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Título
    ctk.CTkLabel(main_frame, text="📊 Reportes y Estadísticas", font=TITLE_FONT).pack(pady=10)
    
    # Pestañas para diferentes tipos de reportes
    tabview = ctk.CTkTabview(main_frame)
    tabview.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Crear pestañas
    tabview.add("Reporte de Ventas")
    tabview.add("Cierre de Turno")
    tabview.add("Estadísticas")
    
    # ===== PESTAÑA 1: REPORTE DE VENTAS =====
    ventas_frame = tabview.tab("Reporte de Ventas")
    
    # Frame de filtros
    filters_frame = ctk.CTkFrame(ventas_frame, fg_color="transparent")
    filters_frame.pack(fill="x", pady=10)
    
    ctk.CTkLabel(filters_frame, text="Rango de fechas:", font=TEXT_FONT).grid(row=0, column=0, padx=5)
    
    # Fechas
    hoy = datetime.now()
    hace_7_dias = hoy - timedelta(days=7)
    
    inicio_var = ctk.StringVar(value=hace_7_dias.strftime("%Y-%m-%d"))
    fin_var = ctk.StringVar(value=hoy.strftime("%Y-%m-%d"))
    
    ctk.CTkEntry(filters_frame, textvariable=inicio_var, width=120, **ENTRY_STYLE).grid(row=0, column=1, padx=5)
    ctk.CTkLabel(filters_frame, text="a", font=TEXT_FONT).grid(row=0, column=2, padx=5)
    ctk.CTkEntry(filters_frame, textvariable=fin_var, width=120, **ENTRY_STYLE).grid(row=0, column=3, padx=5)
    
    # Botón para generar reporte
    def generar_reporte_ventas():
        try:
            fecha_inicio = datetime.strptime(inicio_var.get(), "%Y-%m-%d")
            fecha_fin = datetime.strptime(fin_var.get(), "%Y-%m-%d")
            
            if fecha_inicio > fecha_fin:
                messagebox.showerror("Error", "La fecha de inicio no puede ser mayor a la fecha fin")
                return
            
            # Cargar ventas
            try:
                with open("ventas.json", "r", encoding="utf-8") as f:
                    ventas = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                ventas = []
            
            # Filtrar ventas por fecha
            ventas_filtradas = []
            for venta in ventas:
                try:
                    fecha_venta = datetime.strptime(venta['fecha'], "%Y-%m-%d %H:%M:%S")
                    if fecha_inicio.date() <= fecha_venta.date() <= fecha_fin.date():
                        ventas_filtradas.append(venta)
                except:
                    continue
            
            # Calcular estadísticas
            total_ventas = len(ventas_filtradas)
            total_ingresos = sum(v['total'] for v in ventas_filtradas)
            total_iva = sum(v.get('iva', 0) for v in ventas_filtradas)
            
            # Productos más vendidos
            productos_vendidos = defaultdict(int)
            for venta in ventas_filtradas:
                for producto in venta['productos']:
                    productos_vendidos[producto['nombre']] += producto['cantidad']
            
            top_productos = sorted(productos_vendidos.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Métodos de pago
            metodos_pago = defaultdict(float)
            for venta in ventas_filtradas:
                metodos_pago[venta.get('metodo_pago', 'Efectivo')] += venta['total']
            
            # Actualizar texto de reporte
            texto_reporte = f"REPORTE DE VENTAS\n"
            texto_reporte += f"Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}\n\n"
            texto_reporte += f"Total de ventas: {total_ventas}\n"
            texto_reporte += f"Ingresos totales: ${total_ingresos:.2f}\n"
            texto_reporte += f"IVA recaudado: ${total_iva:.2f}\n\n"
            
            texto_reporte += "TOP 10 PRODUCTOS MÁS VENDIDOS:\n"
            for i, (producto, cantidad) in enumerate(top_productos, 1):
                texto_reporte += f"{i}. {producto}: {cantidad} unidades\n"
            
            texto_reporte += "\nINGRESOS POR MÉTODO DE PAGO:\n"
            for metodo, total in metodos_pago.items():
                porcentaje = (total / total_ingresos * 100) if total_ingresos > 0 else 0
                texto_reporte += f"- {metodo}: ${total:.2f} ({porcentaje:.1f}%)\n"
            
            reporte_textbox.delete("1.0", "end")
            reporte_textbox.insert("1.0", texto_reporte)
            
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha incorrecto. Use YYYY-MM-DD")
    
    ctk.CTkButton(filters_frame, text="Generar Reporte", command=generar_reporte_ventas,
                 **PRIMARY_BUTTON_STYLE).grid(row=0, column=4, padx=10)
    
    # Área de reporte
    reporte_frame = ctk.CTkFrame(ventas_frame)
    reporte_frame.pack(fill="both", expand=True, pady=10)
    
    reporte_textbox = ctk.CTkTextbox(reporte_frame, font=("Consolas", 12))
    reporte_textbox.pack(fill="both", expand=True, padx=10, pady=10)
    
    # ===== PESTAÑA 2: CIERRE DE TURNO =====
    cierre_frame = tabview.tab("Cierre de Turno")
    
    # Frame de fechas para cierre
    cierre_filters_frame = ctk.CTkFrame(cierre_frame, fg_color="transparent")
    cierre_filters_frame.pack(fill="x", pady=10)
    
    hoy = datetime.now().strftime("%Y-%m-%d")
    
    cierre_fecha_var = ctk.StringVar(value=hoy)
    
    ctk.CTkLabel(cierre_filters_frame, text="Fecha:", font=TEXT_FONT).grid(row=0, column=0, padx=5, sticky="w")
    ctk.CTkEntry(cierre_filters_frame, textvariable=cierre_fecha_var, width=120, **ENTRY_STYLE).grid(row=0, column=1, padx=5)
    
    def generar_cierre_turno():
        try:
            with open("ventas.json", "r", encoding="utf-8") as f:
                ventas = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            messagebox.showerror("Error", "No se pudo cargar el historial de ventas.")
            return

        try:
            fecha_cierre = datetime.strptime(cierre_fecha_var.get(), "%Y-%m-%d")
            fecha_siguiente = fecha_cierre + timedelta(days=1)
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha incorrecto. Use YYYY-MM-DD.")
            return

        # Filtrar ventas por fecha
        ventas_dia = []
        for v in ventas:
            try:
                fecha_venta = datetime.strptime(v["fecha"], "%Y-%m-%d %H:%M:%S")
                if fecha_cierre.date() <= fecha_venta.date() < fecha_siguiente.date():
                    ventas_dia.append(v)
            except (ValueError, KeyError):
                continue

        # Calcular totales
        total_ventas = len(ventas_dia)
        total_ingresos = sum(v.get("total", 0) for v in ventas_dia)
        total_efectivo = sum(v.get("efectivo", 0) for v in ventas_dia if v.get("metodo_pago") == "Efectivo")
        total_tarjeta = sum(v.get("total", 0) for v in ventas_dia if v.get("metodo_pago") == "Tarjeta")
        total_transferencia = sum(v.get("total", 0) for v in ventas_dia if v.get("metodo_pago") == "Transferencia")
        total_iva = sum(v.get("iva", 0) for v in ventas_dia)
        
        # Calcular top productos
        top_productos = defaultdict(int)
        for v in ventas_dia:
            for p in v.get("productos", []):
                top_productos[p["nombre"]] += p["cantidad"]

        # Generar resumen
        resumen = "="*50 + "\n"
        resumen += "          CIERRE DE TURNO\n"
        resumen += "="*50 + "\n\n"
        resumen += f"Fecha: {cierre_fecha_var.get()}\n"
        resumen += f"Total de ventas: {total_ventas}\n"
        resumen += f"Ingresos totales: ${total_ingresos:.2f}\n"
        resumen += f"IVA recaudado: ${total_iva:.2f}\n\n"
        
        resumen += "INGRESOS POR MÉTODO DE PAGO:\n"
        resumen += "-"*30 + "\n"
        resumen += f"  Efectivo: ${total_efectivo:.2f}\n"
        resumen += f"  Tarjeta: ${total_tarjeta:.2f}\n"
        resumen += f"  Transferencia: ${total_transferencia:.2f}\n\n"
        
        resumen += "TOP 5 PRODUCTOS MÁS VENDIDOS:\n"
        resumen += "-"*30 + "\n"
        
        for nombre, cant in sorted(top_productos.items(), key=lambda x: x[1], reverse=True)[:5]:
            resumen += f"  {nombre}: {cant} unidades\n"
            
        resumen += "\n" + "="*50

        # Mostrar resumen
        cierre_textbox.delete("1.0", "end")
        cierre_textbox.insert("1.0", resumen)

        # Guardar en histórico
        cierres_guardados = cargar_cierres()
        clave = f"Cierre {cierre_fecha_var.get()}"
        cierres_guardados[clave] = resumen
        guardar_cierres(cierres_guardados)
        
        messagebox.showinfo("Éxito", "Cierre de turno generado correctamente")
        
    ctk.CTkButton(cierre_filters_frame, text="Generar Cierre", command=generar_cierre_turno,
                 **PRIMARY_BUTTON_STYLE).grid(row=0, column=2, padx=10)
    
    # Área de cierre
    cierre_text_frame = ctk.CTkFrame(cierre_frame)
    cierre_text_frame.pack(fill="both", expand=True, pady=10)
    
    cierre_textbox = ctk.CTkTextbox(cierre_text_frame, font=("Consolas", 12))
    cierre_textbox.pack(fill="both", expand=True, padx=10, pady=10)
    
    # ===== PESTAÑA 3: ESTADÍSTICAS =====
    stats_frame = tabview.tab("Estadísticas")
    
    # Frame para estadísticas
    stats_content_frame = ctk.CTkFrame(stats_frame)
    stats_content_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    def generar_estadisticas():
        try:
            with open("ventas.json", "r", encoding="utf-8") as f:
                ventas = json.load(f)
            
            with open("productos.json", "r", encoding="utf-8") as f:
                productos = json.load(f)
            
            # Estadísticas generales
            total_ventas = len(ventas)
            total_ingresos = sum(v['total'] for v in ventas)
            
            # Productos más vendidos
            productos_vendidos = defaultdict(int)
            for venta in ventas:
                for producto in venta['productos']:
                    productos_vendidos[producto['nombre']] += producto['cantidad']
            
            top_productos = sorted(productos_vendidos.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Métodos de pago
            metodos_pago = defaultdict(float)
            for venta in ventas:
                metodos_pago[venta.get('metodo_pago', 'Efectivo')] += venta['total']
            
            # Productos con stock bajo
            stock_bajo = [p for p in productos if p['stock'] < 5]
            
            # Generar reporte
            texto_estadisticas = "ESTADÍSTICAS GENERALES\n"
            texto_estadisticas += "="*30 + "\n\n"
            texto_estadisticas += f"Total de ventas: {total_ventas}\n"
            texto_estadisticas += f"Ingresos totales: ${total_ingresos:.2f}\n\n"
            
            texto_estadisticas += "TOP 10 PRODUCTOS MÁS VENDIDOS:\n"
            texto_estadisticas += "-"*30 + "\n"
            for i, (producto, cantidad) in enumerate(top_productos, 1):
                texto_estadisticas += f"{i}. {producto}: {cantidad} unidades\n"
            
            texto_estadisticas += "\nINGRESOS POR MÉTODO DE PAGO:\n"
            texto_estadisticas += "-"*30 + "\n"
            for metodo, total in metodos_pago.items():
                porcentaje = (total / total_ingresos * 100) if total_ingresos > 0 else 0
                texto_estadisticas += f"- {metodo}: ${total:.2f} ({porcentaje:.1f}%)\n"
            
            texto_estadisticas += "\nPRODUCTOS CON STOCK BAJO:\n"
            texto_estadisticas += "-"*30 + "\n"
            for producto in stock_bajo:
                texto_estadisticas += f"- {producto['nombre']}: {producto['stock']} unidades\n"
            
            stats_textbox.delete("1.0", "end")
            stats_textbox.insert("1.0", texto_estadisticas)
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron generar las estadísticas: {str(e)}")
    
    ctk.CTkButton(stats_content_frame, text="Generar Estadísticas", command=generar_estadisticas,
                 **PRIMARY_BUTTON_STYLE).pack(pady=10)
    
    stats_textbox = ctk.CTkTextbox(stats_content_frame, font=("Consolas", 12))
    stats_textbox.pack(fill="both", expand=True, padx=10, pady=10)
    
    # ===== BOTONES GENERALES =====
    botones_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    botones_frame.pack(fill="x", pady=10)
    
    def exportar_pdf():
        # Determinar qué pestaña está activa
        tab_actual = tabview.get()
        
        if tab_actual == "Reporte de Ventas":
            texto = reporte_textbox.get("1.0", "end")
            titulo = "REPORTE DE VENTAS"
        elif tab_actual == "Cierre de Turno":
            texto = cierre_textbox.get("1.0", "end")
            titulo = "CIERRE DE TURNO"
        elif tab_actual == "Estadísticas":
            texto = stats_textbox.get("1.0", "end")
            titulo = "ESTADÍSTICAS"
        else:
            texto = ""
            titulo = "REPORTE"
            
        if not texto.strip():
            messagebox.showwarning("Advertencia", "No hay contenido para exportar")
            return
        
        archivo = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Guardar reporte como PDF"
        )
        
        if archivo:
            try:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                
                # Título
                pdf.set_font("Arial", "B", 16)
                pdf.cell(0, 10, txt=titulo, ln=True, align="C")
                pdf.ln(10)
                
                # Contenido
                pdf.set_font("Courier", size=10)
                for linea in texto.splitlines():
                    pdf.cell(0, 8, txt=linea, ln=True)
                
                pdf.output(archivo)
                messagebox.showinfo("Éxito", f"Reporte exportado como {archivo}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo exportar el PDF: {str(e)}")
    
    ctk.CTkButton(botones_frame, text="Exportar PDF", command=exportar_pdf,
                 **PRIMARY_BUTTON_STYLE).pack(side="left", padx=5)
    
    ctk.CTkButton(botones_frame, text="Cerrar", command=win.destroy,
                 **BUTTON_STYLE).pack(side="right", padx=5)
    
    # Generar reporte inicial
    generar_reporte_ventas()


# ================== FUNCIONES AUXILIARES ==================

def cargar_cierres():
    if not os.path.exists(CIERRES_FILE):
        return {}
    try:
        with open(CIERRES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def guardar_cierres(data):
    try:
        with open(CIERRES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        messagebox.showerror("Error", f"No se pudieron guardar los cierres: {str(e)}")
        return False