import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from database.connection import Database
from interface import *
from config.config import *
from config.services import users_dao

class MainWindow:
    def __init__(self, root, employee_id, on_logout=None):
        self.root = root
        self.on_logout = on_logout
        self.employee_id = employee_id
        self.root.title("ERP Supermercado")
        self.root.geometry("1500x720+0+0")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)
        self.db = Database()
        self.db.connect_db(use_db=False)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.create_sidebar()
        self.create_main_area()
        self.create_buttons()
        self.show_panel_principal()

    def on_close(self):
        anulated = self.sale.anulate_sale(on_close=True)
        if anulated:
            self.root.destroy()
            self.root.quit()

    def create_sidebar(self):
        self.sidebar = tk.Frame(self.root, width=220, bg=SIDEBAR_COLOR)
        self.sidebar.pack(side="left", fill="y")

        title = tk.Label(self.sidebar, text="🛒 ERP Market", bg=SIDEBAR_COLOR,
                         fg=SIDEBAR_TEXT, font=("Segoe UI", 16, "bold"))
        title.pack(pady=20)

        self.sidebar_buttons_name = [
            "Panel Principal", "Nueva Venta", "Productos", "Proveedores",
            "Empleados"
        ]

    def create_main_area(self):
        self.main_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.main_frame.pack(side="left", fill="both", expand=True)

        self.container = {}
        for button_name in self.sidebar_buttons_name:
            frame = tk.Frame(self.main_frame, bg=BG_COLOR)
            self.container[button_name] = frame
            self.container[button_name].pack(fill='both', expand=True)
        
        # Se pasa el frame donde se construye cada pantalla
        self.dashboard = Dashboard(self.container['Panel Principal'], self.employee_id)
        self.sale = NewSale(self.container['Nueva Venta'], self.employee_id)
        self.producto = Product(self.container['Productos'], self.employee_id)
        self.proveedor = Provider(self.container['Proveedores'])
        self.empleados = Employee(self.container['Empleados'])
        
    def require_role(*allowed_roles):
        def decorator(func):
            def wrapper(self, *args, **kwargs):
                role = users_dao.get_user_data(employee_id=self.employee_id)[2]
                if role in allowed_roles:
                    return func(self, *args, **kwargs)
                else:
                    messagebox.showerror("Acceso denegado", f"No tienes permisos para acceder a esta sección con el rol de {role.upper()}.")
            return wrapper
        return decorator

   # AQUí CREAMOS LAS FUNCIONES PARA CONTROLAR LA VENTANA QUE SE MUESTRA AL HACER CLIC EN LOS BOTONES DEL SIDEBAR
    def show_panel_principal(self):
        # Anulate pending sale on sales_tree if exists
        confirmation = self.sale.anulate_sale(from_sidebar=True)
        if not confirmation:
            return

        for button_name in self.sidebar_buttons_name:
            self.buttons[button_name].config(bg=SIDEBAR_COLOR)
            self.container[button_name].pack_forget()
            self.container['Panel Principal'].pack(expand=True, fill='both')
            
        self.buttons['Panel Principal'].config(bg=SIDEBAR_FOCUS_COLOR_BTN)
        self.dashboard.refresh_interface()

    @require_role("Empleado", "Supervisor", "RRHH", "Gerente", "Admin")
    def show_nueva_venta(self):
        # Anulate pending sale on sales_tree if exists
        confirmation = self.sale.anulate_sale(from_sidebar=True)
        if not confirmation:
            return

        self.sale.restore_placeholder(event=None)
        for button_name in self.sidebar_buttons_name:
            self.buttons[button_name].config(bg=SIDEBAR_COLOR)
            self.container[button_name].pack_forget()
            self.container['Nueva Venta'].pack(expand=True, fill='both')

        self.buttons['Nueva Venta'].config(bg=SIDEBAR_FOCUS_COLOR_BTN)
        self.sale.refresh_interface()
    
    @require_role("Supervisor", "Gerente", "Admin")
    def show_productos(self):
        # Anulate pending sale on sales_tree if exists
        confirmation = self.sale.anulate_sale(from_sidebar=True)
        if not confirmation:
            return

        for button_name in self.sidebar_buttons_name:
            self.buttons[button_name].config(bg=SIDEBAR_COLOR)
            self.container[button_name].pack_forget()
            self.container['Productos'].pack(expand=True, fill='both')

        self.buttons['Productos'].config(bg=SIDEBAR_FOCUS_COLOR_BTN)
        self.producto.refresh_interface()

    @require_role("Supervisor", "Gerente", "Admin")
    def show_proveedores(self):
        # Anulate pending sale on sales_tree if exists
        confirmation = self.sale.anulate_sale(from_sidebar=True)
        if not confirmation:
            return

        for button_name in self.sidebar_buttons_name:
            self.buttons[button_name].config(bg=SIDEBAR_COLOR)
            self.container[button_name].pack_forget()
            self.container['Proveedores'].pack(expand=True, fill='both')

        self.buttons['Proveedores'].config(bg=SIDEBAR_FOCUS_COLOR_BTN)
        self.proveedor.refresh_interface()

    @require_role("Supervisor", "RRHH", "Gerente", "Admin")
    def show_empleados(self):
        # Anulate pending sale on sales_tree if exists
        confirmation = self.sale.anulate_sale(from_sidebar=True)
        if not confirmation:
            return
        
        for button_name in self.sidebar_buttons_name:
            self.buttons[button_name].config(bg=SIDEBAR_COLOR)
            self.container[button_name].pack_forget()
            self.container['Empleados'].pack(expand=True, fill='both')
        
        self.buttons['Empleados'].config(bg=SIDEBAR_FOCUS_COLOR_BTN)
        self.empleados.refresh_interface()

    # CREAMOS LOS BOTONES DEL SIDEBAR
    def create_buttons(self):
        self.buttons = {}  # ← aquí guardamos todos los botones
        commands = ['show_panel_principal', 'show_nueva_venta', 'show_productos', 
                    'show_proveedores', 'show_empleados']

        for i, button_name in enumerate(self.sidebar_buttons_name):
            command = getattr(self, commands[i])
            button = tk.Button(
                self.sidebar, text=button_name, bg=SIDEBAR_COLOR, fg=SIDEBAR_TEXT,
                font=("Segoe UI", 11), bd=0, activebackground="#374151",
                activeforeground="white", anchor="w", padx=20, cursor='hand2', command=command
            )
            button.pack(fill="x", pady=2)
            self.buttons[button_name] = button  # ← lo guardamos con su nombre

        logout_btn = tk.Button(self.sidebar, text="Cerrar sesión", bg=SIDEBAR_COLOR, fg=SIDEBAR_TEXT,
                font=("Segoe UI", 11), bd=0, activebackground="#374151",
                activeforeground="white", anchor="w", padx=20, cursor='hand2', command=self.on_logout)
        logout_btn.pack(fill="x", pady=(410, 0))
        

        
        