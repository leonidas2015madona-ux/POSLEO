# app.py - Corrección de importaciones
import customtkinter as ctk
from ui.ventana_login import mostrar_login  # ✅ Correcto
from ui.ventana_principal import mostrar_ventana_principal  # ✅ Correcto

def iniciar_aplicacion(autenticado, usuario_actual):
    if autenticado:
        root.withdraw()
        mostrar_ventana_principal(root, usuario_actual)
    else:
        root.quit()

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    root.withdraw()
    
    mostrar_login(root, iniciar_aplicacion)
    
    root.mainloop()