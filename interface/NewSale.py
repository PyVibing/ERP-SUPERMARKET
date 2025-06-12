import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from config.config import *
from config.services import sales_dao, product_dao, users_dao


class NewSale(tk.Frame): #DUPLICAR LUEGO PARA *** NUEVA COMPRA ***
    def __init__(self, parent, employee_id):
        self.sell = parent
        self.employee_id = employee_id
        self.build_interface()
        
    def build_interface(self):
        # ----- HEADER -----
        header = tk.Frame(self.sell, bg="#2b6cb0", height=60)
        header.pack(fill="x")
        tk.Label(header, text="🧾 Registrar Nueva Venta", bg="#2b6cb0", fg="white", font=("Segoe UI", 16, "bold")).pack(pady=15)

        # ----- MAIN BODY -----
        main_area = tk.Frame(self.sell, bg="#edf2f7")
        main_area.pack(fill="both", expand=True, padx=20, pady=20)

        # ----- FORM CARD (Left side) -----
        left = tk.Frame(main_area, bg="white", relief="flat", padx=15, pady=15)
        left.place(relx=0.02, rely=0.02, relwidth=0.40, relheight=0.82)


        # FORMULARIO
        tk.Label(left, text="Filtrar por Categoría:", bg="white").pack(anchor="w")
        categorias = [cat for cat in product_dao.get_categories()]
        self.filtrar_categoria_venta = ttk.Combobox(left, values=["Todos"] + categorias, state="readonly")
        self.filtrar_categoria_venta.set("Todos")
        self.filtrar_categoria_venta.pack(fill="x", pady=5)
        self.filtrar_categoria_venta.bind("<<ComboboxSelected>>", self.update_prod_by_cat)

        tk.Label(left, text="Producto:", bg="white").pack(anchor="w")
        self.product_entry = ttk.Combobox(left, values=[f"{prod[0]} - {prod[1]}" for prod in sorted(product_dao.get_all_products_with_stock(), key=lambda x: x[1])], 
                                          state="readonly")
        self.product_entry.pack(fill="x", pady=5)
        self.product_entry.bind("<<ComboboxSelected>>", self.mostrar_stock_disponible)

        tk.Label(left, text="Cantidad:", bg="white").pack(anchor="w")
        self.qty_entry = tk.Entry(left, fg="gray")
        self.qty_entry.insert(0, "Selecciona un producto")
        self.qty_entry.pack(fill="x", pady=5)
        self.qty_entry.bind("<FocusIn>", self.clear_placeholder)
        self.qty_entry.bind("<FocusOut>", self.restore_placeholder)

        # ----- TABLE CARD (Right side) -----
        right = tk.Frame(main_area, bg="white", relief="flat", padx=15, pady=15)
        right.place(relx=0.45, rely=0.02, relwidth=0.53, relheight=0.95)

        upper_right_frame = tk.Frame(right, bg='white')
        upper_right_frame.pack(side="top" , anchor='w', pady=(0, 5), fill="x")
        tk.Label(upper_right_frame, text="🧺 Productos en esta Venta", bg="white").pack(side='left', pady=(0, 5))
        button_today_sales = tk.Button(upper_right_frame, text='Todas las ventas', bg="#2b6cb0", fg="white", command=self.all_sales)
        button_today_sales.pack(side="right", padx=10)

        columnas_y_ancho = {
            "ID": 10,
            "Producto": 80,
            "Cantidad": 10,
            "Precio": 10,
            "Total": 20
        }

        self.sales_tree = ttk.Treeview(right, columns=[key for key in columnas_y_ancho.keys()], show="headings")
        for col in ("ID", "Producto", "Cantidad", "Precio", "Total"):
            self.sales_tree.heading(col, text=col)
            self.sales_tree.column(col, anchor="center", width=columnas_y_ancho[col])
        self.sales_tree.pack(fill="both", expand=True)

        # Totales
        total_frame = tk.Frame(right, bg="white")
        total_frame.pack(fill="x", pady=(10, 5))
        self.total_label = tk.Label(total_frame, text="Total: €0.00", font=("Segoe UI", 12, "bold"), fg="#1f2937", bg="white")
        self.total_label.pack(anchor="e")

        # BUTTONS
        style = ttk.Style()
        style.configure("AddVenta.TButton", foreground="black", background="#2b6cb0")
        style.map("AddVenta.TButton",
                background=[("active", "#2c5282")])
        style.configure("ConfirmSale.TButton", background="#2b6cb0", foreground="black")
        style.map("ConfirmSale.TButton", background=[("active", "#2c5282")])

        style.configure("CancelSale.TButton", background="#e53e3e", foreground="black")
        style.map("CancelSale.TButton", background=[("active", "#c53030")])

        ttk.Button(left, text="➕ Agregar a Venta", style="AddVenta.TButton", command=self.add_to_sale).pack(pady=10, fill="x")

        button_frame = tk.Frame(main_area, bg="#edf2f7")
        button_frame.place(relx=0.02, rely=0.85, relwidth=0.4, relheight=0.12)
        ttk.Button(button_frame, text="✅ Confirmar Venta", style="ConfirmSale.TButton", width=20, command=self.confirm_sale).pack(side='left', expand=True)
        ttk.Button(button_frame, text="❌ Cancelar", style="CancelSale.TButton", width=20, command=self.anulate_sale).pack(side='left', expand=True)
        

