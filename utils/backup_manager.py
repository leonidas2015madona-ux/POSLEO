# utils/backup_manager.py
import json
import os
import shutil
from datetime import datetime
from tkinter import filedialog, messagebox

class BackupManager:
    def __init__(self):
        self.backup_dir = "backups"
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

    def crear_backup(self):
        try:
            # Lista de archivos a respaldar
            archivos = ["productos.json", "ventas.json", "cierres.json", "usuarios.json"]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(self.backup_dir, f"backup_{timestamp}")
            
            os.makedirs(backup_path)
            
            for archivo in archivos:
                if os.path.exists(archivo):
                    shutil.copy2(archivo, backup_path)
            
            # Mantener solo los 10 backups más recientes
            self.limpiar_backups_antiguos()
            
            return True, f"Backup creado: {timestamp}"
        except Exception as e:
            return False, f"Error al crear backup: {str(e)}"

    def restaurar_backup(self, parent):
        try:
            backup_path = filedialog.askdirectory(title="Seleccionar carpeta de backup")
            if not backup_path:
                return False, "Operación cancelada"
            
            archivos = ["productos.json", "ventas.json", "cierres.json", "usuarios.json"]
            
            for archivo in archivos:
                origen = os.path.join(backup_path, archivo)
                if os.path.exists(origen):
                    shutil.copy2(origen, ".")
            
            return True, "Backup restaurado correctamente"
        except Exception as e:
            return False, f"Error al restaurar backup: {str(e)}"

    def limpiar_backups_antiguos(self):
        try:
            backups = []
            for item in os.listdir(self.backup_dir):
                if os.path.isdir(os.path.join(self.backup_dir, item)) and item.startswith("backup_"):
                    backups.append((item, os.path.getctime(os.path.join(self.backup_dir, item))))
            
            # Ordenar por fecha de creación (más antiguos primero)
            backups.sort(key=lambda x: x[1])
            
            # Eliminar backups excedentes (mantener máximo 10)
            while len(backups) > 10:
                oldest = backups.pop(0)
                shutil.rmtree(os.path.join(self.backup_dir, oldest[0]))
        except:
            pass  # Silenciar errores en la limpieza