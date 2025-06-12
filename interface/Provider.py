import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from config.config import *
from config.services import provider_dao, product_dao
from datetime import datetime, timedelta


class Provider(tk.Frame):
    def __init__(self, parent):
        self.proveedores_main_frame = parent
        self.crear_interfaz()
        self.datos_proveedores = {} # ACTUALIZAR ESTO
    
    def crear_interfaz(self):
        # ----- HEADER -----
        header = tk.Frame(self.proveedores_main_frame, bg="#2b6cb0", height=60)
        header.pack(fill="x")
        tk.Label(header, text="Gestión de Proveedores", bg="#2b6cb0", fg="white", font=("Segoe UI", 16, "bold")).pack(pady=15)

        # ----- MAIN BODY -----
        main = tk.Frame(self.proveedores_main_frame, bg="#edf2f7")
        main.pack(fill="both", expand=True, padx=20, pady=20)

        form_card = tk.Frame(main, bg="white", bd=1, relief="solid")
        form_card.place(x=20, y=20, width=500, height=550)

        table_card = tk.Frame(main, bg="white", bd=1, relief="solid")
        table_card.place(x=550, y=20, width=750, height=600)

        # ----- FORM CARD (Left side) -----
        form_card = tk.Frame(main, bg="white", relief="flat")
        form_card.place(x=20, y=20, width=500, height=550)

        def create(label_text, type):
            frame = tk.Frame(form_card, bg="white")
            frame.pack(fill="x", padx=20, pady=5)
            tk.Label(frame, text=label_text, bg="white", anchor="w").pack(fill="x")
            entry = type(frame)
            entry.pack(fill="x")
            return entry

        self.nombre_entry = create("Nombre:", ttk.Entry)
        self.telefono_entry = create("Teléfono:", ttk.Entry)
        self.email_entry = create("Email:", ttk.Entry)
        self.direccion_entry = create("Dirección:", ttk.Entry)
        
        style = ttk.Style()
        style.configure("Accent.TButton", foreground="black", background="#2b6cb0")
        style.map("Accent.TButton",
                background=[("active", "#2c5282")],
                foreground=[("disabled", "#aaa")])
        
        style.configure("Eliminar.TButton", background="#e53e3e", foreground="black")
        style.map("Eliminar.TButton", background=[("active", "#c53030")])

        self.button_add_prod = ttk.Button(form_card, text="Agregar producto", style="Accent.TButton", command=self.add_product)
        self.button_add_prod.pack(pady=(10, 0))
        
        # ADD PRODUCTS FOR THIS PROVIDER
        style = ttk.Style()
        style.configure("Prod.Treeview", font=("Arial", 7))
        style.configure("Prod.Treeview.Heading", font=("Arial", 7))

        columnas_y_ancho = {
            "Nombre": 80, 
            "Stock": 35,
            "Categ. gen.": 40,
            "Categoría": 40,
            "€ Compra": 45,
            "€ Venta": 40,
            "F. Prod.": 60, 
            "F. Venc.": 60
        }

        prod_frame = tk.LabelFrame(form_card, text="Productos de este proveedor (opcional)", bg="white", fg="black")
        prod_frame.pack(fill="both", padx=20, pady=10, expand=True)

        columns = list(columnas_y_ancho.keys())
        self.prod_treeview = ttk.Treeview(prod_frame, columns=columns, show="headings", height=5, style="Prod.Treeview")

        # Configurar columnas
        for col, width in columnas_y_ancho.items():
            self.prod_treeview.heading(col, text=col)
            self.prod_treeview.column(col, width=width, anchor="center")

        self.prod_treeview.pack(fill="both", expand=True)
        self.prod_treeview.bind("<Double-1>", self.edit_prod)

        # ----- BUTTONS -----
        btn_frame = tk.Frame(main, bg="#edf2f7")
        btn_frame.place(x=20, y=570, width=500, height=50)
        
        self.boton_agregar_prov = ttk.Button(btn_frame, text="Agregar proveedor", style="Accent.TButton", command=self.add_provider)
        self.boton_agregar_prov.pack(side="right", padx=5, pady=10)

        self.boton_editar_prov = ttk.Button(btn_frame, text="Editar datos", style="Accent.TButton", command=self.edit_prov)
        self.boton_editar_prov.pack(side="right", padx=5, pady=10)

        self.boton_eliminar_prov = ttk.Button(btn_frame, text="Eliminar proveedor", style="Eliminar.TButton", command=self.del_provider)
        self.boton_eliminar_prov.pack(side="right", padx=5, pady=10)

        self.boton_editar_prod = ttk.Button(btn_frame, text="Editar producto", style="Accent.TButton", command=self.edit_prod)
        self.boton_editar_prod.pack(side="left", padx=5, pady=10)

        # ----- TABLE CARD (Right side) -----
        table_card = tk.Frame(main, bg="white", relief="flat")
        table_card.place(x=550, y=20, width=750, height=600)

        columnas_y_ancho = {
            "ID": 10,
            "Nombre": 60,
            "Telefono": 40, 
            "Email": 80, 
            "Direccion": 140, 
            "Productos": 30
            }
        self.tree_proveedores = ttk.Treeview(table_card, columns=list(columnas_y_ancho.keys()), show="headings", height=30)
        for name, width in columnas_y_ancho.items():
            self.tree_proveedores.heading(name, text=name.capitalize())
            self.tree_proveedores.column(name, width=width, anchor="center")
        self.tree_proveedores.pack(fill="both", padx=10, pady=10)
        self.tree_proveedores.bind("<ButtonRelease-1>", self.popup)
        self.tree_proveedores.bind("<Double-1>", self.edit_prov)

