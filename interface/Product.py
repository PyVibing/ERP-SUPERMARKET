import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
from config.config import *
from config.services import product_dao, provider_dao

class Product(tk.Frame):
    def __init__(self, parent, employee_id):
        self.productos_main_frame = parent
        self.employee_id = employee_id
        self.build_interface()
        self.ask_delete_zero_stock = True

    def build_interface(self):
        # ----- HEADER -----
        header = tk.Frame(self.productos_main_frame, bg="#2b6cb0", height=60)
        header.pack(fill="x")
        tk.Label(header, text="Gestión de Productos", bg="#2b6cb0", fg="white", font=("Segoe UI", 16, "bold")).pack(pady=15)

        # ----- MAIN BODY -----
        main = tk.Frame(self.productos_main_frame, bg="#edf2f7")
        main.pack(fill="both", expand=True, padx=20, pady=20)

        # ----- FORM CARD (Left side) -----
        form_card = tk.Frame(main, bg="white", relief="flat")
        form_card.place(x=20, y=20, width=400, height=550)

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
        self.precio_venta_entry = create_input("Precio de venta (€) (opcional):")
        self.fecha_produccion_entry = create_input("Fecha de Producción (dd/mm/yyyy):")
        self.fecha_vencimiento_entry = create_input("Fecha de Vencimiento (dd/mm/yyyy):")

        # Categoria general con Combobox
        cat_frame = tk.Frame(form_card, bg="white")
        cat_frame.pack(fill="x", padx=20, pady=5)
        tk.Label(cat_frame, text="Categoría general:", bg="white", anchor="w").pack(fill="x")
        categorias_existentes = list(sorted(set(prod[0] for prod in product_dao.get_general_categories())))
        if '_nueva categoría_' not in categorias_existentes:
            categorias_existentes.append('_nueva categoría_')
        self.categoria_general_entry = ttk.Combobox(cat_frame, values=categorias_existentes, state="readonly")
        self.categoria_general_entry.pack(fill="x")
        self.categoria_general_entry.bind("<<ComboboxSelected>>", self.check_new_general_category)

        # Categoría con combobox
        cat_frame = tk.Frame(form_card, bg="white")
        cat_frame.pack(fill="x", padx=20, pady=5)
        tk.Label(cat_frame, text="Categoría:", bg="white", anchor="w").pack(fill="x")
        categorias_existentes = list(sorted(set(prod[2] for prod in product_dao.get_all_products())))
        if '_nueva categoría_' not in categorias_existentes:
            categorias_existentes.append('_nueva categoría_')
        self.categoria_producto_entry = ttk.Combobox(cat_frame, values=categorias_existentes, state="readonly")
        self.categoria_producto_entry.pack(fill="x")
        self.categoria_producto_entry.bind("<<ComboboxSelected>>", self.check_nueva_categoria)

        # Proveedor del producto
        prov_frame = tk.Frame(form_card, bg="white")
        prov_frame.pack(fill="x", padx=20, pady=5)
        tk.Label(prov_frame, text="Proveedor:", bg="white", anchor="w").pack(fill="x")
        proveedores_existentes = list(set(item[1] for item in provider_dao.get_all_providers()))
        if '_nuevo proveedor_' not in proveedores_existentes:
            proveedores_existentes.append('_nuevo proveedor_')
        self.proveedor_producto_entry = ttk.Combobox(prov_frame, values=proveedores_existentes, state="readonly")
        self.proveedor_producto_entry.pack(fill="x")
        self.proveedor_producto_entry.bind("<<ComboboxSelected>>", self.check_nuevo_proveedor)

        # Botones de acción
        btn_frame = tk.Frame(main, bg="#edf2f7")
        btn_frame.place(x=20, y=570, width=400, height=50)

        style = ttk.Style()
        style.configure("Accent.TButton", foreground="black", background="#2b6cb0")
        style.map("Accent.TButton",
                 background=[("active", "#2c5282")],
                 foreground=[("disabled", "#aaa")])
        
        style.configure("Cancel.TButton", background="#e53e3e", foreground="black")
        style.map("Cancel.TButton", background=[("active", "#c53030")])
        
        self.add_prod_button = ttk.Button(btn_frame, text="➕ Agregar", style= 'Accent.TButton', width=15, command=self.add_product)
        self.add_prod_button.pack(side='left', pady=10, expand=True)
        self.edit_prod_button = ttk.Button(btn_frame, text="☰ Editar", style= 'Accent.TButton', width=15, command=self.edit_prod)
        self.edit_prod_button.pack(side='left', padx=(5, 0), pady=10, expand=True)
        self.delete_prod_button = ttk.Button(btn_frame, text="✖️ Eliminar", style="Cancel.TButton", width=15, command=self.eliminar_producto)
        self.delete_prod_button.pack(side="left", padx=(5, 0), pady=10, expand=True)
        self.declare_lost_prod_button = ttk.Button(btn_frame, text="➖ Merma", style="Cancel.TButton", width=15, command=self.declarar_merma)
        self.declare_lost_prod_button.pack(side="left", padx=(5, 0), pady=10, expand=True)
        
        
        # ----- TABLE CARD (Right side) -----
        table_card = tk.Frame(main, bg="white", relief="flat")
        table_card.place(x=440, y=20, width=850, height=600)

        # Filtro superior
        top_filter_frame = tk.Frame(table_card, bg="white")
        top_filter_frame.pack(fill="x", pady=(10, 5), padx=10)

        tk.Label(top_filter_frame, text="🔍 Buscar:", bg="white").pack(side="left")
        self.buscar_entry = tk.Entry(top_filter_frame)
        self.buscar_entry.pack(side="left", padx=5)

        tk.Label(top_filter_frame, text="📂 Categoría:", bg="white").pack(side="left", padx=(10, 0))
        self.filtrar_categoria = ttk.Combobox(top_filter_frame, state="readonly")
        self.filtrar_categoria.set("Todos")
        self.filtrar_categoria.pack(side="left", padx=5)

        tk.Button(top_filter_frame, text="Filtrar", bg="#2b6cb0", fg="white", command=self.filter_prod).pack(side="left", padx=10)
        tk.Button(top_filter_frame, text="Merma", bg="#2b6cb0", fg="white", command=self.show_lost_prod).pack(side="left", padx=0)

        # Tabla de productos
        columnas_y_ancho = {
            "ID": 20,
            "Nombre": 100, 
            "Stock": 30,
            "Cat. General": 60,
            "Categoría": 60,
            "Proveedor": 60,
            "€ Compra": 40,
            "€ Venta": 40,
            "F. Prod.": 60, 
            "F. Venc.": 60
        }

        self.tree_productos = ttk.Treeview(table_card, columns=[key for key in columnas_y_ancho.keys()])
        self.tree_productos.column("#0", width=0, stretch=tk.NO)
        for col in columnas_y_ancho.keys():
            self.tree_productos.heading(col, text=col)
            self.tree_productos.column(col, anchor="center", width=columnas_y_ancho[col])
        self.tree_productos.pack(fill="both", expand=True, padx=0, pady=10)
        self.tree_productos.bind("<Double-1>", self.edit_prod)


