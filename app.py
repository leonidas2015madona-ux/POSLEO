import customtkinter as ctk
from ui.main_window import MainPOS
from ui.ventana_login import mostrar_login
from ui.auth import Autenticacion
from assets.styles import *

def iniciar_aplicacion(usuario_autenticado, usuario):
    if usuario_autenticado:
        # Configurar apariencia
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Crear y ejecutar aplicación
        app = MainPOS()
        app.mainloop()
    else:
        print("Autenticación fallida")

if __name__ == "__main__":
    # Mostrar ventana de login
    auth = Autenticacion()
    
    # Para desarrollo, puedes comentar la siguiente línea y descomentar la que sigue
    # si quieres saltar el login durante el desarrollo
    mostrar_login(None, iniciar_aplicacion)
    
    # Para desarrollo: iniciar directamente sin login
    # iniciar_aplicacion(True, {"username": "admin", "rol": "administrador"})