# ------------------------- FUNCIONES AUXILIARES ------------------------- #
    def refresh_interface(self):
        self.refresh_left_panel()
        self.refresh_right_panel()
    
    def refresh_right_panel(self):
        providers = provider_dao.get_all_providers()
        
        for row in self.tree_proveedores.get_children():
            self.tree_proveedores.delete(row)

        for prov in providers:
            id, provider, phone, email, address = prov
            prov = (id, provider, phone, email, address) + ("[...]",)
            self.tree_proveedores.insert("", "end", values=prov)
    
    def refresh_left_panel(self):        
        self.nombre_entry.delete(0, tk.END)
        categorias_existentes = list(sorted(set(prod[0] for prod in product_dao.get_general_categories())))
        if '_nueva categoría_' not in categorias_existentes:
            categorias_existentes.append('_nueva categoría_')
        self.telefono_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.direccion_entry.delete(0, tk.END)

        for row in self.prod_treeview.get_children():
            self.prod_treeview.delete(row)

    
    def on_close_popup_prod_prov(self, window=None, x=None, y=None, category_to_select=None):
        if hasattr(self, 'popup_categories') and self.popup_categories.winfo_exists():
            self.popup_categories.destroy()
        
        window.destroy()
        if (x and y and category_to_select):
            self.tree_proveedores.event_generate("<Button-1>", x=x, y=y)
            self.tree_proveedores.event_generate("<ButtonRelease-1>", x=x, y=y)

            for item in self.tree_prov_cat.get_children():
                category = self.tree_prov_cat.item(item, "values")[0]
                print(category_to_select, category)
                if category_to_select == category:
                    self.tree_prov_cat.selection_set(item)
                    self.tree_prov_cat.focus(item)
                    self.tree_prov_cat.event_generate("<ButtonRelease-1>")
                    break

        elif (x and y):
            self.tree_proveedores.event_generate("<ButtonRelease-1>", x=x, y=y)

    def refresh_products_popup_prod_prov(self, prov_id=None, category_general=None):
        products = product_dao.get_products_by_prov(prov_id, category=category_general)
        for item in self.tree_prov_prod.get_children():
            self.tree_prov_prod.delete(item)
        for prod in products:
            self.tree_prov_prod.insert('', 'end', values=(prod[0], prod[1], prod[4], prod[2], prod[3], prod[5], prod[6], prod[8], prod[9]))
    
    def popup(self, event):
        region = self.tree_proveedores.identify("region", event.x, event.y)
        columna = self.tree_proveedores.identify_column(event.x)
        fila_id = self.tree_proveedores.identify_row(event.y)
        # Detecting the value of x and y, so we can generate a click event later when closing the popup TopLevel Window
        self.x = event.x
        self.y = event.y
        
        def popup_prod(event=None, category_general=None, break_popup=None):
            if event:
                selection = self.tree_prov_cat.selection()
                if selection:
                    value = self.tree_prov_cat.item(selection, "values")
                    cat_to_filter = value[0]
                    
                    popup_prod(category_general=cat_to_filter) # It is passed with event=None and category_general with value. The "else" statement is activated then
            else:
                self.popup_prod_of_prov = tk.Toplevel()
                self.popup_prod_of_prov.title(f"Productos de {nombre_prov}")
                self.popup_prod_of_prov.geometry("750x500+360+95")
                self.popup_prod_of_prov.resizable("False", "False")
                self.popup_prod_of_prov.grab_set()
                if category_general:
                    self.popup_prod_of_prov.protocol("WM_DELETE_WINDOW", lambda: self.on_close_popup_prod_prov(window=self.popup_prod_of_prov, x=self.x, y=self.y))
                else:
                    self.popup_prod_of_prov.protocol("WM_DELETE_WINDOW", lambda: self.on_close_popup_prod_prov(window=self.popup_prod_of_prov))
                    

                columnas_y_ancho = {
                    "ID": 20,
                    "Producto": 100, 
                    "Stock": 20,
                    "Categoría general": 60,
                    "Categoría": 60,
                    "€ Compra": 20,
                    "€ Venta": 20,
                    "F. Prod.": 60, 
                    "F. Venc.": 60
                }
                
                self.tree_prov_prod = ttk.Treeview(self.popup_prod_of_prov, columns=list(columnas_y_ancho.keys()), show="headings", height=10)
                for name, width in columnas_y_ancho.items():
                    self.tree_prov_prod.heading(name, text=name)
                    self.tree_prov_prod.column(name, width=width, anchor="center")
                self.tree_prov_prod.pack(fill="both", expand=True)

                self.refresh_products_popup_prod_prov(prov_id=prov_id, category_general=category_general)
                                
                btn_frame = ttk.Frame(self.popup_prod_of_prov, style="TButton", padding=5)
                btn_frame.pack(fill="x")
                style = ttk.Style()
                
                self.add_new_prod_btn = ttk.Button(btn_frame, text="Añadir producto", style="Accent.TButton", command=lambda: self.add_product(prov_id=prov_id))
                self.add_new_prod_btn.pack(side="left", padx=(270, 0))
                self.delete_prod_btn = ttk.Button(btn_frame, text="Eliminar producto", style="Eliminar.TButton", command=lambda: self.del_prod_for_prov(parent=self.popup_prod_of_prov))
                self.delete_prod_btn.pack(side="left", padx=(10, 0))

                    

        if region == "cell" and columna == "#6":  # "productos" es la 6ta columna
            valor_fila = self.tree_proveedores.item(fila_id, "values")
            prov_id = int(valor_fila[0])
            nombre_prov = valor_fila[1]
            categories = product_dao.get_general_categories(prov_id=prov_id)
            if categories:
                categories = list(set([cat[0] for cat in categories]))
                                
                self.popup_categories = tk.Toplevel()
                self.popup_categories.title(f"Seleccione una categoría")
                self.popup_categories.geometry("200x300+155+95")
                self.popup_categories.resizable("False", "False")
                self.popup_categories.grab_set()

                columnas_y_ancho = {
                    "Categorías": 100,
                }
            
                self.tree_prov_cat = ttk.Treeview(self.popup_categories, columns=list(columnas_y_ancho.keys()), show="headings", height=30)
                for name, width in columnas_y_ancho.items():
                    self.tree_prov_cat.heading(name, text=name)
                    self.tree_prov_cat.column(name, width=width, anchor="center")
                self.tree_prov_cat.pack(fill="both", expand=True)
                self.tree_prov_cat.bind("<ButtonRelease-1>", popup_prod)
                
                for category in categories:
                    self.tree_prov_cat.insert('', 'end', values=(category,))
            
            else: # Let's skip the Categories popup and go directly to the products, so the user can add a product to the empty treeview
                popup_prod()
            

    def add_provider(self):
        nombre = self.nombre_entry.get().strip().title()
        telefono = self.telefono_entry.get().strip()
        email = self.email_entry.get().strip().lower()
        direccion = self.direccion_entry.get().strip().capitalize()

        if not nombre or not telefono or not email or not direccion:
            messagebox.showerror(title="Faltan datos", message="Debe rellenar todos los datos que se solicitan en el formulario.")
            return
                    
        # Let's check if already exists a provider with the same name
        prov_id = provider_dao.get_prov_id(nombre)
        if prov_id:
            messagebox.showwarning(title="Ya existe este proveedor", 
                                   message="Ya existe un proveedor con el mismo nombre. No es posible añadirlo nuevamente. " \
                                   "Si se trata del mismo proveedor, intente modificar sus datos.")
            self.refresh_left_panel()
            return
            

        # Insert provider into BBDD
        prov_id_inserted = provider_dao.insert_provider(nombre, telefono, email, direccion)
        if not prov_id_inserted:
            messagebox.showerror(title="Error al registrar proveedor", message="Ocurrió un error al intentar registrar el proveedor en la BBDD.")
            return
        
        # Check if there are products on the treeview for this provider
        products_in_tree = self.prod_treeview.get_children()
        products_data = []
        if products_in_tree:
            for item in products_in_tree:
                prod_data = self.prod_treeview.item(item, 'values')
                product = prod_data[0]
                category_general = prod_data[2]
                category = prod_data[3]
                stock = prod_data[1]
                buy_price = prod_data[4]
                sell_price = prod_data[5]
                provider_id = prov_id_inserted
                prod_date = prod_data[6]
                exp_date = prod_data[7]
                fecha_prod_obj = datetime.strptime(prod_date, '%d/%m/%Y')
                fecha_venc_obj = datetime.strptime(exp_date, '%d/%m/%Y')
                prod_data_to_insert = (product, category_general, category, stock, buy_price, sell_price, provider_id, fecha_prod_obj, fecha_venc_obj)
                products_data.append(prod_data_to_insert)
            
            # Insert products in DB
            inserted = product_dao.insert_products(products_data)
            if not inserted:
                messagebox.showerror(title="Error al añadir productos", message="Ocurrió un error al intentar agregar los productos a la base de datos.")
                return
            
            self.refresh_interface()
            if len(products_data) == 0:
                messagebox.showinfo(title="Proveedor registrado", message="Se registró el proveedor satisfactoriamente.")
            elif len(products_data) > 1:
                messagebox.showinfo(title="Proveedor y productos añadidos", message="Se añadió correctamente el proveedor y los productos a la base de datos.")
            else:
                messagebox.showinfo(title="Proveedor y producto añadido", message="Se añadió correctamente el proveedor y producto a la base de datos.")

    
    def del_provider(self):
        selection = self.tree_proveedores.selection()
        if selection:
            values = []
            for item in selection:
                valor_fila = self.tree_proveedores.item(item, "values")
                prov_id = int(valor_fila[0])
                values.append((prov_id,))
            
            if len(selection) < 2:
                confirmation = messagebox.askokcancel(title="Eliminar proveedor", message="¿Seguro que quiere eliminar este proveedor?")
            else:
                confirmation = messagebox.askokcancel(title="Eliminar proveedores", message="¿Seguro que quiere eliminar estos proveedores?")
            if not confirmation:
                return

            deleted = provider_dao.delete_provider(values)
            if len(selection) < 2:
                if deleted == "IntegrityError":
                    messagebox.showerror(title="No se puede eliminar el proveedor", 
                                        message="No puede eliminarse este proveedor mientras existan registros de productos o ventas asociados a este."
                                        "Intente eliminar primero estos registros si quiere continuar con la eliminación de este proveedor.")
                    return

                if deleted:
                    self.refresh_interface()
                    messagebox.showinfo(title="Proveedor eliminado", message=f"Se eliminó correctamente el proveedor seleccionado.")
                else:
                    messagebox.showerror(title="Error al eliminar el proveedor", message="Ocurrió un error al intentar eliminar el proveedor seleccionado.")
                    return
            else:
                if deleted == "IntegrityError":
                    messagebox.showerror(title="No se puede eliminar el proveedor", 
                                        message="No puede eliminarse uno o más de los proveedores seleccionados mientras existan registros de productos o ventas " \
                                        "asociados a este. Intente eliminar uno a uno para identificar el/los proveedor(es) que no puede(n) eliminarse.")
                    return

                if deleted:
                    self.refresh_interface()
                    messagebox.showinfo(title="Proveedores eliminados", message=f"Se eliminaron correctamente los proveedores seleccionados.")
                    return
        else:
            messagebox.showerror(title="Sin selección", message="Debes seleccionar al menos un proveedor para eliminar.")
            return

    def edit_prov (self, event=None):
        selection = self.tree_proveedores.selection()
        if not selection or len(selection) > 1:
            messagebox.showerror(title="Sin selección", message="Debe seleccionar exactamente un proveedor para editarlo.")
            return

        def edit_prov_data(values):
            popup = tk.Toplevel()
            popup.title("Editar proveedor")
            popup.geometry("250x300")
            popup.resizable("False", "False")
            popup.grab_set()

            prov_id = int(values[0])
            selection = values[1]
            prov_data = provider_dao.get_provider_data(prov_id)
            prov_id, prov_name, prov_phone, prov_email, prov_address = prov_data

            form_card = tk.Frame(popup, bg="white", relief="flat")
            form_card.pack(expand=True, fill="both")

            def create_input(label_text, entry_var=None):
                frame = tk.Frame(form_card)
                frame.pack(fill="x", padx=20, pady=5)
                tk.Label(frame, text=label_text, bg="white", anchor="w").pack(fill="x")
                entry = ttk.Entry(frame, textvariable=entry_var) if entry_var else ttk.Entry(frame)
                entry.pack(fill="x")
                return entry

            self.name_edit = create_input("Nombre:")
            self.phone_edit = create_input("Teléfono:")
            self.email_edit = create_input("Email:")
            self.address_edit = create_input("Dirección:")

            def save_changes():
                prov_name = self.name_edit.get()
                prov_phone = self.phone_edit.get()
                prov_email = self.email_edit.get()
                prov_address = self.address_edit.get()

                if not prov_name or not prov_phone or not prov_email or not prov_address:
                    messagebox.showerror(title="Faltan datos", message="Complete todos los datos solicitados antes de intentar guardar los cambios.")
                    return
                
                updated = provider_dao.update_provider(prov_id, prov_name, prov_phone, prov_email, prov_address)
                if updated:
                    self.tree_proveedores.delete(selection)
                    popup.destroy()
                    self.refresh_right_panel()
                    messagebox.showinfo(title="Datos actualizados", message="Se actualizaron correctamente los datos del proveedor seleccionado.")
                else:
                    messagebox.showerror(title="Error al actualizar datos", message="Ocurrió un error al intentar actualizar los datos del proveedor seleccionado.")
                    return
            
            self.name_edit.insert(0, prov_name)
            self.phone_edit.insert(0, prov_phone)
            self.email_edit.insert(0, prov_email)
            self.address_edit.insert(0, prov_address)

            # command=lambda: save_changes(selection)
            self.add_prov_popup = ttk.Button(form_card, text="Finalizar", style="Accent.TButton", width=20, command=save_changes)
            self.add_prov_popup.pack(pady=20, expand=True)

        
        # Pasamos el ID del prov y SELECTION
        values = (self.tree_proveedores.item(selection, "values")[0],) + selection
        edit_prov_data(values)

    def del_prod_for_prov(self, parent):
        selection = self.tree_prov_prod.selection()
        if len(selection) == 0:
            messagebox.showwarning(title="Seleccione al menos un producto", message="Debe seleccionar al menos un producto para eliminar.", parent=parent)
            return
        if len(selection) < 2:
            confirmation = messagebox.askokcancel(title="Eliminar producto", message="¿Quieres realmente eliminar este producto", parent=parent)
        else:
            confirmation = messagebox.askokcancel(title="Eliminar productos", message=f"¿Quieres realmente eliminar estos {len(selection)} productos?", parent=parent)

        if confirmation:
            products_id = []
            for item in selection:
                values = self.tree_prov_prod.item(item, "values")
                prod_id = int(values[0])
                products_id.append((prod_id,))
            deleted = product_dao.delete_product(products_id)
            if deleted == "IntegrityError":
                messagebox.showerror(title="No se puede borrar el producto", message="Existen registros asociados a este producto. " \
                                    "No se puede eliminar mientras exista un registro de merma o venta. Elimine estos registros primeramente " \
                                    "si quiere eliminar este producto", parent=parent)
                return

            if deleted:
                if len(selection) < 2:
                    messagebox.showinfo(title="Producto eliminado", message="El producto fue eliminado correctamente.", parent=parent)
                else:
                    messagebox.showinfo(title="Productos eliminados", message="Los productos fueron eliminados correctamente.", parent=parent)
            else:
                if len(selection) < 2:
                    messagebox.showerror(title="Error al eliminar producto", message="Ocurrió un error al intentar eliminar el producto de la Base de Datos.", parent=parent)
                    return
                else:
                    messagebox.showerror(title="Error al eliminar productos", message="Ocurrió un error al intentar eliminar los productos de la Base de Datos.", parent=parent)
                    return
                
            # Getting the prov ID
            selection_main_tree = self.tree_proveedores.selection()
            prov_id = int(self.tree_proveedores.item(selection_main_tree, "values")[0])

            # Getting the category
            if self.popup_categories.winfo_exists():
                cat_selection = self.tree_prov_cat.selection()
                category = self.tree_prov_cat.item(cat_selection, "values")[0]
            
            self.refresh_products_popup_prod_prov(prov_id=prov_id, category_general=category)

            # When deleting the last prod for this prov, on close, since there are no categories is not shown but the empty prod tree is shown one more time
            # So let's don't allow this
            # First let's detect if there are more categorias on the categories popup, and the amount of products in this tree
            products_on_tree = [self.tree_prov_prod.item(prod)["values"][0] for prod in self.tree_prov_prod.get_children()]
            if hasattr(self, 'popup_categories') and self.popup_categories.winfo_exists():
                categories_on_tree = [self.tree_prov_cat.item(cat)["values"][0] for cat in self.tree_prov_cat.get_children()]
                if len(categories_on_tree) == 1 and len(products_on_tree) == 0:
                    self.popup_prod_of_prov.protocol("WM_DELETE_WINDOW", self.popup_prod_of_prov.destroy)
                    self.popup_categories.destroy()
            else:
                if len(products_on_tree) == 0:
                    self.popup_prod_of_prov.protocol("WM_DELETE_WINDOW", self.popup_prod_of_prov.destroy)




    def add_product(self, edit_values=None, prov_id=None):
        self.popup_add_prod_prov = tk.Toplevel()
        self.popup_add_prod_prov.title("Agregar producto")
        if prov_id:
            self.popup_add_prod_prov.geometry("250x550+1115+95")
        else:
            self.popup_add_prod_prov.geometry("250x550+765+130")
        self.popup_add_prod_prov.resizable("False", "False")
        self.popup_add_prod_prov.grab_set()
        
        def add(selection=None, prov_id=None):
            nombre = self.nombre_producto_entry.get().capitalize().strip()
            categoria = self.categoria_producto_entry.get().capitalize().strip()
            category_general = self.categoria_general_producto_entry.get().capitalize().strip()
            stock = self.stock_entry.get().strip()
            precio_compra = self.precio_compra_entry.get().strip()
            precio_venta = self.precio_venta_entry.get().strip()
            fecha_prod = self.fecha_produccion_entry.get().strip()
            fecha_venc = self.fecha_vencimiento_entry.get().strip()

            def clean():
                self.nombre_producto_entry.delete(0, tk.END)
                self.categoria_producto_entry.set("")

                categorias_existentes = list(sorted(set(prod[0] for prod in product_dao.get_categories())))
                if '_nueva categoría_' not in categorias_existentes:
                    categorias_existentes.append('_nueva categoría_')
                self.categoria_producto_entry.config(values=categorias_existentes)

                self.categoria_general_producto_entry.set("")
                self.stock_entry.delete(0, tk.END)
                self.precio_compra_entry.delete(0, tk.END)
                self.precio_venta_entry.delete(0, tk.END)
                self.fecha_produccion_entry.delete(0, tk.END)
                self.fecha_vencimiento_entry.delete(0, tk.END)
            
            if not nombre or not categoria or not stock or not precio_compra or not fecha_prod or not fecha_venc: # precio_venta es opcional de momento
                messagebox.showwarning("Campos vacíos", "Por favor, completa todos los campos.", parent=self.popup_add_prod_prov)
                return
            
            try:
                fecha_prod_obj = datetime.strptime(fecha_prod, '%d/%m/%Y')
                fecha_venc_obj = datetime.strptime(fecha_venc, '%d/%m/%Y')
            except:
                messagebox.showerror('Error de fecha', 'El formato de la fecha no es válido.', parent=self.popup_add_prod_prov)
                return

            try:
                stock = int(stock)
            except ValueError:
                messagebox.showerror("Error de formato", "Stock debe ser número entero.", parent=self.popup_add_prod_prov)
                return
            else: 
                if stock <= 0:
                    messagebox.showerror("Valor erróneo", "Stock debe ser un número mayor que 0.", parent=self.popup_add_prod_prov)
                    return
            
            try:
                precio_compra = round(float(precio_compra), 2)
            except ValueError:
                messagebox.showerror("Error de formato", "Precio debe ser un número decimal.", parent=self.popup_add_prod_prov)
                return
            else: 
                if precio_compra <= 0:
                    messagebox.showerror("Valor erróneo", "El precio de compra debe ser un número mayor que 0.", parent=self.popup_add_prod_prov)
                    return

            if precio_venta:
                try:
                    precio_venta = round(float(precio_venta), 2)
                except ValueError:
                    messagebox.showerror("Error de formato", "Precio debe ser un número decimal.", parent=self.popup_add_prod_prov)
                    return
                else: 
                    if precio_venta <= 0:
                        messagebox.showerror("Valor erróneo", "El precio de venta debe ser un número mayor que 0.", parent=self.popup_add_prod_prov)
                        return
                    elif precio_venta <= precio_compra:
                        messagebox.showerror("Valor erróneo", "El precio de venta debe ser mayor que el precio de compra.", parent=self.popup_add_prod_prov)
                        return
            else:
                precio_venta = round(float(0), 2)

            if fecha_prod_obj > datetime.now():
                messagebox.showwarning('Fecha de producción errónea', 'La fecha de producción debe ser anterior a la fecha actual.', parent=self.popup_add_prod_prov)
                return
            elif fecha_prod_obj > fecha_venc_obj:
                messagebox.showwarning('Fecha de producción errónea', 'La fecha de producción debe ser anterior a la fecha de vencimiento.', parent=self.popup_add_prod_prov)
                return
            elif fecha_venc_obj.date() - datetime.now().date() <= timedelta(days=30):
                agregar_prod_prox_venc = messagebox.askokcancel('Producto caduca pronto', 'Estás ingresando un producto que caduca próximamente. ¿Seguro que quieres agregarlo?', parent=self.popup_add_prod_prov)
                if not agregar_prod_prox_venc:
                    return
            elif fecha_venc_obj < datetime.now():
                agregar_prod_venc = messagebox.askokcancel('Producto caducado', 'Estás ingresando un producto caducado. ¿Seguro que quieres agregarlo?', parent=self.popup_add_prod_prov)
                if not agregar_prod_venc:
                    return
            elif categoria == "_nueva categoría_":
                self.check_nueva_categoria()
                return
            elif category_general == "_nueva categoría_":
                self.check_new_general_category()
                return
            
                
            if not prov_id: # To insert in the treeview
                prod_to_tree = (nombre, stock, category_general, categoria, precio_compra, precio_venta, fecha_prod, fecha_venc) # Date is inserted as string in the product treeview
            else: # To insert in DB
                prod_to_db = [(nombre, category_general, categoria, stock, precio_compra, precio_venta, prov_id, fecha_prod_obj, fecha_venc_obj)]
            
            if selection: # Means we are editing the prod data
                if not prov_id:
                    self.prod_treeview.delete(selection) # Let's delete first the prod in the tree IF we are editing the prod (Selection is true if we are editing)
                    self.prod_treeview.insert("", "end", values=prod_to_tree)
                    self.popup_add_prod_prov.destroy()
            
            else: # Means we are adding a new prod, not editing it
                # Check if product with same data already exists (except Stock) in the prod tree and update stock
                if not prov_id: # In this case, products will be added to the botton treeview in the left panel
                    for item in self.prod_treeview.get_children():
                        values = self.prod_treeview.item(item, "values")
                        if (
                            nombre == values[0] and
                            categoria == values[2] and 
                            precio_compra == float(values[3]) and 
                            precio_venta == float(values[4]) and
                            fecha_prod == values[5] and
                            fecha_venc == values[6]
                        ):
                            
                            new_stock = int(values[1]) + stock
                            prod_to_tree = (nombre, new_stock, categoria, precio_compra, precio_venta, fecha_prod, fecha_venc)
                            self.prod_treeview.delete(item)
                            self.prod_treeview.insert("", "end", values=prod_to_tree)
                            clean()
                            return
                    self.prod_treeview.insert("", "end", values=prod_to_tree)
                    clean()
                    
                else: # In this case, we are refering to the treeview in the popup TopLevel window
                    for item in self.tree_prov_prod.get_children():
                        values = self.tree_prov_prod.item(item, "values")
                        if (
                            nombre == values[1] and
                            category_general == values[3] and
                            categoria == values[4] and 
                            precio_compra == round(float(values[5]), 2) and 
                            fecha_prod_obj.date() == datetime.strptime(values[7], "%Y-%m-%d %H:%M:%S").date() and
                            fecha_venc_obj.date() == datetime.strptime(values[8], "%Y-%m-%d %H:%M:%S").date()
                        ):
                            
                            new_stock = int(values[2]) + stock
                            prod_id = product_dao.get_product_by_name(nombre)[0]
                            if not prod_id: # Must be True always in this step, just in case
                                messagebox.showerror(title="Error al consultar ID del producto", message=f"Ocurrió un error tratando de consultar el ID del producto {nombre}.", parent=self.popup_add_prod_prov)
                                return
                            stock_id_prod = [(new_stock, prod_id)]
                            updated = product_dao.update_prod_stock(stock_id_prod)
                            if not updated:
                                messagebox.showerror(title="Error al actualizar stock", message=f"Ocurrió un error tratando de el stock del producto {nombre} con ID {prod_id}.", parent=self.popup_add_prod_prov)
                                return
                            
                            self.refresh_products_popup_prod_prov(prov_id=prov_id, category_general=category_general)
                            clean()
                            return
                    
                    inserted_prod_id = product_dao.insert_products(prod_to_db)
                    if not inserted_prod_id:
                        messagebox.showerror(title="Error al agregar el producto", message="Ocurrió un error al intentar agregar el producto a la base de datos.", parent=self.popup_add_prod_prov)
                        return
                    else:
                        messagebox.showinfo(title="Producto añadido", message="Se añadió correctamente el producto a la base de datos.", parent=self.popup_add_prod_prov)
                        
                        # If the prod belongs to a new general category, let's activate the category popup. Else, just refresh the prod tree in the popup
                        if hasattr(self, 'popup_categories') and self.popup_categories.winfo_exists():
                            categories_on_tree = [self.tree_prov_cat.item(cat)["values"][0] for cat in self.tree_prov_cat.get_children()]
                            category_selected = self.tree_prov_cat.item(self.tree_prov_cat.selection(), "values")[0]
                            
                            if category_general not in categories_on_tree:
                                self.popup_add_prod_prov.destroy()
                                self.on_close_popup_prod_prov(window=self.popup_prod_of_prov, x=self.x, y=self.y, category_to_select=category_general)
                            else:
                                if category_general != category_selected:
                                    self.popup_add_prod_prov.destroy()
                                    self.on_close_popup_prod_prov(window=self.popup_prod_of_prov, x=self.x, y=self.y, category_to_select=category_general)
                                else:
                                    clean()
                                    self.refresh_products_popup_prod_prov(prov_id=prov_id, category_general=category_general)
                        # If it the first product for this provider, categories popup doesn't show
                        else:
                            self.popup_add_prod_prov.destroy()
                            self.on_close_popup_prod_prov(window=self.popup_prod_of_prov, x=self.x, y=self.y, category_to_select=category_general)
                    
        form_card = tk.Frame(self.popup_add_prod_prov, bg="white", relief="flat")
        form_card.pack(expand=True, fill="both")

        def create_input(label_text, entry_var=None):
            frame = tk.Frame(form_card, bg="white")
            frame.pack(fill="x", padx=20, pady=5)
            tk.Label(frame, text=label_text, bg="white", anchor="w").pack(fill="x")
            entry = ttk.Entry(frame, textvariable=entry_var) if entry_var else ttk.Entry(frame)
            entry.pack(fill="x")
            return entry

        self.nombre_producto_entry = create_input("Nombre del Producto:")
        self.stock_entry = create_input("Cantidad en Stock:")
        self.precio_compra_entry = create_input("Precio de compra (€):")
        self.precio_venta_entry = create_input("Precio de venta (€):")
        self.fecha_produccion_entry = create_input("Fecha de Producción (dd/mm/yyyy):")
        self.fecha_vencimiento_entry = create_input("Fecha de Vencimiento (dd/mm/yyyy):")
        
        # Categoría general con combobox
        cat_general_frame = tk.Frame(form_card, bg="white")
        cat_general_frame.pack(fill="x", padx=20, pady=5)
        tk.Label(cat_general_frame, text="Categoría general:", bg="white", anchor="w").pack(fill="x")
        categorias_existentes = list(sorted(set(prod[0] for prod in product_dao.get_general_categories())))
        if '_nueva categoría_' not in categorias_existentes:
            categorias_existentes.append('_nueva categoría_')
        self.categoria_general_producto_entry = ttk.Combobox(cat_general_frame, values=categorias_existentes, state="readonly")
        self.categoria_general_producto_entry.pack(fill="x")
        self.categoria_general_producto_entry.bind("<<ComboboxSelected>>", self.check_new_general_category)

        # Categoría con combobox
        cat_frame = tk.Frame(form_card, bg="white")
        cat_frame.pack(fill="x", padx=20, pady=5)
        tk.Label(cat_frame, text="Categoría:", bg="white", anchor="w").pack(fill="x")
        categorias_existentes = list(sorted(set(prod[0] for prod in product_dao.get_categories())))
        if '_nueva categoría_' not in categorias_existentes:
            categorias_existentes.append('_nueva categoría_')
        self.categoria_producto_entry = ttk.Combobox(cat_frame, values=categorias_existentes, state="readonly")
        self.categoria_producto_entry.pack(fill="x")
        self.categoria_producto_entry.bind("<<ComboboxSelected>>", self.check_nueva_categoria)

        self.add_prod_popup = ttk.Button(form_card, text="Añadir", style="Accent.TButton", width=20)
        self.add_prod_popup.pack(pady=20, expand=True)

        if not prov_id:
            if edit_values:
                product, stock, category_general, category, precio_compra, precio_venta, fecha_prod, fecha_venc, selection = edit_values
                self.nombre_producto_entry.insert(0, product)
                self.stock_entry.insert(0, stock)
                self.precio_compra_entry.insert(0, precio_compra)
                self.precio_venta_entry.insert(0, precio_venta)
                self.fecha_produccion_entry.insert(0, fecha_prod)
                self.fecha_vencimiento_entry.insert(0, fecha_venc)
                self.categoria_producto_entry.set(category)
                self.categoria_general_producto_entry.set(category_general)
            else:
                selection = None

            if selection: # if we are editing the prod data
                self.add_prod_popup.config(command=lambda: add(selection=selection), text="Finalizar")
            else: # Just adding a new prod
                self.add_prod_popup.config(command=add, text="Añadir")
        
        else:
            if not edit_values:
                selection = None
                prov_id = int(prov_id)
            
            if not selection: # if we are NOT editing the prod data, just adding a new product
               self.add_prod_popup.config(command=lambda: add(prov_id=prov_id), text="Añadir")

    def check_nueva_categoria(self, event=None):
        if self.categoria_producto_entry.get() == "_nueva categoría_":
            nueva_cat = simpledialog.askstring("Nueva Categoría", "Introduce el nombre de la nueva categoría:")

            if nueva_cat:
                self.categoria_producto_entry.set(nueva_cat)


    def check_new_general_category(self, event=None):
        if self.categoria_general_producto_entry.get() == '_nueva categoría_':
            nueva_cat = simpledialog.askstring("Nueva Categoría", "Introduce el nombre de la nueva categoría general:")

            if nueva_cat:
                self.categoria_general_producto_entry.set(nueva_cat)
        
        categorias_existentes = list(sorted(set(prod[0] for prod in product_dao.get_categories(self.categoria_general_producto_entry.get().capitalize().strip()))))
        if "_nueva categoría_" not in categorias_existentes:
            categorias_existentes.append("_nueva categoría_")
        
        self.categoria_producto_entry.set("")
        self.categoria_producto_entry.config(values=categorias_existentes)
                

    def edit_prod(self, event=None):
        selection = self.prod_treeview.selection()
        if not selection or len(selection) > 1:
            messagebox.showerror(title="Sin selección", message="Debe seleccionar exactamente un producto para editarlo.")
            return

        values = self.prod_treeview.item(selection, "values") + selection
        print(values)
        self.add_product(edit_values=values)
        


    