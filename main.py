import tkinter as tk
from tkinter import ttk, messagebox
from interface.MainWindow import MainWindow
from database.connection import *
import bcrypt
from decimal import Decimal, ROUND_HALF_UP

from datetime import datetime, timedelta
from config.services import users_dao, employees_dao


class LoginWindow:
    employee_id = None
    def __init__(self, master, on_success, first_user=None):
        self.first_user = first_user
        self.master = master
        if not self.first_user:
            self.master.title("Login")
        else:
            self.master.title("Crear usuario ADMIN")
        self.master.geometry("400x300+550+200")
        self.master.configure(bg="#f3f4f6")
        self.master.resizable(False, False)
        self.on_success = on_success  # función a ejecutar si login OK
        self.attempts_remaining = 2

        if not self.first_user:
            self.create_widgets()
        else:
            self.create_first_user()

 
    def create_first_user(self):

        def clean_entrys():
            self.employee_combobox.set("")
            password_entry.delete(0, tk.END)
        
        def create_user():
            employee = self.employee_combobox.get()
            role = role_combobox.get()
            password = password_entry.get()
            
            if not employee or not role or not password:
                messagebox.showwarning(title="Rellene los campos faltantes", 
                                    message="Debe rellenar todos los datos solicitados.",
                                    parent=self.master)
                clean_entrys()
                return
            
            if employee == "__Nuevo empleado__":
                check_new_employee()
                return
            
            employee_id = int(employee.split(":")[1].replace(")", "").strip())
            employee_data = employees_dao.get_employee_data(employee_id, priv_data=True)
            _, employee, _, _, user_email, _ = employee_data
                
                        
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
                                    parent=self.master)
                return
            
            if password:
                password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            else:
                password_hash = None
            
            values = (employee_id, user_email, password_hash, role)
            inserted = users_dao.create_user(values)
            
            
            if not inserted:
                messagebox.showerror(title="Error al crear usuario",
                                    message="Ocurrió un error al intentar crear el usuario.",
                                    parent=self.master)
                return
            messagebox.showinfo("Usuario creado", message="Se creó el usuario correctamente.",
                                parent=self.master)
            
            self.employee_id = employee_id
            self.master.destroy()
            start_main_window(self.employee_id)      

        def check_new_employee(event=None):
            if not self.employee_combobox.get() == "__Nuevo empleado__":
                return
            
            # POPUP
            self.popup_new_employee = tk.Toplevel(self.master)
            self.popup_new_employee.title("Crear nuevo empleado")
            self.popup_new_employee.geometry("470x580")
            main = tk.Frame(self.popup_new_employee, bg="#edf2f7")
            main.pack(fill="both", expand=True)

            # ----- FORM CARD -----
            form_card = tk.Frame(main, bg="white", relief="flat", padx=10)
            form_card.place(x=20, y=20, width=420, height=500)


            # Entradas generales
            def create_labels_entrys(attr_name, label_text):
                frame = tk.Frame(form_card, bg="white")
                frame.pack(fill="x", padx=0, pady=5)
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
            btn_frame.place(x=20, y=530, width=400, height=50)
            
            self.add_employee_btn = ttk.Button(btn_frame, text="Agregar empleado", style="Accent.TButton", command=self.add_employee)
            self.add_employee_btn.pack(side="left", padx=5, pady=10, expand=True)
            
        
        style = ttk.Style()
        style.configure("White.TFrame", background="white")
        style.configure("White.TLabel", background="white")

        # === Frame contenedor general ===
        form_frame = ttk.Frame(self.master, style="White.TFrame")
        form_frame.pack(fill="both", expand=True)
        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(2, weight=1)


        label_title = ttk.Label(form_frame, text="Cree un usuario ADMIN", font=("Segoe UI", 11, "bold"), style="White.TLabel", anchor="e")
        label_title.grid(row=0, column=0, columnspan=2, sticky="n", pady=(25, 30))

        # === Empleado ===
        label_employee = ttk.Label(form_frame, text="Empleado:", font=("Segoe UI", 11), style="White.TLabel", anchor="e")
        label_employee.grid(row=1, column=0, sticky="e", padx=(30, 10), pady=(0, 15))
        self.employee_combobox = ttk.Combobox(form_frame, state="readonly")
        self.employee_combobox.grid(row=1, column=1, sticky="w", padx=20, pady=(0, 15))
        self.employee_combobox.bind("<<ComboboxSelected>>", check_new_employee)

        # === Empleado VALUES ===

        employees = employees_dao.get_all_employees()
        if employees:
            values = []
            for data in employees:
                id, name = data[0], data[1]
                values.append((f"{name} (ID: {id})"))
            values.append("__Nuevo empleado__")
        else:
            values = ["__Nuevo empleado__"]
        
        self.employee_combobox.config(values=values)


        # === Rol ===
        label_rol = ttk.Label(form_frame, text="Rol:", font=("Segoe UI", 11), style="White.TLabel", anchor="e")
        label_rol.grid(row=3, column=0, sticky="e", padx=(30, 10), pady=(0, 15))

        role_combobox = ttk.Combobox(form_frame, state="readonly")
        role_combobox.grid(row=3, column=1, sticky="w", padx=20)
        role_combobox.set("Admin")
        role_combobox["state"] = "disabled"

       # === Password ===
        label_password = ttk.Label(form_frame, text="Contraseña:", font=("Segoe UI", 11), style="White.TLabel", anchor="e")
        label_password.grid(row=5, column=0, sticky="e", padx=(30, 10), pady=(0, 15))

        password_entry = ttk.Entry(form_frame, show="*")
        password_entry.grid(row=5, column=1, sticky="w", padx=20)

        # === Boton CREAR ===
        create_btn = ttk.Button(form_frame, text="Crear usuario", style="Accent.TButton", command=create_user)
        create_btn.grid(row=7, column=1, sticky="w", padx=20, pady=(30, 15))


    def check_contract_type(self, event=None):
        if self.contract_type_combobox.get() == "Temporal":
            self.end_contract_entry["state"] = "normal"
        else:
            self.end_contract_entry.delete(0, tk.END)
            self.end_contract_entry["state"] = "disabled"

    def create_widgets(self):
        frame = tk.Frame(self.master, bg="white", bd=2, relief="flat")
        frame.place(relx=0.5, rely=0.5, anchor="center", width=300, height=200)

        tk.Label(frame, text="Iniciar sesión", font=("Segoe UI", 14, "bold"), bg="white", fg="#111827").pack(pady=(15, 10))

        tk.Label(frame, text="Email", font=("Segoe UI", 10), bg="white", anchor="w", fg="#374151").pack(fill="x", padx=20)
        self.user_entry = tk.Entry(frame)
        self.user_entry.pack(fill="x", padx=20, pady=(0, 10))

        tk.Label(frame, text="Contraseña", font=("Segoe UI", 10), bg="white", anchor="w", fg="#374151").pack(fill="x", padx=20)
        self.pass_entry = tk.Entry(frame, show="*")
        self.pass_entry.pack(fill="x", padx=20, pady=(0, 20))

        tk.Button(frame, text="Ingresar", bg="#3B82F6", fg="white",
                  font=("Segoe UI", 10, "bold"), bd=0, relief="flat", cursor="hand2",
                  activebackground="#2563EB", activeforeground="white",
                  command=self.check_login).pack(pady=(0, 10), ipadx=10, ipady=4)
        
    def add_employee(self):
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
            messagebox.showwarning(title="Faltan datos", message="Por favor, complete los datos que faltan en el formulario.",
                                   parent=self.popup_new_employee)
            return
        
        state = str(self.end_contract_entry.cget("state")).lower().strip()
        if state == "normal" and not end_date:
            messagebox.showwarning(title="Faltan datos", message="Por favor, complete los datos que faltan en el formulario.",
                                   parent=self.popup_new_employee)
            return
               
        try:
            week_hours = int(week_hours)
        except Exception:
            messagebox.showerror(title="Error de datos", message="Las horas semanales deben ser un número entero.",
                                 parent=self.popup_new_employee)
            return
        else:
            if week_hours < 1:
                messagebox.showerror(title="Error de datos", message="Las horas semanales deben ser un número mayor que 0.",
                                     parent=self.popup_new_employee)
                return
        
        try:
            salary = Decimal(salary).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        except Exception:
            messagebox.showerror(title="Error de datos", message="El salario debe ser un número entero o decimal.",
                                 parent=self.popup_new_employee)
            return
        else:
            if salary <= 0:
                messagebox.showerror(title="Error de datos", message="El salario debe ser un número mayor que 0.",
                                     parent=self.popup_new_employee)
                return
        
        
        if ":" not in entry_time:
            messagebox.showerror(title="Error de datos", message="La hora de entrada debe tener un formato 'HH:MM'.",
                                 parent=self.popup_new_employee)
            return
        hour, min = entry_time.split(":")
        hour = int(hour)
        
        try:
            datetime.strptime(entry_time, "%H:%M")
        except ValueError:
            messagebox.showerror(title="Error de datos", message="La hora de entrada debe tener un formato 'HH:MM' válido (00:00 a 23:59).",
                                 parent=self.popup_new_employee)
            return
        else:
            _, min = entry_time.split(":")
            if len(min) < 2:
                messagebox.showerror(title="Error de datos", message="Los minutos de la hora de entrada deben tener dos dígitos.",
                                     parent=self.popup_new_employee)
                return
            try:
                entry_time_obj = datetime.strptime(entry_time, "%H:%M").time()
            except ValueError:
                messagebox.showerror(title="Error de datos", message="La hora de entrada debe tener un formato 'HH:MM' válido (00:00 a 23:59).",
                                     parent=self.popup_new_employee)
                return
       
        try:
            datetime.strptime(exit_time, "%H:%M")
        except ValueError:
            messagebox.showerror(title="Error de datos", message="La hora de salida debe tener un formato 'HH:MM' válido (00:00 a 23:59).",
                                 parent=self.popup_new_employee)
            return
        else:
            _, min = exit_time.split(":")
            if len(min) < 2:
                messagebox.showerror(title="Error de datos", message="Los minutos de la hora de salida deben tener dos dígitos.",
                                     parent=self.popup_new_employee)
                return
            try:
                exit_time_obj = datetime.strptime(exit_time, "%H:%M").time()
            except ValueError:
                messagebox.showerror(title="Error de datos", message="La hora de salida debe tener un formato 'HH:MM' válido (00:00 a 23:59).",
                                     parent=self.popup_new_employee)
                return
            
        try:
            start_date_obj = datetime.strptime(start_date, "%d/%m/%Y").date()
        except Exception:
            messagebox.showerror(title="Error de formato", message="La fecha de alta debe tener un formato correcto ('DD/MM/YYYY').",
                                 parent=self.popup_new_employee)
            return
        else:
            if start_date_obj > datetime.now().date():
                messagebox.showerror(title="Error en la fecha", message="La fecha de alta debe ser anterior a la fecha actual.",
                                     parent=self.popup_new_employee)
                return
        
        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, "%d/%m/%Y").date()
            except Exception:
                messagebox.showerror(title="Error de formato", message="La fecha de fin de contrato debe tener un formato correcto ('DD/MM/YYYY').",
                                     parent=self.popup_new_employee)
                return
            else:
                if end_date_obj < datetime.now().date():
                    messagebox.showerror(title="Error en la fecha", message="La fecha de fin de contrato debe ser posterior a la fecha actual.",
                                         parent=self.popup_new_employee)
                    return
        
        
        data_exists = employees_dao.get_employee_by_data(email=email, personal_id=personal_id, name=name)
        if data_exists == "email":
            messagebox.showwarning(title="Email ya existe", message="Ya existe este email registrado para un usuario en la Base de Datos.",
                                   parent=self.popup_new_employee)
            return
        elif data_exists == "personal_id":
            messagebox.showwarning(title="ID Personal ya existe", 
                                   message="Ya existe este ID Personal registrado para un usuario en la Base de Datos.",
                                   parent=self.popup_new_employee)
            return
        elif isinstance(data_exists, tuple):
            _, quantity = data_exists
            if quantity == 1:
                confirmation = messagebox.askokcancel(title="Existe un nombre igual", 
                                    message="Ya existe un usuario con este mismo nombre aunque. ¿Quiere añadirlo igualmente?",
                                    parent=self.popup_new_employee)
            elif quantity > 1:
                confirmation = messagebox.askokcancel(title="Existen varios nombres iguales", 
                                    message=f"Ya existen {quantity} usuarios con este mismo nombre. ¿Quiere añadirlo igualmente?",
                                    parent=self.popup_new_employee)
            if not confirmation:
                return
        elif data_exists == "error":
            messagebox.showerror(title="Error al comparar datos", 
                                message="Ocurrió un error intentando comparar los datos a ingresar con los datos en la Base de Datos.",
                                parent=self.popup_new_employee)
            return

        # ---------- INSERTING TO DATABASE ---------- #
        
        employee_status = "Activo" # By default
        values_to_insert = (name, personal_id, phone, email, address, position, work_shift, contract_type,
                        week_hours, salary, entry_time_obj, exit_time_obj, employee_status, start_date_obj)
                
        if end_date:
            inserted = employees_dao.insert_employee(values_to_insert, end_contract=end_date_obj)
        else:
            inserted = employees_dao.insert_employee(values=values_to_insert, end_contract=None)
        
        
        if not inserted:
            messagebox.showerror(title="Error al insertar empleado", 
                                message="Ocurrió un error al intentar insertar los datos del empleado en la Base de Datos.",
                                parent=self.popup_new_employee)
            return
        
        messagebox.showinfo(title="Empleado insertado", message="Se insertaron correctamente los datos del empleado en la Base de Datos.",
                            parent=self.popup_new_employee)
        
        self.employee_combobox.set(f"{name} (ID: {inserted})")
        self.employee_combobox["state"] = "disabled"
        self.popup_new_employee.destroy()
        
        

    def check_login(self):
        username = self.user_entry.get()
        password = self.pass_entry.get()
        
        if not username or not password:
            messagebox.showwarning("Complete todos los campos", "Por favor, complete los campos de usuario y contraseña requeridos para iniciar sesión.")
            return
        user_data = users_dao.get_user_data(email=username)
        
        if user_data:
            user_data = list(user_data)
            LoginWindow.employee_id = user_data[0]
            password_hash = user_data[1]
        else:
            password_hash = None
            
        if self.attempts_remaining:
            if password_hash:
                if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
                    self.master.destroy()  # cerrar login
                    self.on_success()      # lanzar MainWindow
                    return
            else:
                messagebox.showerror("Error", f"Email o contraseña incorrecta. Intentos restantes: {self.attempts_remaining}")
                self.attempts_remaining -= 1
                self.user_entry.delete(0, tk.END)
                self.pass_entry.delete(0, tk.END)
                return
        else:
            messagebox.showerror("Error", "Email o contraseña incorrecta. Ha alcanzado el número máximo de intentos. Contacte con el administrador de sistemas.")
            self.user_entry.delete(0, tk.END)
            self.pass_entry.delete(0, tk.END)
            return
        
        self.master.destroy()  # cerrar login
        self.on_success()      # lanzar MainWindow

try:
    connection_db = Database()
    connection_db.connect_db()
except Exception as e:
    print(e)
    messagebox.showerror("Error al conectar a la BBDD", 
                         "Ocurrió un error al intentar conectar a la Base de Datos. Contacte con su administrador de sistemas.")
else:
    if __name__ == "__main__":
        def start_login_window():
            root_main.destroy()
            launch()

        def start_main_window(employee_id):
            global root_main
            root_main = tk.Tk()
            
            app = MainWindow(root_main, employee_id, on_logout=lambda: start_login_window())
            root_main.mainloop()
        
        def launch():
            user_exist = users_dao.get_user_data()
            if len(user_exist) < 1:
                FIRST_USER = True
            else:
                FIRST_USER = None
            login_root = tk.Tk()
            LoginWindow(login_root, on_success=lambda: start_main_window(LoginWindow.employee_id), first_user=FIRST_USER)
            login_root.mainloop()
        
        launch()
            
            