# ------------------------------------------ METODOS AUXILIARES ------------------------------------------ #
    def refresh_interface(self):
        self.refresh_left_panel()
        self.refresh_right_panel()

    def refresh_left_panel(self):
        self.nombre_producto_entry.delete(0, tk.END)
        self.stock_entry.delete(0, tk.END)
        self.precio_compra_entry.delete(0, tk.END)
        self.precio_venta_entry.delete(0, tk.END)
        self.fecha_produccion_entry.delete(0, tk.END)
        self.fecha_vencimiento_entry.delete(0, tk.END)
        self.get_categories()
        self.categoria_producto_entry.set("")
        self.categoria_general_entry.set("")
        self.get_providers()
        self.proveedor_producto_entry.set("")
        self.add_prod_button.config(text="➕ Agregar", command=self.add_product)

    def refresh_right_panel(self):
        # Limpiar el treeview actual
        for item in self.tree_productos.get_children():
            self.tree_productos.delete(item)

        # Insertar todos los productos
        for producto in product_dao.get_all_products():
            id, product, category_general, category, stock, buy_price, sell_price, provider_id, prod_date, exp_date = producto
            
            prov = provider_dao.get_provider_for_id(provider_id)
            if not prov:
                messagebox.showinfo(title="Error al intentar obtener el proveedor", message='No se pudo obtener el nombre del proveedor con el ID proporcionado.')
            else:
                self.tree_productos.insert('', 'end', values=(id, product, stock, category_general, category, prov, buy_price, sell_price, prod_date, exp_date))
        
        # Actualizar filtro categorias
        filter_categorias = list(set([cat[0] for cat in product_dao.get_categories()])) + ["Todos"]
        self.filtrar_categoria.config(values=filter_categorias)


        # Eliminar productos con 0 existencias
        zero_stock_id = []
        for item_id in self.tree_productos.get_children():
            stock = self.tree_productos.item(item_id)["values"][2]
            prod_id = self.tree_productos.item(item_id)["values"][0]
            if int(stock) == 0:
                zero_stock_id.append((prod_id,))
        
        if len(zero_stock_id) > 0 and self.ask_delete_zero_stock:
            confirmacion = messagebox.askyesnocancel(title="Productos con 0 existencias", message=f"Tienes {len(zero_stock_id)} producto(s) con existencia 0. ¿Quieres eliminarlo(s)?")
            if confirmacion:
                deleted = product_dao.delete_product(zero_stock_id)
                if deleted == "IntegrityError":
                    if len(zero_stock_id) < 2:
                        messagebox.showerror(title="No se puede borrar el producto", message="El producto tiene registros asociados en otras tablas y no se puede eliminar. " \
                        "Para eliminar este producto, elimine los registros en otras tablas. ")
                        return
                    else:
                        messagebox.showerror(title="No se puede borrar el producto", 
                                             message="Al menos uno de estos productos tiene registros asociados en otras tablas y no se puede eliminar. " \
                                            "Intente eliminarlos uno a uno para identificar el que no puede ser eliminado. Si luego quiere eliminarlo igualmente," \
                                            "deberá borrar primeramente los registros de merma o ventas asociados a este.")
                        return
                if deleted:
                    self.refresh_right_panel()
                    if len(zero_stock_id) < 2:
                        messagebox.showinfo(title="Producto eliminado", message="El producto con 0 existencias fue eliminado correctamente.")
                    else:
                        messagebox.showinfo(title="Productos eliminados", message="Los productos con 0 existencias fueron eliminados correctamente.")
            else:
                self.ask_delete_zero_stock = False

    def check_nueva_categoria(self, event=None):
        if self.categoria_producto_entry.get() == '_nueva categoría_':
            nueva_cat = simpledialog.askstring("Nueva Categoría", "Introduce el nombre de la nueva categoría:")

            if nueva_cat:
                self.categoria_producto_entry.set(nueva_cat)

    def check_new_general_category(self, event=None):
        if self.categoria_general_entry.get() == '_nueva categoría_':
            nueva_cat = simpledialog.askstring("Nueva Categoría", "Introduce el nombre de la nueva categoría general:")

            if nueva_cat:
                self.categoria_general_entry.set(nueva_cat)
        self.get_categories()
    
    def get_categories(self):
        category_general = self.categoria_general_entry.get().capitalize()
        categorias_existentes = list(sorted(set(prod[0] for prod in product_dao.get_categories(category_general))))
        if '_nueva categoría_' not in categorias_existentes:
            categorias_existentes.append('_nueva categoría_')
        self.categoria_producto_entry.config(values=categorias_existentes)

    def get_categories_general(self):
        categorias_existentes_general = list(sorted(set(prod[0] for prod in product_dao.get_general_categories())))
        if '_nueva categoría_' not in categorias_existentes_general:
            categorias_existentes_general.append('_nueva categoría_')
        self.categoria_general_entry.config(values=categorias_existentes_general)
    
    def get_providers(self):
        proveedores_existentes = list(set(item[1] for item in provider_dao.get_all_providers()))
        if '_nuevo proveedor_' not in proveedores_existentes:
            proveedores_existentes.append('_nuevo proveedor_')
        self.proveedor_producto_entry.config(values=proveedores_existentes)
        

    def check_nuevo_proveedor(self, event=None):
        if self.proveedor_producto_entry.get() == '_nuevo proveedor_':
            # Crear ventana emergente
            popup = tk.Toplevel()
            popup.title("Nuevo Proveedor")
            popup.geometry("300x300")
            popup.grab_set()

            campos = {
                "Prov_name": tk.StringVar(),
                "Phone": tk.StringVar(),
                "Email": tk.StringVar(),
                "Address": tk.StringVar()
            }

            form_card = tk.Frame(popup, bg="white", relief="flat", pady=15)
            form_card.pack(expand=True, fill="both")

            style = ttk.Style()
            for i, (label_text, var) in enumerate(campos.items()):
                ttk.Label(form_card, text=label_text, style="White.TLabel").grid(row=i, column=0, padx=10, pady=15, sticky="e")
                tk.Entry(form_card, textvariable=var).grid(row=i, column=1, padx=10, pady=15)

            # Función para guardar
            def guardar_proveedor():
                provider = campos["Prov_name"].get().title()
                phone = campos["Phone"].get().title()
                email = campos["Email"].get().title()
                address = campos["Address"].get().title()
                
                if not provider or not phone or not email or not address:
                    messagebox.showerror(title='Faltan datos en el formulario', message='Por favor, completa los datos que faltan.',
                                         parent=popup)
                    return
                else:
                    providers = list(set([item[1] for item in provider_dao.get_all_providers()]))
                    if provider not in providers:
                        provider_dao.insert_provider(provider, phone, email, address)
                        self.filtrar_categoria['values'] = list(set([item[1] for item in provider_dao.get_all_providers()]))
                        self.proveedor_producto_entry['values'] = list(set([item[0] for item in product_dao.get_general_categories()]))
                        popup.destroy()
                        
                    else:
                        messagebox.showinfo(title='Proveedor ya existe', 
                                            message='Ya existe un proveedor con ese nombre. No es necesario volver a añadirlo.',
                                            parent=popup)
                        popup.destroy()
                        
                    self.proveedor_producto_entry.set(provider)
                
            # Botón Guardar
            ttk.Button(form_card, text="Guardar", command=guardar_proveedor, style="Accent.TButton").grid(
                row=len(campos), columnspan=2, pady=20, padx=110)
    
    def show_lost_prod(self):
        products_in_db = product_dao.get_all_lost_products()
        if len(products_in_db) == 0:
            messagebox.showinfo(title="No hay registros para mostrar", message="No hay ningún registro de merma en la base de datos.")
            return

        # Crear ventana emergente
        popup = tk.Toplevel()
        popup.title("Merma registrada")
        popup.geometry("1200x600")
        popup.grab_set()
        
        columnas_y_ancho = {
            "ID Merma": 5,
            "ID Producto": 5,
            "Producto": 120, 
            "Cantidad": 5,
            "Precio compra": 10,
            "Total": 10,
            "Concepto": 120,
            "Fecha": 20,
            "ID Empleado": 5,
            "Nombre Empleado": 30
        }
        self.lost_products_tree = ttk.Treeview(popup, columns=[key for key in columnas_y_ancho.keys()])
        self.lost_products_tree.column("#0", width=0, stretch=tk.NO)
        for col in columnas_y_ancho.keys():
            self.lost_products_tree.heading(col, text=col)
            self.lost_products_tree.column(col, anchor="center", width=columnas_y_ancho[col])
        self.lost_products_tree.pack(fill="both", expand=True, padx=0, pady=5)
        
        # Show lost products
        # Limpiar el treeview actual
        for item in self.lost_products_tree.get_children():
            self.lost_products_tree.delete(item)
        
        # Insertar todos los productos
        for producto in products_in_db:
            id_lost_prod, id_prod, product, quantity, buy_price, total, motive, date, employee_id, employee_name = producto
            self.lost_products_tree.insert('', 'end', values=(id_lost_prod, id_prod, product, quantity, buy_price, total, motive, date, employee_id, employee_name))
        
        def delete_lost_product():
            id_rows = self.lost_products_tree.selection()
            if not id_rows:
                messagebox.showerror(title="Registro no seleccionado", message="Debe seleccionar un registro de merma para eliminarlo.")
                return
            
            if len(id_rows) < 2:
                confirmation = messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres eliminar este registro de merma?")
            else:
                confirmation = messagebox.askyesno("Confirmar", f"¿Estás seguro de que quieres eliminar estos {len(id_rows)} registros de merma?")

            if confirmation:
                lost_prod_id = []
                for row in id_rows:
                    item = self.lost_products_tree.item(row)
                    values = item["values"]
                    lost_prod_id.append(values[0])
                deleted = product_dao.delete_lost_product(lost_prod_id)
                if deleted == "IntegrityError":
                    messagebox.showerror(title="Error al eliminar el registro", message="Ocurrió un IntegrityError")
                    return
                if not deleted:
                    messagebox.showerror(title="Error al eliminar el registro", message="Ocurrió una excepción al intentar borrar el registro")
                    return
                if deleted:
                    popup.destroy()
                    if len(lost_prod_id) < 2:
                        messagebox.showinfo(title="Registro eliminado", message=f"El registro con ID {lost_prod_id[0]} fue eliminado correctamente.")
                    else:
                        messagebox.showinfo(title="Registros eliminados", message=f"Los registros con ID {lost_prod_id[::]} fueron eliminados correctamente.")   
                    
                    if len(products_in_db) != len(lost_prod_id):
                        self.show_lost_prod()
        
        ttk.Style()
        ttk.Button(popup, text="Eliminar merma", command=delete_lost_product, style="Accent.TButton").pack(pady=(0, 5))


    def add_product(self, prod_id=None):
        nombre = self.nombre_producto_entry.get().capitalize().strip()
        categoria = self.categoria_producto_entry.get().capitalize().strip()
        stock = self.stock_entry.get().strip()
        precio_compra = self.precio_compra_entry.get().strip()
        precio_venta = self.precio_venta_entry.get().strip()
        fecha_prod = self.fecha_produccion_entry.get().strip()
        fecha_venc = self.fecha_vencimiento_entry.get().strip()
        prov = self.proveedor_producto_entry.get().strip()
        category_general = self.categoria_general_entry.get().capitalize()

        if not nombre or not categoria or not category_general or not stock or not precio_compra or not fecha_prod or not fecha_venc or not prov: # precio_venta es opcional de momento
            messagebox.showwarning("Campos vacíos", "Por favor, completa todos los campos.")
            return
        
        try:
            fecha_prod_obj = datetime.strptime(fecha_prod, '%d/%m/%Y')
            fecha_venc_obj = datetime.strptime(fecha_venc, '%d/%m/%Y')
        except:
            messagebox.showerror('Error de fecha', 'El formato de la fecha no es válido.')
            return

        try:
            stock = int(stock)
        except ValueError:
            messagebox.showerror("Error de formato", "Stock debe ser número entero.")
            return
        else: 
            if stock <= 0:
                messagebox.showerror("Valor erróneo", "Stock debe ser un número mayor que 0.")
                return

        try:
            precio_compra = round(float(precio_compra), 2)
        except ValueError:
            messagebox.showerror("Error de formato", "Precio debe ser un número decimal.")
            return
        else: 
            if precio_compra <= 0:
                messagebox.showerror("Valor erróneo", "El precio de compra debe ser un número mayor que 0.")
                return

        if precio_venta:
            try:
                precio_venta = round(float(precio_venta), 2)
            except ValueError:
                messagebox.showerror("Error de formato", "Precio debe ser un número decimal.")
                return
            else: 
                if precio_venta <= 0:
                    messagebox.showerror("Valor erróneo", "El precio de venta debe ser un número mayor que 0.")
                    return
                elif precio_venta <= precio_compra:
                    messagebox.showerror("Valor erróneo", "El precio de venta debe ser mayor que el precio de compra.")
                    return
        else:
            precio_venta = round(float(0), 2)

        if fecha_prod_obj > datetime.now():
            messagebox.showwarning('Fecha de producción errónea', 'La fecha de producción debe ser anterior a la fecha actual.')
            return
        elif fecha_prod_obj > fecha_venc_obj:
            messagebox.showwarning('Fecha de producción errónea', 'La fecha de producción debe ser anterior a la fecha de vencimiento.')
            return
        elif fecha_venc_obj.date() - datetime.now().date() <= timedelta(days=30):
            agregar_prod_prox_venc = messagebox.askokcancel('Producto caduca pronto', 'Estás ingresando un producto que caduca próximamente. ¿Seguro que quieres agregarlo?')
            if not agregar_prod_prox_venc:
                return
        elif fecha_venc_obj < datetime.now():
            agregar_prod_venc = messagebox.askokcancel('Producto caducado', 'Estás ingresando un producto caducado. ¿Seguro que quieres agregarlo?')
            if not agregar_prod_venc:
                return
        elif categoria == "_nueva categoría_":
            self.check_nueva_categoria()
            return
        elif prov == "_nuevo proveedor_":
            self.check_nuevo_proveedor()
            return
        elif category_general == "_nueva categoría_":
            self.check_new_general_category()
            return
            
        prov_id = provider_dao.get_prov_id(prov.title())
        if not prov_id:
            messagebox.showerror(title="Error al intentar obtener el ID", message='No se pudo obtener el ID del proveedor.')
            return
        else:
            if not prod_id:
            # Check if product with same data already exists (except Stock).The function returns its ID and stock. prod_id is only true when editing the prod data
                product_exist = product_dao.check_if_product_exist(nombre, categoria, precio_compra, precio_venta, prov_id, category_general, fecha_prod_obj, fecha_venc_obj)
                
                if product_exist[0]:
                    add_to_old = messagebox.askyesno(title="Existe producto similar", 
                                                    message="Ya existe un producto con estos mismos datos. ¿Desea añadir el stock al producto existente? " \
                                                    "Diga NO para regresar y editar los datos del producto.")
                    if not add_to_old:
                        return
                    
                    prod_id, stock_prod = product_exist
                    new_stock = stock_prod + stock
                    
                    stock_updated = product_dao.add_product_stock(prod_id, new_stock)
                    if stock_updated:
                        self.refresh_right_panel()
                        self.refresh_left_panel()  
                        messagebox.showinfo(title="Cantidad añadida correctamente", 
                                            message=f"Se añadió correctamente la cantidad especificada al producto existente con ID {prod_id}")
                        return
                    else:
                        messagebox.showerror(title="Error al actualizar stock", 
                                            message=f"Ocurrió un error al intentar añadir la cantidad especificada al producto existente con ID {prod_id}")
                        return
            
            if not prod_id:
                inserted_prod = product_dao.insert_product(nombre, category_general, categoria, stock, precio_compra, precio_venta, prov_id, fecha_prod_obj, fecha_venc_obj)
                estado = ["añadido", "añadir"]
            else:
                inserted_prod = product_dao.update_prod_data((nombre, category_general, categoria, stock, precio_compra, precio_venta, prov_id, fecha_prod_obj, fecha_venc_obj), prod_id)
                estado = ["actualizado", "actualizar"]

            if inserted_prod:
                self.refresh_interface()
                messagebox.showinfo(title=f"Producto {estado[0]}", message=f"El producto fue {estado[0]} correctamente en la base de datos.")
                self.filtrar_categoria.config(values=product_dao.get_categories() + ["Todos"])
            else:
                messagebox.showerror(title=f"Error al intentar {estado[1]} el producto", 
                                    message=f"No se pudo {estado[1]} el producto en la Base de Datos. Ocurrió un error inesperado.")
                return
            
    def filter_prod(self):
        filtro_nombre = self.buscar_entry.get().lower()
        filtro_categoria = self.filtrar_categoria.get()

        for item in self.tree_productos.get_children():
            self.tree_productos.delete(item)

        for prod in product_dao.get_all_products():
            id, product, category_general, category, stock, buy_price, sell_price, provider_id, prod_date, exp_date = prod
            
            prov = provider_dao.get_provider_for_id(provider_id)
            if not prov:
                messagebox.showinfo(title="Error al intentar obtener el proveedor", message='No se pudo obtener el nombre del proveedor con el ID proporcionado.')
                return
            else:
                if (filtro_categoria == "Todos" or category == filtro_categoria) and filtro_nombre in product.lower():
                    self.tree_productos.insert('', 'end', values=(id, product, stock, category_general, category, prov, buy_price, sell_price, prod_date, exp_date))
        
    def eliminar_producto(self):
        id_rows = self.tree_productos.selection()
        if not id_rows:
            messagebox.showwarning("Nada seleccionado", "Selecciona un producto para eliminar.")
            return
        
        if len(id_rows) < 2:
            confirmacion = messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres eliminar este producto?")
        else:
            confirmacion = messagebox.askyesno("Confirmar", f"¿Estás seguro de que quieres eliminar estos {len(id_rows)} productos?")

        if confirmacion:
            products_id = []
            for row in id_rows:
                item = self.tree_productos.item(row)
                values = item["values"]
                products_id.append((values[0],))

            deleted = product_dao.delete_product(products_id)
            if deleted == "IntegrityError":
                messagebox.showerror(title="No se puede borrar el producto", message="Existen registros asociados a este producto. " \
                                    "No se puede eliminar mientras exista un registro de merma o venta. Elimine estos registros primeramente " \
                                    "si quiere eliminar este producto")
                return
            
            if deleted:
                self.refresh_interface()
                if len(products_id) < 2:
                    messagebox.showinfo(title="Producto eliminado", message="Se eliminó el producto correctamente.")
                else:
                    messagebox.showinfo(title="Productos eliminados", message=f"Se eliminaron correctamente los {len(products_id)} productos seleccionados.")
            else:
                messagebox.showerror(title="Error al eliminar", message='No se pudo completar la operación de eliminación.')

    def declarar_merma(self):
        id_row = self.tree_productos.selection()
        if not id_row:
            messagebox.showwarning("Nada seleccionado", "Selecciona un producto para dar de baja.")
            return
        
        if len(id_row) > 1:
            messagebox.showerror(title="Demasiados productos", message="Solo puedes declarar merma de un producto a la vez.")
            return
        
        item = self.tree_productos.item(id_row[0])
        prod_id = int(item["values"][0])
        prod_name = item["values"][1]
        stock = int(item["values"][2])
        

        # Ventana emergente para pedir datos de merma
        decrease_window = tk.Toplevel(self.productos_main_frame)
        decrease_window.title("Declarar Merma")
        decrease_window.geometry("300x270")
        decrease_window.grab_set()  # bloquea la ventana principal

        style = ttk.Style()
        form_card = ttk.Frame(decrease_window, style="White.TFrame")
        form_card.pack(fill="both", expand=True)

        ttk.Label(form_card, text=f"Producto: {prod_name}", font=("Segoe UI", 12), style="White.TLabel").pack(pady=(10, 5))
        ttk.Label(form_card, text=f"Stock actual: {stock}", style="White.TLabel").pack(pady=(0, 10))

        ttk.Label(form_card, text="Cantidad a dar de baja:", style="White.TLabel").pack(pady=(10, 0))
        decrease_stock_entry = tk.Entry(form_card)
        decrease_stock_entry.pack()

        ttk.Label(form_card, text="Motivo de la merma:", style="White.TLabel").pack(pady=(10, 0))
        motive_entry = tk.Entry(form_card)
        motive_entry.pack()

        def confirmar_merma():
            decrease_quantity = decrease_stock_entry.get()
            motive = motive_entry.get()
            if not decrease_quantity or not motive:
                messagebox.showwarning(title="Complete los campos solicitados", message="Debe completar toda la información requerida.",
                                       parent=decrease_window)
                return
            try:
                try:
                    decrease_quantity = int(decrease_stock_entry.get())
                except ValueError:
                    messagebox.showerror(title="Error en los datos", message="Introduzca un número válido.", parent=decrease_window)
                    
                motive = motive_entry.get().strip()

                if decrease_quantity <= 0:
                    raise ValueError("La cantidad debe ser mayor que cero.")
                elif decrease_quantity > stock:
                    raise ValueError("No puedes dar de baja más unidades de las disponibles.")
                
            except ValueError as e:
                messagebox.showerror(title="Error en los datos", message=str(e), parent=decrease_window)
                return
            
            else:
                # Update DDBB
                new_stock = stock - decrease_quantity
                values_to_update = [(new_stock, prod_id)]
                decrease_in_bd = product_dao.update_prod_stock(values_to_update)
                if decrease_in_bd:
                    employee_id = self.employee_id
                    add_to_lost_products_table = product_dao.declare_lost_product(prod_id, decrease_quantity, motive, employee_id)
                    if add_to_lost_products_table:
                        messagebox.showinfo("Merma registrada", f"{decrease_quantity} unidades de '{prod_name}' dadas de baja por: {motive}",
                                            parent=decrease_window)
                        decrease_window.destroy()
                        self.refresh_right_panel()
                    else:
                        messagebox.showerror(title="Error al intentar registrar la merma", 
                                             message="Ocurrió un error intentando registrar la merma en la Base de Datos.",
                                             parent=decrease_window)
                        return
                        
                        
                else:
                    messagebox.showerror(title="Error al intentar actualizar datos", 
                                         message="Ocurrió un error al intentar actualizar la información del producto",
                                         parent=decrease_window)
                    return
                    
        ttk.Button(form_card, text="Confirmar", command=confirmar_merma, style="Accent.TButton").pack(pady=30)

    def edit_prod(self, event=None): # Se activa con doble click sobre el producto en el treeview o con el boton Editar
        fila_id = self.tree_productos.selection()
        if len(fila_id) > 1 or not fila_id:
            messagebox.showerror(title="Seleccione un producto", message="Debe seleccionar exactamente un producto para editarlo.")
            return

        values = self.tree_productos.item(fila_id, "values")
        prod_id = values[0]
        prod_name = values[1]
        stock = values[2]
        category_general = values[3]
        category = values[4]
        prov = values[5]
        buy_price = values[6]
        sell_price = values[7]
        prod_date = values[8]
        exp_date = values[9]
        
        prod_date = prod_date.split()[0].split("-")
        prod_date = prod_date[2] + "/" + prod_date[1] + "/" + prod_date[0]

        exp_date = exp_date.split()[0].split("-")
        exp_date = exp_date[2] + "/" + exp_date[1] + "/" + exp_date[0]
        
        # Let's change the text and command for the Add Product buttton
        self.add_prod_button.config(text="✔️ Guardar Cambios", command=lambda: self.add_product(prod_id))

        # Send the values to the left panel. First, let's delete any possible text on the left panel
        def clean():
            self.nombre_producto_entry.delete(0, "end")
            self.stock_entry.delete(0, "end")
            self.precio_compra_entry.delete(0, "end")
            self.precio_venta_entry.delete(0, "end")
            self.fecha_produccion_entry.delete(0, "end")
            self.fecha_vencimiento_entry.delete(0, "end")
            self.categoria_general_entry.set("")
            self.categoria_producto_entry.set("")
            self.proveedor_producto_entry.set("")

        clean()
        self.nombre_producto_entry.insert(0, prod_name)
        self.stock_entry.insert(0, stock)
        self.precio_compra_entry.insert(0, buy_price)
        if float(sell_price) > 0:
            self.precio_venta_entry.insert(0, sell_price)
        self.fecha_produccion_entry.insert(0, prod_date)
        self.fecha_vencimiento_entry.insert(0, exp_date)
        self.categoria_general_entry.set(category_general)
        self.categoria_producto_entry.set(category)
        self.proveedor_producto_entry.set(prov)        

