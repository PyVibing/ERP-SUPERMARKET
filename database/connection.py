import tkinter.messagebox
import mysql.connector
import os
from dotenv import load_dotenv
import tkinter

load_dotenv()

class Database:
    def __init__(self):
        self.host=os.getenv("MYSQL_HOST")
        self.user=os.getenv("MYSQL_USER")
        self.password=os.getenv("MYSQL_PASSWORD")
        self.database = os.getenv("MYSQL_DB")
        self.create_database()

    def connect_db(self, use_db=True):
        if not use_db:
            try:
                return mysql.connector.connect(
                    host=os.getenv("MYSQL_HOST"),
                    user=os.getenv("MYSQL_USER"),
                    password=os.getenv("MYSQL_PASSWORD")
                )
                    
            except Exception as e: 
                tkinter.messagebox.showerror("Error de conexión", f"No se pudo conectar a la BBDD: {e}")
                return None
        
        else:
            try:
                return mysql.connector.connect(
                    host=os.getenv("MYSQL_HOST"),
                    user=os.getenv("MYSQL_USER"),
                    password=os.getenv("MYSQL_PASSWORD"),
                    database=os.getenv("MYSQL_DB")
                )
                    
            except Exception as e: 
                tkinter.messagebox.showerror("Error de conexión", f"No se pudo conectar a la BBDD: {e}")
                return None
            
    def create_database(self):
            connection = self.connect_db(use_db=False)
            if connection:
                try:
                    cursor = connection.cursor()
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {os.getenv('MYSQL_DB')}")
                    connection.commit()
                    self.create_tables()

                except Exception as e:
                    tkinter.messagebox.showerror(
                        title='Error al crear la BBDD', 
                        message=f'Ocurrió un error al intentar crear la Base de Datos inicial: {e}'
                    )

                finally:
                    if cursor:
                        cursor.close()
                    connection.close()

    def create_tables(self):
        connection = self.connect_db()
        if connection:
            try:
                cursor = connection.cursor()
                tables = ["""
                    CREATE TABLE IF NOT EXISTS employees (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        employee VARCHAR(100) NOT NULL,
                        personal_id VARCHAR(30) NOT NULL UNIQUE,
                        phone VARCHAR(30) NOT NULL,
                        email VARCHAR(100) NOT NULL UNIQUE,
                        address VARCHAR(255) NOT NULL,
                        position VARCHAR(100) NOT NULL,
                        work_shift VARCHAR(30) NOT NULL,
                        contract_type VARCHAR(30) NOT NULL,
                        week_hours INT NOT NULL,
                        salary DECIMAL(10,2) NOT NULL,
                        entry_time TIME NOT NULL,
                        exit_time TIME NOT NULL,
                        employee_status VARCHAR(30) NOT NULL CHECK (employee_status IN ('Activo', 'Inactivo')),
                        employment_start_date DATETIME NOT NULL,
                        contract_end_date DATETIME,
                        employment_end_date DATETIME,
                        contract_filepath VARCHAR(255)
                    );""",

                    """CREATE TABLE IF NOT EXISTS temp_leaves (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        employee_id INT NOT NULL,
                        employee_status VARCHAR(30) NOT NULL CHECK 
                            (employee_status IN ('Vacaciones', 'Baja médica', 'Excedencia', 'Maternidad', 'Baja definitiva')),
                        status_start_date DATETIME NOT NULL,
                        status_end_date DATETIME,
                        FOREIGN KEY (employee_id) REFERENCES employees(id) 
                            ON UPDATE CASCADE ON DELETE RESTRICT
                    );""",
                    
                    """CREATE TABLE IF NOT EXISTS providers (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        provider VARCHAR(100) NOT NULL,
                        phone VARCHAR(30) NOT NULL,
                        email VARCHAR(100) NOT NULL,
                        address VARCHAR(255) NOT NULL
                    );""",

                    """CREATE TABLE IF NOT EXISTS products (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        product VARCHAR(100) NOT NULL,
                        category_general VARCHAR(100) NOT NULL,
                        category VARCHAR(100) NOT NULL, 
                        stock INT NOT NULL,
                        buy_price DECIMAL(10, 2) NOT NULL,
                        sell_price DECIMAL(10, 2),
                        provider_id INT NOT NULL,
                        prod_date DATETIME NOT NULL,
                        exp_date DATETIME NOT NULL,
                        FOREIGN KEY (provider_id) REFERENCES providers(id) 
                            ON UPDATE CASCADE ON DELETE RESTRICT
                    );""",
                    
                    """CREATE TABLE IF NOT EXISTS sales (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        prod_id INT NOT NULL,
                        quantity INT NOT NULL,
                        buy_price DECIMAL(10, 2) NOT NULL,
                        sell_price DECIMAL(10, 2) NOT NULL,
                        total DECIMAL(10, 2) NOT NULL,
                        profit DECIMAL(10, 2) NOT NULL,
                        date DATETIME NOT NULL,
                        employee_id INT NOT NULL,
                        FOREIGN KEY (prod_id) REFERENCES products(id)
                            ON UPDATE CASCADE ON DELETE RESTRICT,
                        FOREIGN KEY (employee_id) REFERENCES employees(id)
                            ON UPDATE CASCADE ON DELETE RESTRICT
                    );""",

                    """CREATE TABLE IF NOT EXISTS users (
                        employee_id INT NOT NULL UNIQUE,
                        email VARCHAR(50) NOT NULL UNIQUE,
                        password_hash VARCHAR(255) NOT NULL,
                        role VARCHAR(30) NOT NULL,
                        FOREIGN KEY (employee_id) REFERENCES employees(id)
                            ON DELETE CASCADE 
                    );""",

                    """CREATE TABLE IF NOT EXISTS lost_products (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        prod_id INT NOT NULL,
                        quantity INT NOT NULL,
                        buy_price DECIMAL(10, 2) NOT NULL,
                        total DECIMAL(10, 2) NOT NULL,
                        concept VARCHAR(255) NOT NULL,
                        date DATETIME NOT NULL,
                        employee_id INT NOT NULL,
                        FOREIGN KEY (prod_id) REFERENCES products(id)
                            ON UPDATE CASCADE ON DELETE RESTRICT,
                        FOREIGN KEY (employee_id) REFERENCES employees(id)
                            ON UPDATE CASCADE ON DELETE RESTRICT
                    );"""                    
                ]
                
                for query in tables:
                    cursor = connection.cursor()
                    cursor.execute(query)
                    cursor.close()
                
            except Exception as e:
                tkinter.messagebox.showerror(title="Error al crear las tablas", message=f"Ocurrió un error intentando crear las tablas de la BBDD: {e}")

            finally:
                if cursor: # por si queda algun cursor abierto
                    cursor.close()
                connection.close()
                        
        else:
            tkinter.messagebox.showerror(title="Sin conexión a la BBDD", message="No hay conexión a la BBDD. No se pudo crear las tablas de la BBDD.")

