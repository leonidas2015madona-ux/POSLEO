# ui/reportes.py
import json
from datetime import datetime, timedelta
from collections import defaultdict
import matplotlib.pyplot as plt
from fpdf import FPDF
import os

class GeneradorReportes:
    def __init__(self):
        self.reportes_dir = "reportes"
        if not os.path.exists(self.reportes_dir):
            os.makedirs(self.reportes_dir)

    def generar_reporte_ventas(self, fecha_inicio, fecha_fin):
        try:
            with open("ventas.json", "r", encoding="utf-8") as f:
                ventas = json.load(f)
        except:
            return None, "Error al cargar ventas"
        
        # Filtrar ventas por fecha
        ventas_filtradas = []
        for venta in ventas:
            try:
                fecha_venta = datetime.strptime(venta['fecha'], "%Y-%m-%d %H:%M:%S")
                if fecha_inicio <= fecha_venta <= fecha_fin:
                    ventas_filtradas.append(venta)
            except:
                continue
        
        # Calcular estadísticas
        total_ventas = len(ventas_filtradas)
        total_dinero = sum(venta['total'] for venta in ventas_filtradas)
        promedio_venta = total_dinero / total_ventas if total_ventas > 0 else 0
        
        # Productos más vendidos
        productos_vendidos = defaultdict(int)
        for venta in ventas_filtradas:
            for producto in venta['productos']:
                productos_vendidos[producto['nombre']] += producto['cantidad']
        
        top_productos = sorted(productos_vendidos.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Generar PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Reporte de Ventas", 0, 1, "C")
        pdf.ln(5)
        
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}", 0, 1)
        pdf.cell(0, 10, f"Total ventas: {total_ventas}", 0, 1)
        pdf.cell(0, 10, f"Total dinero: ${total_dinero:.2f}", 0, 1)
        pdf.cell(0, 10, f"Promedio por venta: ${promedio_venta:.2f}", 0, 1)
        pdf.ln(5)
        
        pdf.cell(0, 10, "Top 10 productos más vendidos:", 0, 1)
        for i, (producto, cantidad) in enumerate(top_productos, 1):
            pdf.cell(0, 10, f"{i}. {producto}: {cantidad} unidades", 0, 1)
        
        # Guardar reporte
        nombre_archivo = f"reporte_ventas_{fecha_inicio.strftime('%Y%m%d')}_{fecha_fin.strftime('%Y%m%d')}.pdf"
        ruta_completa = os.path.join(self.reportes_dir, nombre_archivo)
        pdf.output(ruta_completa)
        
        return ruta_completa, "Reporte generado correctamente"
    
    def generar_grafico_ventas(self, dias=30):
        try:
            with open("ventas.json", "r", encoding="utf-8") as f:
                ventas = json.load(f)
        except:
            return None, "Error al cargar ventas"
        
        # Agrupar ventas por día
        ventas_por_dia = defaultdict(float)
        fecha_fin = datetime.now()
        fecha_inicio = fecha_fin - timedelta(days=dias)
        
        for i in range((fecha_fin - fecha_inicio).days + 1):
            fecha = fecha_inicio + timedelta(days=i)
            ventas_por_dia[fecha.strftime("%Y-%m-%d")] = 0
        
        for venta in ventas:
            try:
                fecha_venta = datetime.strptime(venta['fecha'], "%Y-%m-%d %H:%M:%S")
                if fecha_inicio <= fecha_venta <= fecha_fin:
                    fecha_str = fecha_venta.strftime("%Y-%m-%d")
                    ventas_por_dia[fecha_str] += venta['total']
            except:
                continue
        
        # Crear gráfico
        fechas = sorted(ventas_por_dia.keys())
        valores = [ventas_por_dia[fecha] for fecha in fechas]
        
        plt.figure(figsize=(10, 6))
        plt.plot(fechas, valores, marker='o')
        plt.title(f"Ventas últimos {dias} días")
        plt.xlabel("Fecha")
        plt.ylabel("Ventas ($)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Guardar gráfico
        nombre_archivo = f"grafico_ventas_{dias}dias.png"
        ruta_completa = os.path.join(self.reportes_dir, nombre_archivo)
        plt.savefig(ruta_completa)
        plt.close()
        
        return ruta_completa, "Gráfico generado correctamente"