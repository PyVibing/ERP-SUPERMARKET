import os
import subprocess
import platform
import tkinter as tk
import shutil
import bcrypt
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta, time
from config.config import *
from config.services import employees_dao, users_dao
from decimal import Decimal, ROUND_HALF_UP



class Employee(tk.Frame):
    def __init__(self, parent):
        self.empleados_main_frame = parent
        self.build_interface()

    def build_interface(self):
        # ----- HEADER -----
        header = tk.Frame(self.empleados_main_frame, bg="#2b6cb0", height=60)
        header.pack(fill="x")
        tk.Label(header, text="Gestión de Empleados", bg="#2b6cb0", fg="white", font=("Segoe UI", 16, "bold")).pack(pady=15)

        # ----- MAIN BODY -----
        main = tk.Frame(self.empleados_main_frame, bg="#edf2f7")
        main.pack(fill="both", expand=True, padx=20, pady=20)

        # ----- FORM CARD (Izquierda) -----
        form_card = tk.Frame(main, bg="white", relief="flat")
        form_card.place(x=20, y=20, width=400, height=550)


        # Entradas generales
        def create_labels_entrys(attr_name, label_text):
            frame = tk.Frame(form_card, bg="white")
            frame.pack(fill="x", padx=20, pady=5)
            tk.Label(frame, text=label_text, bg="white", anchor="w").pack(fill="x")
            
            entry = ttk.Entry(frame)
            entry.pack(fill="x")
            
            setattr(self, attr_name, entry)  # Crea self.nombre, self.email, etc.

        campos = [
            ("nombre_entry", "Nombre:"),
            ("cargo_entry", "Cargo:"),
            ("id_entry", "DNI/NIE/ID:"),
            ("telefono_entry", "Teléfono:"),
            ("email_entry", "Email:"),
            ("direccion_entry", "Dirección:")
        ]

        for attr, label in campos:
            create_labels_entrys(attr, label)

        # Frame para JORNADA TRABAJO, HORAS SEMANALES y SALARIO
        jornada_horas_frame = tk.Frame(form_card, bg="white")
        jornada_horas_frame.pack(fill="x", padx=20, pady=5)

        # ----- Jornada de trabajo -----
        jornada_frame = tk.Frame(jornada_horas_frame, bg="white")
        jornada_frame.pack(side="left", fill="x", expand=True)
        tk.Label(jornada_frame, text="Jornada de trabajo:", bg="white", anchor="w").pack(fill="x")
        self.jornada_combobox = ttk.Combobox(jornada_frame, values=['Completa', 'Parcial'], state='readonly')
        self.jornada_combobox.pack(fill="x")

        # ---- Horas semanales ----
        horas_frame = tk.Frame(jornada_horas_frame, bg="white")
        horas_frame.pack(side="left", fill="x", expand=True)
        tk.Label(horas_frame, text="Horas semanales:", bg="white", anchor="w").pack(fill="x", padx=(5, 0))
        self.horas_semana_entry = ttk.Entry(horas_frame)
        self.horas_semana_entry.pack(fill="x", padx=(5, 0))

        # ---- SALARIO ----
        salary_frame = tk.Frame(jornada_horas_frame, bg="white")
        salary_frame.pack(side="left", fill="x", expand=True)
        tk.Label(salary_frame, text="Salario:", bg="white", anchor="w").pack(fill="x", padx=(5, 0))
        self.salary_entry = ttk.Entry(salary_frame)
        self.salary_entry.pack(fill="x", padx=(5, 0))

        # Frame para HORARIO ENTRADA y SALIDA
        horario_frame = tk.Frame(form_card, bg="white")
        horario_frame.pack(fill="x", padx=20, pady=5)

        # Horario entrada
        horario_in_frame = tk.Frame(horario_frame, bg="white")
        horario_in_frame.pack(side="left", fill="x", expand=True)
        tk.Label(horario_in_frame, text="Entrada:", bg="white", anchor="w").pack(fill="x")
        self.check_in_hour_combobox = ttk.Combobox(horario_in_frame, values=[f"{i:02d}:00" for i in range(24)])
        self.check_in_hour_combobox.pack(fill="x")

        # Horario salida
        horario_out_frame = tk.Frame(horario_frame, bg="white")
        horario_out_frame.pack(side="left", fill="x", expand=True)
        tk.Label(horario_out_frame, text="Salida:", bg="white", anchor="w").pack(fill="x", padx=(10, 0))
        self.check_out_hour_combobox = ttk.Combobox(horario_out_frame, values=[f"{i:02d}:00" for i in range(24)])
        self.check_out_hour_combobox.pack(fill="x", padx=(10, 0))
        
        # FECHA BAJA, TIPO DE CONTRATO y FECHA DE ALTA
        estado_contrato = tk.Frame(form_card, bg="white")
        estado_contrato.pack(fill="x", padx=20, pady=5)

        # ----- Tipo de contrato -----
        contrato_frame = tk.Frame(estado_contrato, bg="white")
        contrato_frame.pack(side="left", fill="x", expand=True)
        tk.Label(contrato_frame, text="Tipo de contrato:", bg="white", anchor="w").pack(fill="x")
        self.contract_type_combobox = ttk.Combobox(contrato_frame, values=["Indefinido", "Temporal"], state='readonly')
        self.contract_type_combobox.pack(fill="x")
        self.contract_type_combobox.bind("<<ComboboxSelected>>", self.check_contract_type)

        # ----- Fecha de alta -----
        fecha_ingreso_frame = tk.Frame(estado_contrato, bg="white")
        fecha_ingreso_frame.pack(side="left", fill="x", expand=True)
        tk.Label(fecha_ingreso_frame, text="Fecha alta:", bg="white", anchor="w").pack(fill="x", padx=(5, 0))
        self.start_date_entry = ttk.Entry(fecha_ingreso_frame)
        self.start_date_entry.pack(fill="x", padx=(5, 0))
                
        # Fin de contrato (derecha) - Deshabilitado por defecto
        self.fin_contrato_frame = tk.Frame(estado_contrato, bg="white")
        self.fin_contrato_frame.pack(side="left", fill="x", expand=True)
        tk.Label(self.fin_contrato_frame, text="Fin contrato:", bg="white", anchor="w").pack(fill="x", padx=(5, 0))
        self.end_contract_entry = ttk.Entry(self.fin_contrato_frame)
        self.end_contract_entry.pack(fill="x", padx=(5, 0))
        self.end_contract_entry["state"] = "disabled"
        
        # ----- Botones -----
        style = ttk.Style()
        style.configure("Accent.TButton", foreground="black", background="#2b6cb0")
        style.map("Accent.TButton", background=[("active", "#2c5282")], foreground=[("disabled", "#aaa")])
        style.configure("Eliminar.TButton", background="#e53e3e", foreground="black")
        style.map("Eliminar.TButton", background=[("active", "#c53030")])

        btn_frame = tk.Frame(main, bg="#edf2f7")
        btn_frame.place(x=20, y=570, width=400, height=50)
        
        self.add_employee_btn = ttk.Button(btn_frame, text="Agregar empleado", style="Accent.TButton", command=self.add_employee)
        self.add_employee_btn.pack(side="left", padx=5, pady=10, expand=True)
        self.edit_employee_btn = ttk.Button(btn_frame, text="Editar empleado", style="Accent.TButton", command=self.edit_employee_data)
        self.edit_employee_btn.pack(side="left", padx=5, pady=10, expand=True)
        self.del_employee_btn = ttk.Button(btn_frame, text="Eliminar empleado", style="Eliminar.TButton", command=self.delete_employee)
        self.del_employee_btn.pack(side="left", padx=5, pady=10, expand=True)
        

        # ----- TABLE CARD (Derecha) -----
        table_card = tk.Frame(main, bg="white", relief="flat")
        table_card.place(x=440, y=20, width=850, height=600)


        columnas_y_ancho = {
            "ID": 10,
            "Nombre": 120,
            "Cargo": 30,
            "Jornada": 30,
            "Hrs. Sem.": 20,
            "Salario": 20,
            "Hora Ent.": 20,
            "Hora Sal": 20,
            "Contrato": 40,
            "Alta": 30,
            "Estado": 25,
            "Datos Pers.": 30
        }
        
        self.tree_empleados = ttk.Treeview(table_card, columns=list(columnas_y_ancho.keys()), show="headings", height=30)
        for name, width in columnas_y_ancho.items():
            self.tree_empleados.heading(name, text=name)
            self.tree_empleados.column(name, width=width, anchor="center")
        self.tree_empleados.pack(fill="both", padx=10, pady=10)
        self.tree_empleados.bind("<ButtonRelease-1>", self.check_click_on_tree)

        # Styles that will be later used
        style = ttk.Style()
        style.configure("White.TFrame", background="white")
        style.configure("White.TLabel", background="white")

    # METODOS AUXILIARES
    def refresh_interface(self):
        self.refresh_left_panel()
        self.refresh_right_panel()

    def refresh_left_panel(self):
        self.nombre_entry.delete(0, tk.END)
        self.cargo_entry.delete(0, tk.END)
        self.id_entry.delete(0, tk.END)
        self.telefono_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.direccion_entry.delete(0, tk.END)
        self.jornada_combobox.set("")
        self.horas_semana_entry.delete(0, tk.END)
        self.salary_entry.delete(0, tk.END)
        self.check_in_hour_combobox.set("")
        self.check_out_hour_combobox.set("")
        self.contract_type_combobox.set("")
        self.start_date_entry.delete(0, tk.END)
        self.check_contract_type(event=None)

        self.add_employee_btn.config(text="Agregar empleado", command=self.add_employee)
        self.del_employee_btn.config(text="Eliminar empleado", command=self.delete_employee)
        self.edit_employee_btn.config(state="normal")
        
    def refresh_right_panel(self):
        # Deleting data from the right treeview
        for item in self.tree_empleados.get_children():
            self.tree_empleados.delete(item)
        
        # Getting the employee data (only WORK DATA) from DB and inserting it into the right side treeview
        employees = employees_dao.get_all_employees(work_data=True, priv_data=None)
        for employee_db in employees:
            employee_tree = [employee_db[0], employee_db[1], employee_db[2], employee_db[3], employee_db[5], employee_db[6], employee_db[7], 
                             employee_db[8], employee_db[4], employee_db[10].date(), employee_db[9], "[...]"]
            employee_tree[6] = self.timedelta_to_string(employee_tree[6])
            employee_tree[7] = self.timedelta_to_string(employee_tree[7])
            if employee_db[4] == "Temporal":
                employee_tree[8] = "[Temporal]" #This way, users know this field can be clicked for more info
            if employee_db[4] == "Indefinido":
                employee_tree[8] = "[Indefinido]" #This way, users know this field can be clicked for more info
            if employee_db[9] == "Inactivo":
                employee_tree[10] = "[Inactivo]" #This way, users know this field can be clicked for more info
            if employee_db[9] == "Activo":
                employee_tree[10] = "[Activo]" #This way, users know this field can be clicked for more info
            self.tree_empleados.insert("", "end", values=employee_tree)

    
    def check_contract_type(self, event=None):
        if self.contract_type_combobox.get() == "Temporal":
            self.end_contract_entry["state"] = "normal"
        else:
            self.end_contract_entry.delete(0, tk.END)
            self.end_contract_entry["state"] = "disabled"
    
    def delete_employee(self):
        selection = self.tree_empleados.selection()
        if not selection:
            messagebox.showerror(title="Selecciona un empleado", message="Debe seleccionar al menos un empleado para eliminar.")
            return
        if len(selection) < 2:
            confirmation = messagebox.askokcancel(title="Eliminar empleado", 
                                                  message="¿Está seguro de querer eliminar este empleado de la Base de Datos?")
        else:
            confirmation = messagebox.askokcancel(title="Eliminar empleados", 
                                                  message=f"¿Está seguro de querer eliminar estos {len(selection)} empleados de la Base de Datos?")
        if not confirmation:
            return
        
        employees_id = []
        for item in selection:
            id = int(self.tree_empleados.item(item, "values")[0])
            employees_id.append((id,))
        deleted = employees_dao.delete_employee(employees_id)
        if not deleted:
            if len(selection) < 2:
                messagebox.showerror(title="Error al eliminar empleado", 
                                     message="Ocurrió un error al intentar eliminar el empleado.")
                return
            else:
                messagebox.showerror(title="Error al eliminar empleados", 
                                     message=f"Ocurrió un error al intentar eliminar estos {len(selection)} empleado.")
                return
        self.refresh_right_panel()
        if len(selection) < 2:
            messagebox.showinfo(title="Empleado eliminado", message="Se eliminó correctamente el empleado seleccionado.")
        else:
            messagebox.showinfo(title="Empleados eliminados", message=f"Se eliminaron correctamente los {len(selection)} empleados seleccionados.")
        
    
    def add_employee(self, update_id=None):
        """ If update_id, employee is updated. Else, employee is added for the first time."""
        name = self.nombre_entry.get().strip().title()
        position = self.cargo_entry.get().strip().capitalize()
        personal_id = self.id_entry.get().strip()
        phone = self.telefono_entry.get().strip()
        email = self.email_entry.get().strip()
        address = self.direccion_entry.get().strip().capitalize()
        work_shift = self.jornada_combobox.get().strip().capitalize()
        week_hours = self.horas_semana_entry.get().strip()
        salary = self.salary_entry.get().strip()
        entry_time = self.check_in_hour_combobox.get().strip()
        exit_time = self.check_out_hour_combobox.get().strip()
        contract_type = self.contract_type_combobox.get().strip()
        start_date = self.start_date_entry.get().strip()
        end_date = self.end_contract_entry.get().strip()

        # ---------- DATA VALIDATION ---------- #
        if not all([name, position, personal_id, phone, email, address, work_shift, week_hours, salary, entry_time, exit_time, contract_type,
                start_date]):
            messagebox.showwarning(title="Faltan datos", message="Por favor, complete los datos que faltan en el formulario.")
            return
        
        state = str(self.end_contract_entry.cget("state")).lower().strip()
        if state == "normal" and not end_date:
            messagebox.showwarning(title="Faltan datos", message="Por favor, complete los datos que faltan en el formulario.")
            return
               
        try:
            week_hours = int(week_hours)
        except Exception:
            messagebox.showerror(title="Error de datos", message="Las horas semanales deben ser un número entero.")
            return
        else:
            if week_hours < 1:
                messagebox.showerror(title="Error de datos", message="Las horas semanales deben ser un número mayor que 0.")
                return
        
        try:
            salary = Decimal(salary).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        except Exception:
            messagebox.showerror(title="Error de datos", message="El salario debe ser un número entero o decimal.")
            return
        else:
            if salary <= 0:
                messagebox.showerror(title="Error de datos", message="El salario debe ser un número mayor que 0.")
                return
        
        
        if ":" not in entry_time:
            messagebox.showerror(title="Error de datos", message="La hora de entrada debe tener un formato 'HH:MM'.")
            return
        hour, min = entry_time.split(":")
        hour = int(hour)
        
        try:
            datetime.strptime(entry_time, "%H:%M")
        except ValueError:
            messagebox.showerror(title="Error de datos", message="La hora de entrada debe tener un formato 'HH:MM' válido (00:00 a 23:59).")
            return
        else:
            _, min = entry_time.split(":")
            if len(min) < 2:
                messagebox.showerror(title="Error de datos", message="Los minutos de la hora de entrada deben tener dos dígitos.")
                return
            try:
                entry_time_obj = datetime.strptime(entry_time, "%H:%M").time()
            except ValueError:
                messagebox.showerror(title="Error de datos", message="La hora de entrada debe tener un formato 'HH:MM' válido (00:00 a 23:59).")
                return
       
        try:
            datetime.strptime(exit_time, "%H:%M")
        except ValueError:
            messagebox.showerror(title="Error de datos", message="La hora de salida debe tener un formato 'HH:MM' válido (00:00 a 23:59).")
            return
        else:
            _, min = exit_time.split(":")
            if len(min) < 2:
                messagebox.showerror(title="Error de datos", message="Los minutos de la hora de salida deben tener dos dígitos.")
                return
            try:
                exit_time_obj = datetime.strptime(exit_time, "%H:%M").time()
            except ValueError:
                messagebox.showerror(title="Error de datos", message="La hora de salida debe tener un formato 'HH:MM' válido (00:00 a 23:59).")
                return
            
        try:
            start_date_obj = datetime.strptime(start_date, "%d/%m/%Y").date()
        except Exception:
            messagebox.showerror(title="Error de formato", message="La fecha de alta debe tener un formato correcto ('DD/MM/YYYY').")
            return
        else:
            if start_date_obj > datetime.now().date():
                messagebox.showerror(title="Error en la fecha", message="La fecha de alta debe ser anterior a la fecha actual.")
                return
        
        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, "%d/%m/%Y").date()
            except Exception:
                messagebox.showerror(title="Error de formato", message="La fecha de fin de contrato debe tener un formato correcto ('DD/MM/YYYY').")
                return
            else:
                if end_date_obj < datetime.now().date():
                    messagebox.showerror(title="Error en la fecha", message="La fecha de fin de contrato debe ser posterior a la fecha actual.")
                    return
        
        # ---------- DATA COINCIDENCE VALIDATION ---------- #
        if not update_id: #if editing, let's skip this step
            data_exists = employees_dao.get_employee_by_data(email=email, personal_id=personal_id, name=name)
            if data_exists == "email":
                messagebox.showwarning(title="Email ya existe", message="Ya existe este email registrado para un usuario en la Base de Datos.")
                return
            elif data_exists == "personal_id":
                messagebox.showwarning(title="ID Personal ya existe", message="Ya existe este ID Personal registrado para un usuario en la Base de Datos.")
                return
            elif isinstance(data_exists, tuple):
                _, quantity = data_exists
                if quantity == 1:
                    confirmation = messagebox.askokcancel(title="Existe un nombre igual", 
                                        message="Ya existe un usuario con este mismo nombre aunque. ¿Quiere añadirlo igualmente?")
                elif quantity > 1:
                    confirmation = messagebox.askokcancel(title="Existen varios nombres iguales", 
                                        message=f"Ya existen {quantity} usuarios con este mismo nombre. ¿Quiere añadirlo igualmente?")
                if not confirmation:
                    return
            elif data_exists == "error":
                messagebox.showerror(title="Error al comparar datos", 
                                    message="Ocurrió un error intentando comparar los datos a ingresar con los datos en la Base de Datos")
                return

        # ---------- INSERTING TO DATABASE ---------- #
        if not update_id:
            employee_status = "Activo" # By default
            values_to_insert = (name, personal_id, phone, email, address, position, work_shift, contract_type,
                            week_hours, salary, entry_time_obj, exit_time_obj, employee_status, start_date_obj)
        else:
            values_to_update = (name, personal_id, phone, email, address, position, work_shift, contract_type,
                            week_hours, salary, entry_time_obj, exit_time_obj, start_date_obj)

        
        if end_date:
            if not update_id:
                inserted = employees_dao.insert_employee(values_to_insert, end_contract=end_date_obj)
            else:
                updated = employees_dao.update_employee_data(update_id, values_to_update, end_contract=end_date_obj)
                pass
        else:
            if not update_id:
                inserted = employees_dao.insert_employee(values=values_to_insert, end_contract=None)
            else:
                updated = employees_dao.update_employee_data(update_id, values_to_update, end_contract=None)

        if not update_id:
            if not inserted:
                messagebox.showerror(title="Error al insertar empleado", 
                                    message="Ocurrió un error al intentar insertar los datos del empleado en la Base de Datos.")
                return
            self.refresh_interface()
            messagebox.showinfo(title="Empleado insertado", message="Se insertaron correctamente los datos del empleado en la Base de Datos.")
        else:
            if not updated:
                messagebox.showerror(title="Error al actualizar empleado", 
                                    message="Ocurrió un error al intentar actualizar los datos del empleado en la Base de Datos.")
                return
            self.refresh_interface()
            messagebox.showinfo(title="Empleado actualizado", message="Se actualizaron correctamente los datos del empleado en la Base de Datos.")
        
    def check_click_on_tree(self, event):
        self.region = self.tree_empleados.identify("region", event.x, event.y)
        self.column = self.tree_empleados.identify_column(event.x)
        self.row_id = self.tree_empleados.identify_row(event.y)
        if self.row_id:
            self.row_number = self.tree_empleados.get_children().index(self.row_id) + 1

        if self.region == "cell": 
            if self.column == "#12": # Datos pers.
                self.priv_data_popup()
            elif self.column == "#9": # Contrato
                value = self.tree_empleados.set(self.row_id, self.column)
                self.end_contract_popup(value)
            elif self.column == "#11": # Estado
                value = self.tree_empleados.set(self.row_id, self.column)
                self.employee_status_popup(value)
    
    def refresh_priv_data_popup(self):
        employee_id = int(self.tree_empleados.item(self.row_id, "values")[0])
        employee_priv_data = employees_dao.get_employee_data(employee_id, work_data=None, priv_data=True)
        employee_name = employee_priv_data[1]
        employee_email = employee_priv_data[4]

        for item in self.tree_priv_data.get_children():
            self.tree_priv_data.delete(item)

        self.tree_priv_data.insert("", "end", values=(employee_priv_data + ("[...]",)))

        user_exist = users_dao.get_user_data(employee_id)
        if not user_exist:
            # Button
            self.create_user_btn.config(text="🔁 Crear usuario", command=lambda: self.open_popup_create_user(employee_id, employee_email))
        else:
            self.create_user_btn.config(text="🔁 Ver usuario", command=lambda: self.user_data_popup(employee_id, employee_name, employee_email))
        
        
    
    def priv_data_popup(self):
        employee_id = int(self.tree_empleados.item(self.row_id, "values")[0])
        employee_priv_data = employees_dao.get_employee_data(employee_id, work_data=None, priv_data=True)
        if not employee_priv_data:
            messagebox.showerror(title="Error al acceder a los datos", 
                                    message=f"Ocurrió un error al intentar acceder a los datos del empleado con ID {employee_id}.")
            return
        employee_name = employee_priv_data[1]
        
        self.popup_data = tk.Toplevel(self.empleados_main_frame)
        self.popup_data.title(f"Datos personales de {employee_name}")
        self.popup_data.geometry("850x100+618+310")
        self.popup_data.resizable("False", "False")
        self.popup_data.configure(bg="white")
        self.popup_data.grab_set()

        frame_content = tk.Frame(self.popup_data, bg="white")
        frame_content.pack(fill="both", expand=True)

        columnas_y_ancho = {
            "ID": 20,
            "Nombre": 200, 
            "ID Personal": 50,
            "Teléfono": 50,
            "Email": 50,
            "Dirección": 150
        }
                        
        self.tree_priv_data = ttk.Treeview(frame_content, columns=list(columnas_y_ancho.keys()), show="headings", height=1)
        for name, width in columnas_y_ancho.items():
            self.tree_priv_data.heading(name, text=name)
            self.tree_priv_data.column(name, width=width, anchor="center")
        self.tree_priv_data.pack(fill="both", expand=True)

        self.create_user_btn = ttk.Button(self.popup_data, style="Accent.TButton")
        self.create_user_btn.pack(pady=5)
        
        self.refresh_priv_data_popup()
        

        

    def open_popup_create_user(self, employee_id, user_email, edit=False):
        if not edit:
            self.popup_create_user = tk.Toplevel(self.popup_data, bg="white")
        else:
            self.popup_create_user = tk.Toplevel(self.popup_user_data, bg="white")
        if not edit:
            self.popup_create_user.title("Crear usuario")
        else:
            self.popup_create_user.title("Editar datos de usuario")

        self.popup_create_user.geometry("400x210+618+310")
        self.popup_create_user.resizable(False, False)
        self.popup_create_user.grab_set()

        def create_user(edit=False):
            if not edit:
                # VERIFY IF THIS EMPLOYEE HAS ALREADY A USER CREATED
                exists = users_dao.get_user_data(employee_id=employee_id)
                if exists:
                    messagebox.showwarning(title="Usuario ya existe",
                                        message="Ya existe un usuario creado para este empleado.",
                                        parent=self.popup_create_user)
                    return
            
            role = role_combobox.get()
            password = password_entry.get()
            if not edit:
                if not role or not password:
                    messagebox.showwarning(title="Rellene los campos faltantes", 
                                        message="Debe rellenar todos los datos solicitados.",
                                        parent=self.popup_create_user)
                    return
            if not edit or (edit and password):
            
                signs_list = ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "_", "+", "-", "=", "{", "}",
                                    "[", "]", "|", ":", ";", "'", "<", ">", "?", "/", ".", "~", "`"]
                signs = 0
                uppers = 0
                lowers = 0
                number = 0
                for x in password:
                    for i in signs_list:
                        if x == i:
                            signs += 1
                    if x.isalpha() and x == x.upper():
                        uppers += 1
                    if x.isalpha() and x == x.lower():
                        lowers += 1
                    if x.isdigit():
                        number += 1
                
                if signs < 1 or len(password) < 8 or uppers < 1 or lowers < 1 or number < 1:
                    messagebox.showwarning(title="Contraseña debil", 
                                        message="Cree una contraseña de al menos 8 CARACTERES. Además, debe contener al menos: " \
                                        "1 SIGNO,  1 MAYÚSCULA, 1 MINÚSCULA, 1 NÚMERO",
                                        parent=self.popup_create_user)
                    return
            
            
            if password:
                password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            else:
                password_hash = None
            
            
            if not edit:
                values = (employee_id, user_email, password_hash, role)
                inserted = users_dao.create_user(values)
            else:
                #values = (user_email, password_hash, role)
                if password_hash and role:
                    updated = users_dao.update_user(employee_id, password_hash=password_hash, role=role)
                elif password_hash and not role:
                    updated = users_dao.update_user(employee_id, password_hash=password_hash, role=None)
                elif role and not password_hash:
                    updated = users_dao.update_user(employee_id, password_hash=None, role=role)

            
            if not edit:
                if not inserted:
                    messagebox.showerror(title="Error al crear usuario",
                                        message="Ocurrió un error al intentar crear el usuario.",
                                        parent=self.popup_create_user)
                    return
                messagebox.showinfo("Usuario creado", message="Se creó el usuario correctamente.",
                                    parent=self.popup_create_user)
            else:
                if not updated:
                    messagebox.showerror(title="Error al actualizar datos",
                                        message="Ocurrió un error al intentar actualizar los datos del usuario.",
                                        parent=self.popup_create_user)
                    return
                messagebox.showinfo("Usuario creactualizado", message="Se actualizaron los datos del usuario correctamente.",
                                    parent=self.popup_create_user)
                
            self.popup_create_user.destroy()
            if edit:
                self.refresh_user_data_popup(employee_id)
            else:
                self.refresh_priv_data_popup()

        ttk.Style()

        # === Frame contenedor general ===
        form_frame = ttk.Frame(self.popup_create_user, style="White.TFrame")
        form_frame.pack(fill="x", padx=20, pady=20)

        # === Usuario ===
        label_usuario = ttk.Label(form_frame, text="Usuario:", font=("Segoe UI", 11, "bold"), style="White.TLabel", anchor="e")
        label_usuario.grid(row=0, column=0, sticky="e", padx=(0, 10), pady=(0, 15))

        subtitulo = ttk.Label(form_frame, text=user_email, font=("Segoe UI", 11), style="White.TLabel", anchor="w")
        subtitulo.grid(row=0, column=1, sticky="w", pady=(0, 15))

        # === Rol ===
        label_rol = ttk.Label(form_frame, text="Rol:", font=("Segoe UI", 11, "bold"), style="White.TLabel", anchor="e")
        label_rol.grid(row=2, column=0, sticky="e", padx=(0, 10), pady=(0, 15))

        role_combobox = ttk.Combobox(form_frame, values=["Invitado", "Empleado", "Supervisor", "RRHH", "Gerente", "Admin"], state="readonly")
        role_combobox.grid(row=2, column=1, sticky="w", pady=(0, 15))

        # === Password ===
        label_password = ttk.Label(form_frame, text="Contraseña:", font=("Segoe UI", 11, "bold"), style="White.TLabel", anchor="e")
        label_password.grid(row=4, column=0, sticky="e", padx=(0, 10), pady=(0, 15))

        password_entry = ttk.Entry(form_frame)
        password_entry.grid(row=4, column=1, sticky="w", pady=(0, 15))

        # === Boton CREAR ===
        if not edit:
            create_btn = ttk.Button(form_frame, text="Crear usuario", style="Accent.TButton", command=create_user)
        else:
            create_btn = ttk.Button(form_frame, text="Actualizar datos", style="Accent.TButton", command=lambda: create_user(edit=True))
        create_btn.grid(row=6, column=1, sticky="w", pady=(10, 15))
    
    def refresh_user_data_popup(self, employee_id):
        # Delete and insert data in treeview
        for item in self.tree_user_data.get_children():
            self.tree_user_data.delete(item)

        user_data = users_dao.get_user_data(employee_id=employee_id)
        if user_data:
            email, _, role = user_data
            tree_values = (employee_id, email, role, "*****")
        
            self.tree_user_data.insert("", "end", values=tree_values)
        else:
            self.popup_user_data.destroy()


    
    def user_data_popup(self, employee_id, employee_name, employee_email):
        self.popup_user_data = tk.Toplevel(self.popup_data)
        self.popup_user_data.title(f"Datos de usuario de {employee_name}")
        self.popup_user_data.geometry("850x100+618+440")
        self.popup_user_data.resizable("False", "False")
        self.popup_user_data.configure(bg="white")
        self.popup_user_data.grab_set()
        
        frame_content = tk.Frame(self.popup_user_data, bg="white")
        frame_content.pack(fill="both", expand=True)

        columnas_y_ancho = {
            "ID": 20,
            "Email": 100,
            "Rol": 50,
            "Contraseña": 20
        }
                        
        self.tree_user_data = ttk.Treeview(frame_content, columns=list(columnas_y_ancho.keys()), show="headings", height=1)
        for name, width in columnas_y_ancho.items():
            self.tree_user_data.heading(name, text=name)
            self.tree_user_data.column(name, width=width, anchor="center")
        self.tree_user_data.pack(fill="both", expand=True)

        # Button frame and buttons
        left_btn_frame = tk.Frame(self.popup_user_data, bg="white")
        left_btn_frame.pack(side="left", fill="both", expand=True, padx=(0, 7))

        right_btn_frame = tk.Frame(self.popup_user_data, bg="white")
        right_btn_frame.pack(side="left", fill="both", expand=True, padx=(7, 0))

        self.change_role = ttk.Button(left_btn_frame, text="🔁 Editar datos", style="Accent.TButton", 
                                            command=lambda: self.open_popup_create_user(employee_id, employee_email, edit=True))
        self.change_role.pack(side="right")

        self.delete_user = ttk.Button(right_btn_frame, text="🔁 Eliminar usuario", style="Eliminar.TButton", 
                                            command=lambda: self.delete_user_from_db(employee_id))
        self.delete_user.pack(side="left")

        self.refresh_user_data_popup(employee_id)
    
    def delete_user_from_db(self, employee_id):
        confirmation = messagebox.askokcancel(title="Eliminar usuario",
                                              message="¿Quiere realmente eliminar este usuario? Esta acción no puede deshacerse.",
                                              parent=self.popup_user_data)
        if not confirmation:
            return
        
        deleted = users_dao.delete_user_data(employee_id)
        if not deleted:
            messagebox.showerror(title="Error al eliminar usuario",
                                 message="Ocurrió un error al intentar eliminar la cuenta de usuario de este empleado.",
                                 parent=self.popup_user_data)
            return
        messagebox.showinfo(title="Usuario eliminado",
                            message="Se eliminaron correctamente los datos de usuario de este empleado.",
                            parent=self.popup_user_data)
        self.refresh_priv_data_popup()
        self.refresh_user_data_popup(employee_id)


    def refresh_status_popup(self, employee_status, employee_id):
        style = ttk.Style()
        
        if employee_status == "Activo":
            style.configure("Status.TLabel", background="white", foreground="green")
        elif employee_status == "Inactivo":
            style.configure("Status.TLabel", background="white", foreground="red")

        if employee_status == "Activo":
            self.label_status_popup.config(text=f"✅{employee_status.upper()}")
        elif employee_status == "Inactivo":
            self.label_status_popup.config(text=f"❌{employee_status.upper()}")

        if employee_status == "Activo":
            # Let's calculate the last INACTIVO status with end_date = True
            data = employees_dao.get_inactive_status_data(employee_id, end_date=True)
            end_dates = []
            for item in data:
                end_dates.append(item[3].date()) 
            if len(end_dates) > 0:
                self.label_fecha_popup.config(text=f"Desde {max(end_dates)}")
            else:
                self.label_fecha_popup.config(text="Nunca ha estado inactivo")
        elif employee_status == "Inactivo": # If it's still INACTIVO, it must have an end_date = None
            data = employees_dao.get_inactive_status_data(employee_id, end_date=None)
            if data: # Must be always true, just in case
                motive = data[1]
                start_status_date = data[2].date()
                self.label_fecha_popup.config(text=f"Desde {start_status_date} por {motive}")
            else:
                print("Error en linea 515")
            
        self.change_status_combobox.set("")
        values = ["Activo", "Vacaciones", "Baja médica", "Excedencia", "Maternidad"]
        if employee_status == "Activo":
            values.remove("Activo")
        elif employee_status == "Inactivo" and motive != "Baja definitiva":
            values.remove(motive)
        self.change_status_combobox.config(values=values)

        self.change_status_btn["state"] = "disabled" # Until combobox is selected

        # UPDATE TREEVIEW
        for item in self.tree_inactivity_history.get_children():
            self.tree_inactivity_history.delete(item)
        data_from_db = employees_dao.get_inactivity_history(employee_id)
        for data in reversed(data_from_db):
            id = data[0]
            inactive_status = data[1]
            start_date = data[2].date()
            if data[3]:
                end_date = data[3].date()
            else:
                end_date = "ACTUAL"
            
            values_to_insert = [id, inactive_status, start_date, end_date]
            self.tree_inactivity_history.insert("", tk.END, values=values_to_insert)
        
        if employee_status != "Activo":
            if motive == "Baja definitiva":
                self.change_status_combobox["state"] = "disabled"
                self.change_status_btn["state"] = "disabled"
                return


    def employee_status_popup(self, employee_status):
        employee_status = employee_status.replace("[", "").replace("]", "")
        
        employee_id = int(self.tree_empleados.item(self.row_id, "values")[0])
        employee_name = self.tree_empleados.item(self.row_id, "values")[1]
        employee_work_data = employees_dao.get_employee_data(employee_id, work_data=True, priv_data=None)
        if not employee_work_data:
            messagebox.showerror(title="Error al acceder a los datos", 
                                    message=f"Ocurrió un error al intentar acceder a los datos del empleado con ID {employee_id}.")
            return
        
        self.popup_data = tk.Toplevel(bg="white")
        self.popup_data.title(f"Estado")
        self.popup_data.geometry("350x500+618+250")
        self.popup_data.resizable("False", "False")
        self.popup_data.grab_set()

        # Frame principal
        frame_contenido = ttk.Frame(self.popup_data, padding=20, style="White.TFrame")
        frame_contenido.pack(fill="both", expand=True)

        # Título superior
        titulo = ttk.Label(frame_contenido, text=f"Estado del empleado", font=("Segoe UI", 11, "bold"), style="White.TLabel")
        titulo.pack(anchor="center", pady=(0, 0))
        subtitulo = ttk.Label(frame_contenido, text=f"{employee_name}", font=("Segoe UI", 8), style="White.TLabel")
        subtitulo.pack(anchor="center", pady=(0, 10))

        # Separador visual
        separator = ttk.Separator(frame_contenido, orient="horizontal")
        separator.pack(fill="x", pady=(0, 10))

        # Subcontenedor para la info de fecha
        frame_status = ttk.Frame(frame_contenido, style="White.TFrame")
        frame_status.pack(fill="x", pady=(0, 10))

        # Etiqueta de campo
        self.label_status_popup = ttk.Label(frame_status, font=("Segoe UI", 11, "bold"), style="Status.TLabel")
        self.label_status_popup.pack()

        # Valor de la fecha
        self.label_fecha_popup = ttk.Label(frame_status, font=("Segoe UI", 8), style="White.TLabel")
        self.label_fecha_popup.pack()
                
        # Separador extra opcional
        separator2 = ttk.Separator(frame_contenido, orient="horizontal")
        separator2.pack(fill="x", pady=(0, 20))

        # Combobox
        self.change_status_combobox = ttk.Combobox(frame_contenido)
        self.change_status_combobox.pack()
        self.change_status_combobox.bind("<<ComboboxSelected>>", self.activate_popup_status_btn)

        # Change status button
        self.change_status_btn = ttk.Button(frame_contenido, text="🔁 Cambiar estado", style="Accent.TButton", 
                                            command=lambda: self.change_status(employee_id))
        self.change_status_btn.pack(pady=10)
        
        # Treeview - historial
        columnas_y_ancho = {
            "ID": 20,
            "Estado": 100,
            "Desde": 40,
            "Hasta": 40
        }
        title_treeview = ttk.Label(self.popup_data, text=f"Historial de inactividad", font=("Segoe UI", 10, "bold"), style="White.TLabel")
        title_treeview.pack(anchor="center", pady=(0, 0))

        self.tree_inactivity_history = ttk.Treeview(self.popup_data, columns=list(columnas_y_ancho.keys()), show="headings", height=10)
        for name, width in columnas_y_ancho.items():
            self.tree_inactivity_history.heading(name, text=name)
            self.tree_inactivity_history.column(name, width=width, anchor="center")
        self.tree_inactivity_history.pack(fill="both", expand=True)
        
        self.refresh_status_popup(employee_status, employee_id)

    def activate_popup_status_btn(self, event):
        self.change_status_btn["state"] = "normal"

    def change_status(self, employee_id):
        new_status = self.change_status_combobox.get()
        new_start_date = datetime.now().date()
        current_status = employees_dao.get_active_inactive_status(employee_id=employee_id)[0]
        open_inactive_status_data = employees_dao.get_inactive_status_data(employee_id, end_date=None)
        if open_inactive_status_data:
            open_status_id, open_employee_status, open_status_start_date = open_inactive_status_data
        
        if not new_status:
            messagebox.showerror(title="Selecciona una opción", 
                                 message="Debe seleccionar una opción para continuar.", 
                                 parent=self.popup_data)
            return
        elif current_status == "Activo": # Any option selected will be considered INACTIVO
            # Let's change the status to INACTIVO in the employees DB
            updated = employees_dao.update_status(employee_id, "Inactivo")
            if not updated:
                messagebox.showerror(title="Error al actualizar estado",
                                     message="Ocurrió un error al intentar actualizar el estado del empleado.", 
                                     parent=self.popup_data)
                return
        elif current_status == "Inactivo" and new_status == "Activo":
            # Let's change the status to Activo in the employees DB
            updated = employees_dao.update_status(employee_id, "Activo")
            if not updated:
                messagebox.showerror(title="Error al actualizar estado",
                                     message="Ocurrió un error al intentar actualizar el estado del empleado.", 
                                     parent=self.popup_data)
                return
        elif current_status == "Inactivo" and new_status != "Activo": #It must have a current inactive status with no end_date
            if not open_inactive_status_data: # It shouldn't be this way, just in case. If it's INACTIVO, it must have an open_inactive_status
                messagebox.showerror(title="Error en la consulta", 
                                     message="Al parecer no hay estados inactivos abiertos para este empleado.", 
                                     parent=self.popup_data)
                return
        
        if current_status == "Inactivo":
            # Let's close (update) the open_employee_status before creating a new one or before changing to ACTIVO
            updated = employees_dao.close_inactive_status_data(open_status_id, datetime.now().date())
            if not updated:
                messagebox.showerror(title="Error al actualizar datos", 
                                    message="Ocurrió un error al intentar cerrar el estado inactivo actual antes de crear uno nuevo.", 
                                    parent=self.popup_data)
                return
            if new_status == "Activo":
                self.refresh_status_popup(new_status, employee_id)
                messagebox.showinfo(title="Estado actualizado", 
                                    message="Se actualizó correctamente el estado del empleado a ACTIVO.", 
                                    parent=self.popup_data)
        
        # Let's create a new INACTIVO status
        if new_status != "Activo":
            values = [employee_id, new_status, new_start_date]
            inserted = employees_dao.insert_inactive_status_data(values)
            if not inserted:
                messagebox.showerror(title="Error al insertar nuevo estado", 
                                    message="Ocurrió un error al intentar insertar un nuevo estado INACTIVO del empleado.", 
                                    parent=self.popup_data)
                return
            self.refresh_status_popup("Inactivo", employee_id)
            messagebox.showinfo(title="Estado actualizado", 
                                message=f"Se actualizó correctamente el estado del empleado a INACTIVO por {new_status}.", 
                                parent=self.popup_data)
            
        self.refresh_interface()
        
    def refresh_contract_popup(self, employee_id):
        # GET EXISTING CONTRACT_FILE IN DB
        contract_data = employees_dao.get_contract_data(employee_id)
        if not contract_data:
            messagebox.showerror(title="Error al consultar datos",
                                 message="Ocurrió un error al intentar consultar los datos del contrato.")
            return
        contract_type, _, contract_end_date, employment_end_date, contract_filepath = contract_data
        
        self.btn_see_contract.pack(side="left", padx=(25, 0), pady=(0, 15))
        self.btn_see_contract.config(command=lambda: self.open_contract(contract_filepath))
        if not contract_filepath:
            self.btn_see_contract["state"] = "disabled"
            self.btn_delete_contract["state"] = "disabled"
        else:
            self.btn_see_contract["state"] = "normal"
            self.btn_delete_contract["state"] = "normal"

        if contract_filepath:
            self.btn_upload_contract.config(text="Actualizar", command=lambda: self.upload_file(employee_id, update=True))
        else:
            self.btn_upload_contract.config(text="Subir", command=lambda: self.upload_file(employee_id))
        self.btn_upload_contract.pack(side="left", padx=(10, 0), pady=(0, 15))

        self.btn_delete_contract.pack(side="left", padx=(10, 0), pady=(0, 15))
        self.btn_delete_contract.config(command=lambda: self.delete_contract(employee_id, contract_filepath))

        if contract_type == "Temporal":
            self.label_fecha.config(text=contract_end_date.date())
        elif contract_type == "Indefinido":
            self.label_fecha.config(text="Contrato indefinido")
        if employment_end_date:
            self.label_fecha.config(text=f"Relación laboral finalizada ({employment_end_date.date()})")
            self.btn_terminate.pack_forget()
            self.label_titulo.pack_forget()
            self.label_fecha.pack(side="top")
            self.btn_upload_contract["state"] = "disabled"
        else:
            self.btn_terminate.pack(side="right", padx=(0, 15))
            self.label_titulo.pack(side="left")
            self.label_fecha.pack(side="left")
            self.btn_upload_contract["state"] = "normal"
            
    def end_contract_popup(self, contract_type):
        contract_type = contract_type.replace("[", "").replace("]", "")
        employee_id = int(self.tree_empleados.item(self.row_id, "values")[0])
        employee_name = self.tree_empleados.item(self.row_id, "values")[1]
        employee_work_data = employees_dao.get_employee_data(employee_id, work_data=True, priv_data=None)
        if not employee_work_data:
            messagebox.showerror(title="Error al acceder a los datos", 
                                    message=f"Ocurrió un error al intentar acceder a los datos del empleado con ID {employee_id}.")
            return
        
        style = ttk.Style()
        style.configure("White.TFrame", background="white")
        style.configure("White.TLabel", background="white")

        self.popup_data = tk.Toplevel(bg="white")
        self.popup_data.title(f"Contrato")
        self.popup_data.geometry("300x200+618+310")
        self.popup_data.resizable("False", "False")
        self.popup_data.grab_set()

        # Main frame
        frame_contenido = ttk.Frame(self.popup_data, padding=20, style="White.TFrame")
        frame_contenido.pack(fill="both", expand=True)

        # Title
        titulo = ttk.Label(frame_contenido, text=f"Datos de contratación", font=("Segoe UI", 11, "bold"), style="White.TLabel")
        titulo.pack(anchor="center", pady=(0, 0))
        subtitulo = ttk.Label(frame_contenido, text=f"{employee_name}", font=("Segoe UI", 8), style="White.TLabel")
        subtitulo.pack(anchor="center", pady=(0, 10))

        # Separator
        separator = ttk.Separator(frame_contenido, orient="horizontal")
        separator.pack(fill="x", pady=(0, 10))

        # Subcontenedor para la info de fecha
        frame_fecha = ttk.Frame(frame_contenido, style="White.TFrame")
        frame_fecha.pack(fill="x", pady=(0, 10))

        self.label_titulo = ttk.Label(frame_fecha, text="Fin de contrato:", style="White.TLabel")
        
        # Date value
        self.label_fecha = ttk.Label(frame_fecha, style="White.TLabel")
        self.btn_terminate = ttk.Button(frame_fecha, text="❌", style="Cancel.TButton", width=3, 
                                        command=lambda: self.terminate_contract(employee_id))
        
        # Separator
        separator2 = ttk.Separator(frame_contenido, orient="horizontal")
        separator2.pack(fill="x", pady=(0, 10))

        # Buttons
        btn_frame = ttk.Frame(self.popup_data, style="White.TFrame")
        btn_frame.pack(fill="both", expand=True)

        self.btn_upload_contract = ttk.Button(btn_frame, text="⬆️ Subir", style="Accent.TButton")
        self.btn_see_contract = ttk.Button(btn_frame, text="🔍 Ver", style="Accent.TButton")
        self.btn_delete_contract = ttk.Button(btn_frame, text="🚮 Eliminar", style="Accent.TButton")
        
        self.refresh_contract_popup(employee_id)
    
    
    def terminate_contract(self, employee_id):
        confirmation = messagebox.askokcancel(title="Terminar relación laboral", 
                                              message="Va a terminar la relación laboral. Este proceso no tiene vuelta atrás." 
                                              "¿Realmente quiere continuar?",
                                              parent=self.popup_data)
        if not confirmation:
            return
        terminated = employees_dao.terminate_contract(employee_id, datetime.now().date())
        if not terminated:
            messagebox.showerror(title="Ocurrió un error",
                                 message="Ocurió un error al intentar cerrar el contrato.",
                                 parent=self.popup_data)
            return
        
        inactive = employees_dao.get_inactive_status_data(employee_id)
        if inactive: # We need to close first the current INACTIVO status
            print(inactive)
            if inactive[0]:
                status_id, employee_status, status_start_date = inactive
                closed = employees_dao.close_inactive_status_data(status_id, datetime.now().date())
                if not closed:
                    messagebox.showerror(title="Error al actualizar estado",
                                        message="Ocurrió un error al intentar actualizar el estado del empleado.",
                                        parent=self.popup_data)
                    return
        values = (employee_id, "Baja definitiva", datetime.now().date())
        inserted = employees_dao.insert_inactive_status_data(values)
        if not inserted:
            messagebox.showerror(title="Error al actualizar estado",
                                 message="Ocurrió un error al intentar actualizar el estado del empleado.",
                                 parent=self.popup_data)
            return

        messagebox.showinfo(title="Relación laboral terminada",
                            message="Se cerró correctamente el contrato laboral con el empleado.",
                            parent=self.popup_data)
                
        self.refresh_interface()
        self.refresh_contract_popup(employee_id)
        
    def delete_contract(self, employee_id, contract_filepath):
                                              
        confirmation = messagebox.askokcancel(title="Eliminar contrato",
                                              message="Se va a eliminar completamente el contrato. ¿Realmente quiere continuar?",
                                              parent=self.popup_data)
        if not confirmation:
            return
        try:
            if os.path.exists(contract_filepath):
                os.remove(contract_filepath)
        except Exception as e:
            messagebox.showwarning(title="El archivo no existe",
                                   message="Se intentó eliminar el archivo PDF pero no se pudo encontrar." \
                                   "Se procederá con el borrado en la Base de Datos.",
                                   parent=self.popup_data)
            return
        finally:
            updated = employees_dao.update_contract_path(employee_id)
            if not updated:
                messagebox.showerror(title="Error al eliminar contrato", 
                                    message="Ocurrió un error al intentar eliminar el contrato.",
                                    parent=self.popup_data)
            messagebox.showinfo(title="Contrato eliminado", 
                                message="El contrato fue eliminado correctamente.",
                                parent=self.popup_data)
            
            self.refresh_interface()
            self.refresh_contract_popup(employee_id)
        

    def upload_file(self, employee_id, update=None):
        try:
            file_path = filedialog.askopenfilename(
                title="Seleccionar archivo PDF",
                filetypes=[("Archivos PDF", "*.pdf")],
                defaultextension=".pdf",
                parent=self.popup_data
            )
        except Exception as e:
            print(e)
            messagebox.showerror(title="Error al abrir el explorador de archivos", 
                                 message="Ocurrió un error al intentar abrir el explorador de archivos para cargar el contrato.",
                                 parent=self.popup_data)
            return
        else:
            if file_path:
                if not update:
                    confirmation = messagebox.askokcancel(title="Guardar contrato",
                                                      message="Se va a guardar el contrato en la base de datos. ¿Quiere continuar?",
                                                      parent=self.popup_data)
                else:
                    confirmation = messagebox.askokcancel(title="Actualizar contrato",
                                                      message="Se va a actualizar el contrato en la base de datos. ¿Quiere continuar?",
                                                      parent=self.popup_data)
                if not confirmation:
                    return
                _, extension = os.path.basename(file_path).split(".")
                destiny_folder = os.path.join("media", "contratos_empleados")
                try:
                    os.makedirs(destiny_folder, exist_ok=True)
                except Exception as e:
                    print(e)
                    messagebox.showerror(title="Error al crear la carpeta", 
                                 message="Ocurrió un error al intentar crear la carpeta para guardar el contrato.",
                                 parent=self.popup_data)
                    return
                else:
                    file_name = f"Contrato_laboral_empleado_{employee_id}.{extension}" # PERSONALIZAR NOMBRE
                    destiny_path = os.path.join(destiny_folder, file_name)
                    if update: # Let's get the filepath and delete first the old file
                        if os.path.exists(destiny_path):
                            os.remove(destiny_path)
                    try:
                        shutil.copy(file_path, destiny_path)
                    except Exception as e:
                        print(e)
                        messagebox.showerror(title="Error al copiar el archivo", 
                                    message="Ocurrió un error al intentar copiar el archivo a la carpeta de destino.",
                                    parent=self.popup_data)
                        return
                    else:
                        # INSERT (update) contract_filepath into DB
                        inserted = employees_dao.update_contract_path(employee_id, contract_path=destiny_path)
                        if not inserted:
                            if not update:
                                messagebox.showerror(title="Error al guardar el contrato", 
                                                    message="Ocurrió un error al intentar guardar el contrato en la Base de Datos.",
                                                    parent=self.popup_data)
                                return
                            else:
                                messagebox.showerror(title="Error al actualizar el contrato", 
                                                    message="Ocurrió un error al intentar actualizar el contrato en la Base de Datos.",
                                                    parent=self.popup_data)
                                return
                        if not update:
                            messagebox.showinfo(title="Contrato guardado", 
                                                message="Se guardó correctamente el contrato en la Base de Datos.",
                                                parent=self.popup_data)
                        else:
                            messagebox.showinfo(title="Contrato actualizado", 
                                                message="Se actualizó correctamente el contrato en la Base de Datos.",
                                                parent=self.popup_data)
                       
                        self.refresh_interface()
                        self.refresh_contract_popup(employee_id)

    def open_contract(self, contract_filepath):
        try:
            if platform.system() == "Darwin":  # macOS
                subprocess.call(("open", contract_filepath))
            elif platform.system() == "Linux":
                subprocess.call(("xdg-open", contract_filepath))
            elif platform.system() == "Windows":
                os.startfile(contract_filepath)
        except Exception as e:
            print(e)
            messagebox.showerror(title="Error al intentar cargar el archivo", 
                                 message="Ocurrió un error al intentar cargar el archivo para mostrarlo.")
            return


    def edit_employee_data(self):
        selection = self.tree_empleados.selection()
        if not selection or len(selection) > 1:
            messagebox.showwarning(title="Seleccione un empleado", message="Debe seleccionar exactamente un empleado para editar sus datos.")
            return
        
        employee_id = int(self.tree_empleados.item(selection, "values")[0])
        data_from_db = employees_dao.get_employee_data(employee_id)
        
        name = data_from_db[1]
        personal_id = data_from_db[2]
        phone = data_from_db[3]
        email = data_from_db[4]
        address = data_from_db[5]
        position = data_from_db[6]
        work_shift = data_from_db[7]
        contract_type = data_from_db[8]
        week_hours = data_from_db[9]
        salary = data_from_db[10]
        entry_time = data_from_db[11]
        exit_time = data_from_db[12]
        employee_status = data_from_db[13]
        employment_start_date = data_from_db[14]
        employment_end_date = data_from_db[15]
        contract_end_date = data_from_db[16]

        # Entry time and exit time are saved in DB as timedelta. I don't know why! So we need to convert it to string
        entry_time = self.timedelta_to_string(entry_time)
        exit_time = self.timedelta_to_string(exit_time)

        # Let's convert employment_start_date and contract_end_date to string
        employment_start_date = datetime.strftime(employment_start_date, "%d/%m/%Y")
        if contract_end_date:
            contract_end_date = datetime.strftime(contract_end_date, "%d/%m/%Y")


        # Insert data to left panel
        self.nombre_entry.insert(0, name)
        self.cargo_entry.insert(0, position)
        self.id_entry.insert(0, personal_id)
        self.telefono_entry.insert(0, phone)
        self.email_entry.insert(0, email)
        self.direccion_entry.insert(0, address)
        self.jornada_combobox.set(work_shift)
        self.horas_semana_entry.insert(0, week_hours)
        self.salary_entry.insert(0, salary)
        self.check_in_hour_combobox.set(entry_time)
        self.check_out_hour_combobox.set(exit_time)
        self.contract_type_combobox.set(contract_type)
        self.start_date_entry.insert(0, employment_start_date)
        if contract_end_date:
            self.end_contract_entry["state"] = "normal"
            self.end_contract_entry.insert(0, contract_end_date)

        self.add_employee_btn.config(text="Guardar cambios", command=lambda: self.add_employee(update_id=employee_id))
        self.del_employee_btn.config(text="Cancelar edición", command=self.refresh_left_panel)
        self.edit_employee_btn.config(state="disabled")
        
    def timedelta_to_string(self, time):
        if not isinstance(time, timedelta):
            return time
        time = time.seconds
        hours = time // 3600
        min = (time % 3600) // 60
        return f"{hours:02d}:{min:02d}"