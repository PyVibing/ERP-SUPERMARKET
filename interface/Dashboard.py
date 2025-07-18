import os, sys
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from config.config import *
from config.services import sales_dao, employees_dao, product_dao
from decimal import Decimal, ROUND_HALF_UP
import PIL
import matplotlib
matplotlib.use('TkAgg')
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

       
class Dashboard(tk.Frame):
    def __init__(self, parent, employee_id):
        self.dashboard_main_frame = parent
        self.dashboard_main_frame.config(bg="white")
        self.name = employees_dao.get_employee_data(employee_id)[1].split()[0]
        self.build_interface()
        
    def build_interface(self):
        def create_rounded_rect(canvas, x1, y1, x2, y2, radius=20, **kwargs):
            points = [
                x1 + radius, y1,
                x2 - radius, y1,
                x2, y1,
                x2, y1 + radius,
                x2, y2 - radius,
                x2, y2,
                x2 - radius, y2,
                x1 + radius, y2,
                x1, y2,
                x1, y2 - radius,
                x1, y1 + radius,
                x1, y1
            ]
            return canvas.create_polygon(points, smooth=True, **kwargs)

        self.x_margin = 20
        self.card_width = 220
        self.spacing = 35
        self.content_top_cards_font = ("Segoe UI Semibold", 26)
        self.title_card_font = ("Segoe UI Semibold", 10)
        self.content_card_font = ("Segoe UI Semibold", 12)


        self.icon_label = tk.Label(self.dashboard_main_frame, bg="white", fg="#333")
        
        self.welcome_label = tk.Label(self.dashboard_main_frame, font=("Segoe UI Semibold", 16), bg="white", fg="#333")
        self.welcome_label.place(x=self.x_margin + 40, y=40)
        
        card_bg = "white"
        metrics = [
            "Ingresos de hoy",
            "Ingresos de esta semana",
            "Sin stock",
            "Productos vendidos hoy",
            "Pérdida mensual por merma"
        ]
        self.top_cards = {}
        for i, (label) in enumerate(metrics):
            canvas = tk.Canvas(self.dashboard_main_frame, width=self.card_width, height=140, bg="white", highlightthickness=0)
            canvas.place(x=self.x_margin + i * (self.card_width + self.spacing), y=90)
            create_rounded_rect(canvas, 0, 0, self.card_width - 1, 138, radius=20, fill=card_bg, outline="#D6EAF8")
            canvas.create_text(20, 20, anchor="nw", text=label, font=self.title_card_font, fill="#1D3557")
            id = canvas.create_text(175, 50, anchor="ne", text="", font=self.content_top_cards_font)
            self.top_cards[label] = (canvas, id)
        
        
        
        self.income_canvas = tk.Canvas(self.dashboard_main_frame, width=600, height=200, bg="white", highlightthickness=0)
        self.income_canvas.place(x=self.x_margin, y=260)
        create_rounded_rect(self.income_canvas, 0, 0, 598, 198, radius=20, fill=card_bg, outline="#D6EAF8")
        self.income_canvas.create_text(20, 20, anchor="nw", text="Ingresos brutos por meses", font=self.title_card_font, fill="#1D3557")
        self.income_today_content = self.income_canvas.create_text(250, 100, font=self.content_card_font, fill="#888")

        self.category_canvas = tk.Canvas(self.dashboard_main_frame, width=600, height=200, bg="white", highlightthickness=0)
        self.category_canvas.place(x=self.x_margin + 610 + self.spacing, y=260)
        create_rounded_rect(self.category_canvas, 0, 0, 598, 198, radius=20, fill=card_bg, outline="#D6EAF8")
        self.category_canvas_id = self.category_canvas.create_text(20, 20, anchor="nw", text="Ventas por categoría mes/año", font=self.title_card_font, fill="#1D3557")
                       
        sold_prod_today_canvas = tk.Canvas(self.dashboard_main_frame, width=430, height=200, bg="white", highlightthickness=0)
        sold_prod_today_canvas.place(x=self.x_margin, y=490)
        create_rounded_rect(sold_prod_today_canvas, 0, 0, 428, 198, radius=20, fill=card_bg, outline="#D6EAF8")
        tk.Label(self.dashboard_main_frame, text="Productos de mayor ingreso - Hoy", 
                 font=self.title_card_font, bg="white", fg="#1D3557").place(x=self.x_margin + 20, y=500)
        self.sold_prod_today_treeview = ttk.Treeview(self.dashboard_main_frame, 
                                                     columns=("Producto", "Ingresos", "Respecto a ayer"), show="headings", height=5)
        for col in self.sold_prod_today_treeview["columns"]:
            self.sold_prod_today_treeview.heading(col, text=col)
            self.sold_prod_today_treeview.column(col, width=130)
        self.sold_prod_today_treeview.place(x=self.x_margin + 20, y=540)
        
        sold_prod_month_treeview = tk.Canvas(self.dashboard_main_frame, width=430, height=200, bg="white", highlightthickness=0)
        sold_prod_month_treeview.place(x=self.x_margin + 440 + self.spacing-10, y=490)
        create_rounded_rect(sold_prod_month_treeview, 0, 0, 423, 198, radius=20, fill=card_bg, outline="#D6EAF8")
        tk.Label(self.dashboard_main_frame, text="Productos de mayor ingreso - Este mes", 
                 font=self.title_card_font, bg="white", fg="#1D3557").place(x=self.x_margin + 425 + self.spacing + 20, y=500)
        self.sold_prod_month_treeview = ttk.Treeview(self.dashboard_main_frame, columns=("Producto", "Ingresos", "Respecto mes anterior"), show="headings", height=5)
        for col in self.sold_prod_month_treeview["columns"]:
            self.sold_prod_month_treeview.heading(col, text=col)
            self.sold_prod_month_treeview.column(col, width=130)
        self.sold_prod_month_treeview.place(x=self.x_margin + 480, y=540)
    
        # --- TOP PROVIDERS ---
        self.top_employees_canvas = tk.Canvas(self.dashboard_main_frame, width=355, height=200, bg="white", highlightthickness=0)
        self.top_employees_canvas.place(x=self.x_margin-10 + 900, y=490)
        create_rounded_rect(self.top_employees_canvas, 40, 0, 353, 198, radius=20, fill=card_bg, outline="#D6EAF8")
        self.top_employees_canvas.create_text(50, 20, anchor="nw", text="Top Empleados - Ventas mes", font=self.title_card_font, fill="#1D3557")

        self.top_employees_text_id = []
        # Top 1
        self.top1_employee_id = self.top_employees_canvas.create_text(0, 0, anchor="nw", text="", font=self.content_card_font, fill="#000000")
        self.top1_employee_name = self.top_employees_canvas.create_text(0, 0, anchor="nw", text="", font=self.content_card_font, fill="#0A770C")
        self.top1_employee_sales = self.top_employees_canvas.create_text(0, 0, anchor="ne", text="", font=self.content_card_font, fill="#0A770C")
        self.top_employees_text_id.append((self.top1_employee_id, self.top1_employee_name, self.top1_employee_sales))
        # Top 2
        self.top2_employee_id = self.top_employees_canvas.create_text(0, 0, anchor="nw", text="", font=self.content_card_font, fill="#000000")
        self.top2_employee_name = self.top_employees_canvas.create_text(0, 0, anchor="nw", text="", font=self.content_card_font, fill="#0A770C")
        self.top2_employee_sales = self.top_employees_canvas.create_text(0, 0, anchor="ne", text="", font=self.content_card_font, fill="#0A770C")
        self.top_employees_text_id.append((self.top2_employee_id, self.top2_employee_name, self.top2_employee_sales))
        # Top 3
        self.top3_employee_id = self.top_employees_canvas.create_text(0, 0, anchor="nw", text="", font=self.content_card_font, fill="#000000")
        self.top3_employee_name = self.top_employees_canvas.create_text(0, 0, anchor="nw", text="", font=self.content_card_font, fill="#0A770C")
        self.top3_employee_sales = self.top_employees_canvas.create_text(0, 0, anchor="ne", text="", font=self.content_card_font, fill="#0A770C")
        self.top_employees_text_id.append((self.top3_employee_id, self.top3_employee_name, self.top3_employee_sales))
        # Top 4
        self.top4_employee_id = self.top_employees_canvas.create_text(0, 0, anchor="nw", text="", font=self.content_card_font, fill="#000000")
        self.top4_employee_name = self.top_employees_canvas.create_text(0, 0, anchor="nw", text="", font=self.content_card_font, fill="#0A770C")
        self.top4_employee_sales = self.top_employees_canvas.create_text(0, 0, anchor="ne", text="", font=self.content_card_font, fill="#0A770C")
        self.top_employees_text_id.append((self.top4_employee_id, self.top4_employee_name, self.top4_employee_sales))
        # Top 5
        self.top5_employee_id = self.top_employees_canvas.create_text(0, 0, anchor="nw", text="", font=self.content_card_font, fill="#000000")
        self.top5_employee_name = self.top_employees_canvas.create_text(0, 0, anchor="nw", text="", font=self.content_card_font, fill="#0A770C")
        self.top5_employee_sales = self.top_employees_canvas.create_text(0, 0, anchor="ne", text="", font=self.content_card_font, fill="#0A770C")
        self.top_employees_text_id.append((self.top5_employee_id, self.top5_employee_name, self.top5_employee_sales))
        
        

