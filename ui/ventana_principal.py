import customtkinter as ctk
from tkinter import messagebox
from ui.auth import Autenticacion

def centrar_ventana(win, ancho, alto):
    win.update_idletasks()
    pantalla_ancho = win.winfo_screenwidth()
    pantalla_alto = win.winfo_screenheight()
    x = (pantalla_ancho // 2) - (ancho // 2)
    y = (pantalla_alto // 2) - (alto // 2)
    win.geometry(f'{ancho}x{alto}+{x}+{y}')

def mostrar_login(parent, callback):
    win = ctk.CTkToplevel(parent)
    win.title("🔐 Iniciar Sesión - Librería 24hs")
    win.geometry("400x350")
    win.resizable(False, False)
    win.grab_set()
    win.transient(parent)
    
    # Centrar ventana
    win.update_idletasks()
    width = win.winfo_width()
    height = win.winfo_height()
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")

    auth = Autenticacion()

    # Frame principal con gradiente
    main_frame = ctk.CTkFrame(win, fg_color=("white", "#2b2b2b"))
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Logo o título
    ctk.CTkLabel(main_frame, 
                text="📚 Librería 24hs", 
                font=("Arial", 24, "bold"),
                text_color=("#2c3e50", "#ecf0f1")).pack(pady=(30, 10))

    ctk.CTkLabel(main_frame, 
                text="Sistema de Facturación", 
                font=("Arial", 14),
                text_color=("#7f8c8d", "#bdc3c7")).pack(pady=(0, 30))

    # Frame de formulario
    form_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    form_frame.pack(pady=10, padx=20, fill="both", expand=True)

    ctk.CTkLabel(form_frame, text="Usuario:", font=("Arial", 12)).pack(pady=(10, 5))
    usuario_var = ctk.StringVar()
    usuario_entry = ctk.CTkEntry(form_frame, 
                                textvariable=usuario_var, 
                                width=250,
                                height=40,
                                font=("Arial", 14),
                                placeholder_text="Ingrese su usuario")
    usuario_entry.pack(pady=5)

    ctk.CTkLabel(form_frame, text="Contraseña:", font=("Arial", 12)).pack(pady=(15, 5))
    password_var = ctk.StringVar()
    password_entry = ctk.CTkEntry(form_frame, 
                                textvariable=password_var, 
                                show="•", 
                                width=250,
                                height=40,
                                font=("Arial", 14),
                                placeholder_text="Ingrese su contraseña")
    password_entry.pack(pady=5)

    def intentar_login():
        usuario = usuario_var.get().strip()
        password = password_var.get()
        
        if not usuario or not password:
            messagebox.showwarning("Advertencia", "Por favor complete todos los campos")
            return
            
        if auth.login(usuario, password):
            callback(True, auth.usuario_actual)
            win.destroy()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
            password_var.set("")
            usuario_entry.focus_set()

    # Botón de login
    login_btn = ctk.CTkButton(form_frame, 
                            text="Iniciar Sesión", 
                            command=intentar_login,
                            height=45,
                            font=("Arial", 14, "bold"),
                            fg_color=("#3498db", "#2980b9"),
                            hover_color=("#2980b9", "#2471a3"))
    login_btn.pack(pady=25)

    # Información de usuarios demo
    info_text = """Usuarios demo:
• admin / admin123 (Administrador)
• empleado / empleado123 (Empleado)
• caja / caja123 (Cajero)"""
    
    ctk.CTkLabel(form_frame, 
                text=info_text,
                font=("Arial", 10),
                text_color=("#7f8c8d", "#95a5a6"),
                justify="left").pack(pady=(10, 5))

    # Enter para iniciar sesión
    win.bind('<Return>', lambda e: intentar_login())

    # Focus en el primer campo
    usuario_entry.focus_set()

    # Hacer que la ventana sea modal
    win.protocol("WM_DELETE_WINDOW", lambda: parent.quit())
    
    