# ---------------------------------------------- METODOS AUXILIARES ---------------------------------------------- #
    def refresh_interface(self):
        self.refresh_left_panel()
        self.refresh_right_panel()
        
    def refresh_right_panel(self):
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)
        self.total_label.config(text=f"Total: €{Decimal(0.00):.2f}")

        self.filtrar_categoria_venta.set("Todos")
    
    def refresh_left_panel(self):
        self.product_entry.config(values=[f"{str(prod[0]).zfill(4)} - {prod[1]}" 
            for prod in sorted(product_dao.get_all_products_with_stock(), key=lambda x: x[1])])
        self.filtrar_categoria_venta.set("Todos")
        self.product_entry.delete(0, tk.END)
        self.product_entry.set("")
        self.qty_entry.delete(0, tk.END)
        self.qty_entry.insert(0, "Selecciona un producto")
    
    def mostrar_stock_disponible(self, event):
        selection = self.product_entry.get()
        prod_id = selection.split("-")[0].strip()
        prod_name = selection.split("-")[1].strip()
        if prod_id:
            try:
                prod_id = int(prod_id)
            except Exception:
                messagebox.showerror(title="ID no válido", message="No se pudo comprobar el stock con el ID de este producto.")
                return
            
            stock = product_dao.get_product_stock(prod_id)
            self.qty_entry.delete(0, tk.END)
            self.qty_entry.insert(0, f'Disponible: {stock}')
            self.qty_entry.config(fg='gray')
        else:
            messagebox.showerror(title="Producto no encontrado", message="No se pudo comprobar el stock de este producto.")
    
    def clear_placeholder(self, event):
        # Borra el texto solo si es el valor por defecto
        if event:
            if self.qty_entry.get() == "Selecciona un producto" or self.qty_entry.get().startswith("Disponible:"):
                self.qty_entry.delete(0, tk.END)
                self.qty_entry.config(fg="black")
        
    def restore_placeholder(self, event):
        # Si el campo está vacío, restauramos el valor por defecto
        if not self.qty_entry.get():
            self.qty_entry.insert(0, "Selecciona un producto")
            self.qty_entry.config(fg="gray")
    
    def update_prod_by_cat(self, event=None):
        categoria_seleccionada = self.filtrar_categoria_venta.get()
        if categoria_seleccionada == "Todos":
            productos_filtrados = [f"{prod[0]} - {prod[1]}" for prod in product_dao.get_all_products_with_stock()]
        else:
            productos_filtrados = [f"{prod[0]} - {prod[1]}" for prod in product_dao.get_all_products_with_stock(categoria_seleccionada)]
        
        self.product_entry['values'] = productos_filtrados
        self.product_entry.set('')  # Limpia la selección actual

    def add_to_sale(self):
        selection = self.product_entry.get()
        if not selection:
            messagebox.showerror(title="Seleccione un producto", message="Debe seleccionar un producto para vender.")
            return
        
        prod_id = selection.split("-")[0].strip()
        prod_name = selection.split("-")[1].strip()
        quantity = self.qty_entry.get()
        
        try:
            quantity = int(quantity)
        except ValueError:
            messagebox.showerror('Valor erróneo', 'La cantidad debe ser un número entero')
            return
        
        if quantity == 0:
            messagebox.showerror('Valor erróneo', 'La cantidad debe ser mayor que 0')
            return
        
        sell_price = Decimal(product_dao.get_product_price_stock(prod_id)[0]).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if sell_price == Decimal("0.00"):
            new_sell_price = simpledialog.askfloat("Precio de venta", "Debe definir primero un precio de venta para este producto")
            sell_price = Decimal(new_sell_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            update_sell_price = sales_dao.update_sell_price(prod_id, sell_price)
            if not update_sell_price:
                messagebox.showerror(title="Error al actualizar precio de venta", 
                                     message="Ocurrió un error al intentar actualizar el precio de venta de este producto.",
                                     parent=self.sell)
                return

        stock = int(product_dao.get_product_price_stock(prod_id)[1])
        row_total = Decimal((sell_price * quantity)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        if quantity > stock:
            messagebox.showwarning('No hay existencias suficientes', f'Solo puedes vender un máximo de {stock} unidades.')
            return
        
        # Decrease amount in DDBB
        def update_prod_stock():
            actual_stock = product_dao.get_product_stock(prod_id)
            new_stock = int(actual_stock) - int(quantity)

            prod_to_update = [(new_stock, prod_id)]
        
            return product_dao.update_prod_stock(prod_to_update)
            
            
        updated_prod = update_prod_stock()
        
        if updated_prod is None:
            messagebox.showerror(title="Error al añadir el producto", 
                                 message="Ocurrió un error al intentar añadir el producto para la venta.")
            return
        
        self.refresh_left_panel()

        # If the product that is already about to be sold is added again, we sum both amounts
        product_exists = None
        for item_id in self.sales_tree.get_children():
            current_values = self.sales_tree.item(item_id)["values"]
            if int(current_values[0]) == int(prod_id):
                new_values = list(current_values)
                new_values[2] = int(new_values[2]) + quantity
                new_values[4] = (Decimal(new_values[4]) + Decimal(row_total)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                self.sales_tree.item(item_id, values=new_values)
                self.product_entry.set('')
                self.qty_entry.delete(0, tk.END)
                product_exists = True
            
        if not product_exists:
            self.sales_tree.insert('', 'end', values=(prod_id, prod_name, quantity, Decimal(sell_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), 
                                                Decimal(row_total).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)))
            

        # CALCULATE TOTAL
        def calculate_total_sale():
            tree_total = 0
            for item_id in self.sales_tree.get_children():
                item = self.sales_tree.item(item_id)
                inserted_prod_total = Decimal(item["values"][4]).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                tree_total += inserted_prod_total
            return tree_total
            
        tree_total = calculate_total_sale()
        self.total_label.config(text=f"Total: €{Decimal(tree_total).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)}")
        
    def anulate_sale(self, from_sidebar=None, on_close=None):
        if len(self.sales_tree.get_children()) > 0:
            if not from_sidebar and not on_close:
                confirmation = messagebox.askyesno(title="Anulación de venta", message="¿Estás seguro que quieres anular la venta?")
            else:
                if from_sidebar:
                    confirmation = messagebox.askyesno(title="Anulación de venta", 
                                                    message="Si sale de esta ventana, la venta se anulará. ¿Quiere continuar?")
                elif on_close:
                    confirmation = messagebox.showwarning(title="Anulación de venta", 
                                                    message="Debe anular la venta antes de cerrar el programa.")
                    return None
            if confirmation:
                # Let's add back the products to the DB
                prods_to_update = []
                for item_id in self.sales_tree.get_children():
                    item = self.sales_tree.item(item_id)
                    prod_id = item["values"][0]
                    stock_to_add = item["values"][2]
                    current_stock = product_dao.get_product_stock(prod_id)
                    new_stock = int(stock_to_add) + int(current_stock)
                    prod = (new_stock, prod_id)
                    prods_to_update.append(prod,)

                updated = product_dao.update_prod_stock(prods_to_update)
                if updated and not from_sidebar and not on_close:
                    messagebox.showinfo(title="Venta anulada", message="Se anuló la venta correctamente.")
                self.refresh_interface()
                return True
            else:
                return None
        else:
            return True
        
    def confirm_sale(self):
        if not self.sales_tree.get_children():
            messagebox.showerror(title="No hay productos", message="Debe añadir al menos un producto.")
            return
        
        sales_to_update = []
        for item_id in self.sales_tree.get_children():
            current_values = self.sales_tree.item(item_id)["values"]
            prod_id = current_values[0]
            sale_quantity = float(current_values[2])
            buy_price = product_dao.get_buy_price(prod_id)
            sale_price = float(current_values[3])
            total = round(float(sale_quantity * sale_price), 2)
            profit = round(float((sale_quantity * sale_price) - (sale_quantity * float(buy_price))), 2)
            sale_date = datetime.now()
            employee_id = self.employee_id
            
            prod = (
                prod_id,
                sale_quantity,
                buy_price,
                sale_price,
                total,
                profit,
                sale_date,
                employee_id
            )

            sales_to_update.append(prod)
                
        sale_registered = sales_dao.register_sale(sales_to_update)
        if sale_registered:
            messagebox.showinfo(title="Venta satisfactoria", message="Se completó la venta correctamente.")
            self.refresh_interface()
        else:
            messagebox.showerror(title="Error en la venta", message="Ocurrió un error al intentar registrar la venta.")
           
    
    def all_sales(self, sale_date=None):
        if sale_date is None:
            sales_by_date_in_bbdd = sales_dao.get_sales_by_date(date=None)
            if sales_by_date_in_bbdd is None:
                messagebox.showinfo(title="No hay ventas registradas", message="No hay ningún registro de venta para mostrar")
                return
        else:
            sales_by_date_in_bbdd = sales_dao.get_sales_by_date(date=sale_date)
            if sales_by_date_in_bbdd is None:
                messagebox.showinfo(title="No hay ventas registradas", message="No hay ningún registro de venta con la fecha seleccionada para mostrar.")
                # If no sales to filter, show all sales by default
                self.all_sales()
                return
        
        popup = tk.Toplevel()
        popup.title("Historial de ventas")
        popup.geometry("1000x600+0+0")
        popup.resizable(False, False)
        popup.grab_set()

        columnas_y_ancho = {
            "Venta ID": 10,
            "Fecha Venta": 40,
            "Prod. ID": 10,
            "Producto": 200,
            "Cantidad": 10,
            "Precio": 10,
            "Total": 20,
            "Empleado ID": 20
        }
        
        frame = ttk.Frame(popup, height=500)
        frame.pack(expand=True, fill="both")

        self.tree_sales_history = ttk.Treeview(frame, columns=list(columnas_y_ancho.keys()), show="headings")
        for name, width in columnas_y_ancho.items():
            self.tree_sales_history.heading(name, text=name)
            self.tree_sales_history.column(name, width=width, anchor="center")
        self.tree_sales_history.pack(expand=True, fill="both")
        

        def delete_sale():
            selection = self.tree_sales_history.selection()
            if not selection:
                messagebox.showerror(title="Seleccione un registro", message="Debe seleccionar un registro de venta para ser eliminado.")
                return
            
            if len(selection) < 2:
                confirm = messagebox.askokcancel(title="Eliminar venta", message="¿Estás seguro de querer eliminar este registro de venta?")
            else:
                confirm = messagebox.askokcancel(title="Eliminar venta", message=f"¿Estás seguro de querer eliminar estos {len(selection)} registros de venta?")
            
            if confirm:
                sales_id = []
                for row in selection:
                    item = self.tree_sales_history.item(row)
                    values = item["values"]
                    sales_id.append((values[0],))
                deleted = sales_dao.delete_sales(sales_id)
                
                if deleted:
                    popup.destroy()
                    if len(selection) < 2:
                        messagebox.showinfo(title="Registro eliminado", message="Se eliminó el registro de venta seleccionado.")
                    else:
                        messagebox.showinfo(title="Registros eliminados", message=f"Se eliminaron los {len(selection)} registros de venta seleccionados.")
                    
                    if len(sales_by_date_in_bbdd) != len(sales_id):
                        self.all_sales()
        
        def filter_sale_by_date(today=None, all=None):
            date = self.date_filter_var.get()
            if not today and not all:
                try:
                    date_filter = datetime.strptime(date, '%d/%m/%Y')
                except Exception:
                    messagebox.showerror(title="Datos incorrectos", message="Debe introducir una fecha válida con formato dd/mm/aaaa")
                    return
                else:
                    popup.destroy()
                    self.all_sales(date_filter)
            elif today:
                popup.destroy()
                self.all_sales(today)
            elif all:
                popup.destroy()
                self.all_sales(sale_date=None)
            
        button_frame = ttk.Frame(popup, padding=5)
        button_frame.pack(fill="x")

        del_sale = ttk.Button(button_frame, text="Eliminar venta", command=delete_sale)
        del_sale.pack(side="left", padx=(350, 50))

        self.date_filter_var = tk.StringVar()
        entry_date_filter = ttk.Entry(button_frame, textvariable=self.date_filter_var)
        entry_date_filter.pack(side="left", padx=(50, 0))

        filter_sale = ttk.Button(button_frame, text="Filtrar", command=filter_sale_by_date)
        filter_sale.pack(side="left", padx=(10, 0))

        today_sales = ttk.Button(button_frame, text="Hoy", command=lambda: filter_sale_by_date(datetime.today().date()))
        today_sales.pack(side="left", padx=(10, 0))

        all_sales = ttk.Button(button_frame, text="Todas", command=lambda: filter_sale_by_date(all=True))
        all_sales.pack(side="left", padx=(10, 0))

        for sale in sales_by_date_in_bbdd:
            self.tree_sales_history.insert("", "end", values=sale)