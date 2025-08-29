import json
import os
from dataclasses import dataclass

@dataclass
class Usuario:
    username: str
    nombre: str
    rol: str
    permisos: list

class Autenticacion:
    def __init__(self):
        self.usuario_actual = None
        self.archivo_usuarios = "data/usuarios.json"
        self.cargar_usuarios()
    
    def cargar_usuarios(self):
        if os.path.exists(self.archivo_usuarios):
            try:
                with open(self.archivo_usuarios, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.usuarios = data.get('usuarios', [])
            except:
                self.crear_usuarios_por_defecto()
        else:
            self.crear_usuarios_por_defecto()
    
    def crear_usuarios_por_defecto(self):
        self.usuarios = [
            {
                "username": "admin",
                "password": "admin123",
                "rol": "administrador",
                "nombre": "Administrador Principal",
                "permisos": ["gestion_usuarios", "gestion_productos", "ver_reportes", "realizar_ventas", "cerrar_turnos"]
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
                    rol=usuario['rol'],
                    permisos=usuario.get('permisos', [])
                )
                return True
        return False
    
    def tiene_permiso(self, permiso):
        if not self.usuario_actual:
            return False
        return permiso in self.usuario_actual.permisos