# ----------- METODOS AUXILIARES ----------- #
    def refresh_interface(self):
        self.set_welcome()
        self.show_today_income()
        self.show_week_income()
        self.show_no_stock()
        self.show_sold_prods_today()
        self.show_lost_prods()
        self.show_more_sold_prods_today()
        self.show_more_sold_prods_month()
        self.show_top_employees()
        self.show_category_graph()
        self.show_year_gross_income()

    def set_welcome(self):
        def resource_path(relative_path):
            """ Obtiene la ruta absoluta al recurso, funcionando en desarrollo y en el ejecutable PyInstaller """
            try:
                # PyInstaller crea un atributo temporal _MEIPASS donde pone los archivos
                base_path = sys._MEIPASS
            except Exception:
                base_path = os.path.abspath(".")

            return os.path.join(base_path, relative_path)
        
        icon_morning_path = resource_path(os.path.join("media", "icons", "morning.png"))
        icon_morning = Image.open(icon_morning_path)
        icon_morning = icon_morning.resize((34, 34), Image.Resampling.LANCZOS)
        self.icon_morning = ImageTk.PhotoImage(icon_morning)
        icon_afternoon_path = resource_path(os.path.join("media", "icons", "afternoon.png"))
        icon_afternoon = Image.open(icon_afternoon_path)
        icon_afternoon = icon_afternoon.resize((24, 24), Image.Resampling.LANCZOS)
        self.icon_afternoon = ImageTk.PhotoImage(icon_afternoon)
        icon_night_path = resource_path(os.path.join("media", "icons", "night.png"))
        icon_night = Image.open(icon_night_path)
        icon_night = icon_night.resize((20, 20), Image.Resampling.LANCZOS)
        self.icon_night = ImageTk.PhotoImage(icon_night)

        if datetime.now().hour >= 6 and datetime.now().hour < 13:
            self.welcome_label.config(text=f"Buenos días, {self.name}")
            self.icon_label.config(image=self.icon_morning)
            self.icon_label.place(x=self.x_margin, y=40)
        elif datetime.now().hour >= 13 and datetime.now().hour < 20:
            self.welcome_label.config(text=f"Buenas tardes, {self.name}")
            self.icon_label.config(image=self.icon_afternoon)
            self.icon_label.place(x=self.x_margin, y=46)
        else:
            self.welcome_label.config(text=f"Buenas noches, {self.name}")
            self.icon_label.config(image=self.icon_night)
            self.icon_label.place(x=self.x_margin, y=47)

    def show_today_income(self):
        today = datetime.now().date()
        today_sales = sales_dao.get_sales_by_date(date=today)
        
        if not today_sales:
            today_income = str(Decimal(0.00).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)) + " €"
        else:
            today_income = Decimal("0.00")
            for x in today_sales:
                today_income += Decimal(str(x[6]))
            today_income = str(Decimal(today_income).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)) + " €"
        canvas, id = self.top_cards["Ingresos de hoy"]
        canvas.itemconfig(id, text=today_income, fill="#0A770C")
        
        
    def show_week_income(self):
        today = datetime.now().date()
        start_week = today - timedelta(days=today.weekday())  # lunes de esta semana
        end_week = start_week + timedelta(days=6)   
        week_sales = sales_dao.get_sales_by_date(date_range=(start_week, end_week))
        
        
        if not week_sales:
            week_income = str(Decimal(0.00).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)) + " €"
        else:
            week_income = Decimal("0.00")
            for x in week_sales:
                week_income += Decimal(str(x[6]))
            week_income = str(Decimal(week_income).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)) + " €"
        canvas, id = self.top_cards["Ingresos de esta semana"]
        canvas.itemconfig(id, text=week_income, fill="#0A770C")

    def show_no_stock(self):
        prods = product_dao.get_products_with_no_stock()
        if not prods:
            prods_qtt = 0
        else:
            prods_qtt = len(prods)
        canvas, id = self.top_cards["Sin stock"]
        canvas.itemconfig(id, text=prods_qtt, anchor="n")
        canvas.coords(id, 115, 50)
        
        if prods_qtt == 0:
            canvas.itemconfig(id, fill="#0A770C")
        elif 0 < prods_qtt < 5:
            canvas.itemconfig(id, fill="#CBCB00")
        else:
            canvas.itemconfig(id, fill="#E8280A")

    def show_sold_prods_today(self):
        today = datetime.now().date()
        prods = sales_dao.get_sales_by_date(today)
        if not prods:
            prods_qtt = 0
        else:
            prods_qtt = len(prods)
        canvas, id = self.top_cards["Productos vendidos hoy"]
        canvas.itemconfig(id, text=prods_qtt, anchor="n")
        canvas.coords(id, 115, 50)
        if prods_qtt == 0:
            canvas.itemconfig(id, fill="#E8280A")
        elif 0 < prods_qtt < 10:
            canvas.itemconfig(id, fill="#CBCB00")
        else:
            canvas.itemconfig(id, fill="#0A770C")

    def show_lost_prods(self):
        year = datetime.now().year
        month = datetime.now().month
        
        first_day = datetime(year, month, 1)

        if month == 12:
            next_month = datetime(year+1, 1, 1)
        else:
            next_month = datetime(year, month+1, 1)
        last_day = next_month - timedelta(days=1)

        lost_prods = product_dao.get_all_lost_products(date_range=(first_day, last_day))
        if len(lost_prods) < 1:
            money_lost = str(Decimal(0.00).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)) + " €"
        else:
            money_lost = Decimal("0.00")
            for x in lost_prods:
                money_lost += Decimal(str(x[5]))
            money_lost = str(Decimal(money_lost).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)) + " €"
        canvas, id = self.top_cards["Pérdida mensual por merma"]
        canvas.itemconfig(id, text=money_lost)
        if Decimal(money_lost.split()[0]) == 0:
            canvas.itemconfig(id, fill="#0A770C")
        elif 0 < Decimal(money_lost.split()[0]) < 100:
            canvas.itemconfig(id, fill="#CBCB00")
        else:
            canvas.itemconfig(id, fill="#E8280A")

    def show_more_sold_prods_today(self):
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)

        sales_today = sales_dao.get_sales_by_date(date=today)
        if not sales_today:
            return
        
        id_sales_today = {}
        for sale in sales_today:
            prod_id = sale[2]
            prod_name = sale[3]
            income = sale[6]
            if prod_id not in id_sales_today:
                id_sales_today[prod_id] = [prod_name, income]
            else:
                id_sales_today[prod_id][1] += income
        
        for id in id_sales_today:
            yesterday_sales = sales_dao.get_sales_by_date_and_prod_id(id, yesterday)
            if not yesterday_sales:
                yesterday_amount = Decimal(0.00).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                relative = "100.00%"
            else:
                yesterday_amount = Decimal("0.00")
                for sale in yesterday_sales:
                    yesterday_amount += Decimal(sale[6])
                relative = str(Decimal(id_sales_today[id][1] / yesterday_amount * 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)) + "%"
            id_sales_today[id].append(relative)
        
        # Ordenar por valor (ingresos), descendente
        sorted_sales_today = dict(sorted(id_sales_today.items(), key=lambda item: item[1][1], reverse=True))
        for item in self.sold_prod_today_treeview.get_children():
            self.sold_prod_today_treeview.delete(item)
        for prod, income, relative in sorted_sales_today.values():
            values = (prod, income, relative)
            self.sold_prod_today_treeview.insert("", tk.END, values=values)

    def show_more_sold_prods_month(self):
        year = datetime.now().year
        month = datetime.now().month
        
        first_day_current_month = datetime(year, month, 1)
        if month == 12:
            next_month = datetime(year+1, 1, 1)
        else:
            next_month = datetime(year, month+1, 1)
        last_day_current_month = next_month - timedelta(days=1)

        sales_current_month = sales_dao.get_sales_by_date(date_range=(first_day_current_month, last_day_current_month))
        if not sales_current_month:
            return
        
        if month == 1:
            first_day_last_month = datetime(year-1, 12, 1)
        else:
            first_day_last_month = datetime(year, month-1, 1)
        last_day_last_month = first_day_current_month - timedelta(days=1)
        
        id_sales_current_month = {}
        for sale in sales_current_month:
            prod_id = sale[2]
            prod_name = sale[3]
            income = sale[6]
            if prod_id not in id_sales_current_month:
                id_sales_current_month[prod_id] = [prod_name, income]
            else:
                id_sales_current_month[prod_id][1] += income
        
        
        for id in id_sales_current_month:
            last_month_sales = sales_dao.get_sales_by_date_and_prod_id(id, date_range=(first_day_last_month, last_day_last_month))
            if not last_month_sales:
                last_month_amount = Decimal(0.00).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                relative = "100.00%"
            else:
                last_month_amount = Decimal("0.00")
                for sale in last_month_sales:
                    last_month_amount += Decimal(sale[6])
                relative = str(Decimal(id_sales_current_month[id][1] / last_month_amount * 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)) + "%"
                
            id_sales_current_month[id].append(relative)
        
        # Ordenar por valor (ingresos), descendente
        sorted_sales_month = dict(sorted(id_sales_current_month.items(), key=lambda item: item[1][1], reverse=True))
        for item in self.sold_prod_month_treeview.get_children():
            self.sold_prod_month_treeview.delete(item)
        for prod, income, relative in sorted_sales_month.values():
            values = (prod, income, relative)
            self.sold_prod_month_treeview.insert("", tk.END, values=values)

    def show_top_employees(self):
        year = datetime.now().year
        month = datetime.now().month
        
        first_day = datetime(year, month, 1)

        if month == 12:
            next_month = datetime(year+1, 1, 1)
        else:
            next_month = datetime(year, month+1, 1)
        last_day = next_month - timedelta(days=1)

        sales = sales_dao.get_sales_by_date(date_range=(first_day, last_day))
        if not sales:
            return
        
        employee_total = {} # id: amount
        for sales_id, sales_date, prod_id, pproduct, sale_quantity, sell_price, sale_total, employee_id in sales:
            if employee_id in employee_total.keys():
                employee_total[employee_id] += sale_quantity
            else:
                employee_total[employee_id] = sale_quantity

        top_employees = []
        for id, amount in employee_total.items():
            name = employees_dao.get_employee_data(id, priv_data=True)[1]
            top_employees.append((id, name, amount))
        top_employees = sorted(top_employees, key=lambda item: item[2], reverse=True)[:5]
        
        for index, (employee_data, text_ids) in enumerate(zip(top_employees, self.top_employees_text_id)):
            employee_id = employee_data[0]
            employee_name = employee_data[1]
            employee_sales = Decimal(employee_data[2]).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            text_id = text_ids[0]
            text_name = text_ids[1]
            text_sales = text_ids[2]
            y = 50 + index * 30

            self.top_employees_canvas.itemconfig(text_id, text="👤")
            self.top_employees_canvas.itemconfig(text_name, text=employee_name)
            self.top_employees_canvas.itemconfig(text_sales, text=f"{employee_sales}€")
            self.top_employees_canvas.coords(text_id, 50, y)
            self.top_employees_canvas.coords(text_name, 80, y)
            self.top_employees_canvas.coords(text_sales, 340, y)

    def show_category_graph(self):
        if hasattr(self, 'cat_widget_1'):
            self.cat_widget_1.destroy()
        if hasattr(self, 'cat_widget_2'):
            self.cat_widget_2.destroy()
        if hasattr(self, 'cat_legend_frame'):
            self.cat_legend_frame.destroy()


        year = datetime.now().year
        month = datetime.now().month
        
        # Get first and last day of this month
        first_day_month = datetime(year, month, 1)

        if month == 12:
            next_month = datetime(year+1, 1, 1)
        else:
            next_month = datetime(year, month+1, 1)
        last_day_month = next_month - timedelta(days=1)

        if month == 12:
            next_month = datetime(year+1, 1, 1)
        else:
            next_month = datetime(year, month+1, 1)
        last_day_month = next_month - timedelta(days=1)
    
        # Get first and last day of this year 
        first_day_year = datetime(year, 1, 1)
        last_day_year = datetime(year, 12, 31)

        general_categories = product_dao.get_general_categories(prod_category=None, prov_id=None)
        if not general_categories:
            return
        general_categories = list(set([cat[0] for cat in general_categories]))
        

        # Get data from DB
        month_sales = {}
        date_range_month = (first_day_month, last_day_month)
        for cat in general_categories:
            cat_sales = sales_dao.get_sales_by_general_cat(cat, date_range_month)
            if cat_sales:
                total_sales = sum(data[1] for data in cat_sales)
                month_sales[cat] = total_sales
        
        if month_sales:
            month_sales = dict(sorted(month_sales.items(), key=lambda item: item[1], reverse=True))
            month_sales = dict(list(month_sales.items())[:5])
        
        year_sales = {}
        date_range_year = (first_day_year, last_day_year)
        for cat in general_categories:
            cat_sales = sales_dao.get_sales_by_general_cat(cat, date_range_year)
            if cat_sales:
                total_sales = sum(data[1] for data in cat_sales)
                year_sales[cat] = total_sales
        
        if year_sales:
            year_sales = dict(sorted(year_sales.items(), key=lambda item: item[1], reverse=True))
            year_sales = dict(list(year_sales.items())[:5])
        
        # Create labels
        labels_1 = list(month_sales.keys())
        labels_1 = labels_1[:5]
        sizes_1 = list(month_sales.values())

        labels_2 = list(year_sales.keys())
        labels_2 = labels_2[:5]
        sizes_2 = list(year_sales.values())

        # Colors
        colors = [
            "#3366CC", "#F50A0A", "#E3D403", "#00C90D", "#CE00CE"
        ]
        if labels_1 and labels_2:
            colors = colors[:max(len(labels_1), len(labels_2))]
        elif labels_2 and not labels_1:
            colors = colors[:len(labels_2)]
        else:
            colors = None
            
        # Create figures
        fig_1 = Figure(figsize=(1.3, 1.3), dpi=100)
        fig_1.patch.set_alpha(0)
        fig_1.subplots_adjust(left=0, right=1, top=1, bottom=0)

        ax_1 = fig_1.add_subplot(111)
        ax_1.set_facecolor('none')

        wedges, _, autotexts = ax_1.pie(
            sizes_1,
            labels=None,
            autopct="%1.1f%%",
            startangle=140,
            colors=colors,
            textprops={'fontsize': 7, 'color': '#333'},
            wedgeprops={"edgecolor": "white", "linewidth": 1}
        )

        ax_1.axis("equal")

        fig_2 = Figure(figsize=(1.6, 1.6), dpi=100)
        fig_2.patch.set_alpha(0)
        fig_2.subplots_adjust(left=0, right=1, top=1, bottom=0)

        ax_2 = fig_2.add_subplot(111)
        ax_2.set_facecolor('none')

        wedges, _, autotexts = ax_2.pie(
            sizes_2,
            labels=None,
            autopct="%1.1f%%",
            startangle=140,
            colors=colors,
            textprops={'fontsize': 7, 'color': '#333'},
            wedgeprops={"edgecolor": "white", "linewidth": 1}
        )

        ax_2.axis("equal")

        # Mostrar en Tkinter
        canvas_widget_1 = FigureCanvasTkAgg(fig_1, master=self.dashboard_main_frame)
        canvas_widget_1.draw()
        widget_1 = canvas_widget_1.get_tk_widget()
        widget_1.place(x=780, y=310)
        widget_1.config(highlightthickness=0)

         
        canvas_widget_2 = FigureCanvasTkAgg(fig_2, master=self.dashboard_main_frame)
        canvas_widget_2.draw()
        widget_2 = canvas_widget_2.get_tk_widget()
        widget_2.place(x=1080, y=280)
        widget_2.config(highlightthickness=0)


        # Crear leyenda ventas mensuales
        legend_frame_month = tk.Frame(self.dashboard_main_frame, bg=self.dashboard_main_frame["bg"])
        legend_frame_month.place(x=700, y=320)

        if labels_1:
            for i, label in enumerate(labels_1):
                color = colors[i]
                item_frame = tk.Frame(legend_frame_month, bg=self.dashboard_main_frame["bg"])
                item_frame.pack(anchor='w', pady=1)
                tk.Label(item_frame, width=2, height=1, bg=color).pack(side="left", padx=(0, 5))
                tk.Label(item_frame, text=label, font=("Arial", 8), bg=self.dashboard_main_frame["bg"]).pack(side="left")

    
        # Crear leyenda ventas anuales
        legend_frame_year = tk.Frame(self.dashboard_main_frame, bg=self.dashboard_main_frame["bg"])
        legend_frame_year.place(x=980, y=320)

        if labels_2:
            for i, label in enumerate(labels_2):
                color = colors[i]
                item_frame = tk.Frame(legend_frame_year, bg=self.dashboard_main_frame["bg"])
                item_frame.pack(anchor='w', pady=1)
                tk.Label(item_frame, width=2, height=1, bg=color).pack(side="left", padx=(0, 5))
                tk.Label(item_frame, text=label, font=("Arial", 8), bg=self.dashboard_main_frame["bg"]).pack(side="left")

    def show_year_gross_income(self):
        year = datetime.now().year
        current_month = datetime.now().month
        
        months_date_range = []
        for i in range(1, current_month + 1):
            first_day = datetime(year, i, 1)
            
            # Define next month and rest 1 timedelta to get last day from current_month
            if i < 12:
                next_month = i + 1
                next_month = datetime(year, next_month, 1)
            else:
                year = year + 1
                next_month = 1
                next_month = datetime(year, next_month, 1)
            
            last_day = next_month - timedelta(days=1)
            months_date_range.append((first_day.date(), last_day.date()))
        
        months_sales = {}
        for j in months_date_range:
            sales = sales_dao.get_sales_by_date(date_range=j)
            if not sales:
                months_sales[j] = Decimal("0.00").quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            else:
                month_total = Decimal(0.00)
                for k in sales:
                    month_total += Decimal(k[6])
                months_sales[j] = Decimal(month_total).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Primero, borra cualquier gráfico anterior (si lo hay)
        if hasattr(self, 'income_graph_widget'):
            self.income_graph_widget.get_tk_widget().destroy()
            self.income_graph_widget = None 
    
        # Datos
        month_names = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", 
            "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        labels = [month_names[start.month - 1] for start, _ in months_sales.keys()]

        values = [float(val) for val in months_sales.values()]

        # Colores y estilo
        line_color = "#2E86C1"
        marker_color = "#1ABC9C"
        label_color = "#000"  # Negro puro para texto

        # Crear figura
        fig = Figure(figsize=(5.5, 1.5), dpi=100)
        ax = fig.add_subplot(111)

        # Fondo completamente blanco
        fig.patch.set_facecolor("white")
        ax.set_facecolor("white")

        # Dibujar la línea
        ax.plot(labels, values, color=line_color, linewidth=1.0, markersize=6, markerfacecolor=marker_color)

        # Etiquetas de ejes
        ax.set_ylabel("Ingresos (€)", fontsize=10, color=label_color)

        # Colores de los ticks
        ax.tick_params(axis='x', labelrotation=0, colors=label_color)
        ax.tick_params(axis='y', colors=label_color)

        # Ocultar todos los bordes (spines)
        for spine in ax.spines.values():
            spine.set_visible(False)

        # Quitar cuadrículas
        ax.grid(False)

        # Ajuste de márgenes
        fig.tight_layout()

        # Insertar en Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.income_canvas)
        canvas.draw()
        canvas.get_tk_widget().place(x=20, y=50)
