# utils/impresora.py
import os
from datetime import datetime
from tkinter import messagebox

class Impresora:
    def __init__(self):
        self.impresora_configurada = self.detectar_impresora()

    def detectar_impresora(self):
        # En Windows
        if os.name == 'nt':
            try:
                import win32print
                impresoras = win32print.EnumPrinters(2)
                return impresoras[0][2] if impresoras else None
            except:
                return None
        # En Linux
        else:
            try:
                # Intentar detectar impresora por defecto
                import subprocess
                result = subprocess.run(['lpstat', '-d'], capture_output=True, text=True)
                if result.returncode == 0 and ":" in result.stdout:
                    return result.stdout.split(":")[1].strip()
                return None
            except:
                return None

    def imprimir_ticket(self, venta_data):
        try:
            # Generar contenido del ticket
            contenido = self.generar_contenido_ticket(venta_data)
            
            if self.impresora_configurada:
                self.imprimir_directo(contenido)
            else:
                self.guardar_archivo(contenido, venta_data)
                
            return True, "Ticket impreso/guardado correctamente"
        except Exception as e:
            return False, f"Error al imprimir: {str(e)}"

    def generar_contenido_ticket(self, venta_data):
        lines = []
        lines.append("=" * 40)
        lines.append("       LIBRERÍA 24HS")
        lines.append("=" * 40)
        lines.append(f"Fecha: {venta_data['fecha']}")
        lines.append(f"Ticket: #{hash(venta_data['fecha']) % 10000:04d}")
        lines.append("-" * 40)
        
        for producto in venta_data['productos']:
            line = f"{producto['nombre'][:20]:20} {producto['cantidad']:2} x ${producto['precio']:7.2f}"
            lines.append(line)
        
        lines.append("-" * 40)
        lines.append(f"TOTAL: ${venta_data['total']:>31.2f}")
        lines.append(f"EFECTIVO: ${venta_data.get('efectivo', 0):>29.2f}")
        lines.append(f"VUELTO: ${venta_data.get('vuelto', 0):>30.2f}")
        lines.append("=" * 40)
        lines.append("¡Gracias por su compra!")
        lines.append("=" * 40)
        
        return "\n".join(lines)

    def imprimir_directo(self, contenido):
        if os.name == 'nt':  # Windows
            import win32print
            import win32api
            
            hprinter = win32print.OpenPrinter(self.impresora_configurada)
            try:
                win32print.StartDocPrinter(hprinter, 1, ("Ticket", None, "RAW"))
                win32print.StartPagePrinter(hprinter)
                win32print.WritePrinter(hprinter, contenido.encode('utf-8'))
                win32print.EndPagePrinter(hprinter)
                win32print.EndDocPrinter(hprinter)
            finally:
                win32print.ClosePrinter(hprinter)
        else:  # Linux
            import subprocess
            lpr = subprocess.Popen(["lpr", "-P", self.impresora_configurada], stdin=subprocess.PIPE)
            lpr.stdin.write(contenido.encode('utf-8'))
            lpr.stdin.close()

    def guardar_archivo(self, contenido, venta_data):
        # Guardar en archivo si no hay impresora
        tickets_dir = "tickets"
        if not os.path.exists(tickets_dir):
            os.makedirs(tickets_dir)
        
        filename = f"ticket_{venta_data['fecha'].replace(':', '-').replace(' ', '_')}.txt"
        with open(os.path.join(tickets_dir, filename), 'w', encoding='utf-8') as f:
            f.write(contenido)