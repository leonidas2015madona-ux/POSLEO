import json
import os
from dataclasses import dataclass

@dataclass
class Usuario:
    username: str
    nombre: str
    rol: str

class Autenticacion:
    def __init__(self):
        self.usuario_actual = None
        self.archivo_usuarios = "data/usuarios.json"
        self.cargar_usuarios()
    
    def cargar_usuarios(self):
        if os.path.exists(self.archivo_usuarios):
            with open(self.archivo_usuarios, 'r', encoding='utf-8') as f:
                self.usuarios = json.load(f)['usuarios']
        else:
            # Crear archivo con usuarios por defecto
            self.usuarios = [
                {
                    "username": "admin",
                    "password": "admin123", 
                    "rol": "administrador",
                    "nombre": "Administrador Principal"
                }
            ]
            os.makedirs('data', exist_ok=True)
            with open(self.archivo_usuarios, 'w', encoding='utf-8') as f:
                json.dump({"usuarios": self.usuarios}, f, indent=4, ensure_ascii=False)
    
    def login(self, username, password):
        for usuario in self.usuarios:
            if usuario['username'] == username and usuario['password'] == password:
                self.usuario_actual = Usuario(
                    username=usuario['username'],
                    nombre=usuario['nombre'],
                    rol=usuario['rol']
                )
                return True
        return False
    
    def tiene_permiso(self, permiso):
        if not self.usuario_actual:
            return False
        
        permisos = {
            'administrador': ['gestion_productos', 'gestion_usuarios', 'ver_reportes', 'realizar_ventas', 'cerrar_turnos'],
            'empleado': ['realizar_ventas', 'ver_historial_ventas', 'cerrar_turnos'],
            'cajero': ['realizar_ventas', 'ver_historial_ventas']
        }
        
        return permiso in permisos.get(self.usuario_actual.rol, [])