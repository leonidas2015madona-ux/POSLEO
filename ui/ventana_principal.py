import customtkinter as ctk
from tkinter import messagebox
from ui.auth import Autenticacion

def mostrar_ventana_principal(parent, usuario_actual):
    """
    Muestra la ventana principal de la aplicación después del login exitoso
    """
    # Ocultar la ventana de login (parent)
    parent.withdraw()
    
    # Crear ventana principal
    root = ctk.CTkToplevel()
    root.title("Sistema de Facturación - Librería 24hs")
    root.geometry("1200x700")
    
    # Configurar el protocolo de cierre
    def on_closing():
        parent.quit()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Etiqueta de bienvenida con el usuario
    welcome_label = ctk.CTkLabel(
        root, 
        text=f"Bienvenido: {usuario_actual.nombre} ({usuario_actual.rol})",
        font=("Arial", 16, "bold")
    )
    welcome_label.pack(pady=20)
    
    # Aquí puedes agregar el resto de tu interfaz según el rol del usuario
    if usuario_actual.rol == "administrador":
        # Mostrar todas las opciones para administradores
        admin_label = ctk.CTkLabel(
            root,
            text="Modo Administrador: Acceso completo al sistema",
            font=("Arial", 14)
        )
        admin_label.pack(pady=10)
        
    elif usuario_actual.rol == "empleado":
        # Mostrar opciones limitadas para empleados
        empleado_label = ctk.CTkLabel(
            root,
            text="Modo Empleado: Acceso a ventas y cierre de turnos",
            font=("Arial", 14)
        )
        empleado_label.pack(pady=10)
        
    elif usuario_actual.rol == "cajero":
        # Mostrar solo opciones de ventas para cajeros
        cajero_label = ctk.CTkLabel(
            root,
            text="Modo Cajero: Solo acceso a ventas",
            font=("Arial", 14)
        )
        cajero_label.pack(pady=10)
    
    # Botón de salir
    logout_btn = ctk.CTkButton(
        root,
        text="Cerrar Sesión",
        command=on_closing,
        fg_color="#e74c3c",
        hover_color="#c0392b"
    )
    logout_btn.pack(pady=20)
    
    return root

# La clase VentanaPrincipal original (si la necesitas)
class VentanaPrincipal:
    def __init__(self, parent, usuario_actual):
        self.parent = parent
        self.usuario_actual = usuario_actual
        self.ventana = None
        
    def mostrar(self):
        self.ventana = mostrar_ventana_principal(self.parent, self.usuario_actual)
        
    def ocultar(self):
        if self.ventana:
            self.ventana.withdraw()
            
    def mostrar_de_nuevo(self):
        if self.ventana:
            self.ventana.deiconify()