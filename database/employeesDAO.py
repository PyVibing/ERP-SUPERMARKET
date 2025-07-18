from mysql.connector import IntegrityError

class EmployeesDAO:

    def __init__(self, db):
        self.db = db

    def get_all_employees(self, work_data=None, priv_data=None):
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    if (not work_data and not priv_data) or (work_data and priv_data):
                        cursor.execute("""
                                    SELECT id, employee, personal_id, phone, email, address, position, work_shift, contract_type,
                                    week_hours, salary, entry_time, exit_time, employee_status, employment_start_date, 
                                    employment_end_date, contract_end_date
                                    FROM employees
                                    """)
                        return cursor.fetchall()
                    elif work_data and not priv_data:
                        cursor.execute("""
                                    SELECT id, employee, position, work_shift, contract_type, week_hours, salary, entry_time, exit_time, 
                                    employee_status, employment_start_date, employment_end_date, contract_end_date
                                    FROM employees
                                    """)
                        return cursor.fetchall()
                    elif priv_data and not work_data:
                        cursor.execute("""
                                    SELECT id, employee, personal_id, phone, email, address
                                    FROM employees
                                    """)
                        return cursor.fetchall()
        except Exception as e:
            print(e)
            return None
        
    def get_employee_data(self, id, work_data=None, priv_data=None):
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    if (not work_data and not priv_data) or (work_data and priv_data):
                        cursor.execute("""
                                    SELECT id, employee, personal_id, phone, email, address, position, work_shift, contract_type,
                                    week_hours, salary, entry_time, exit_time, employee_status, employment_start_date, 
                                    employment_end_date, contract_end_date
                                    FROM employees
                                    WHERE id=%s
                                    """, (id,))
                        return cursor.fetchone()
                    elif work_data and not priv_data:
                        cursor.execute("""
                                    SELECT id, employee, position, work_shift, contract_type, week_hours, salary, entry_time, exit_time, 
                                    employee_status, employment_start_date, employment_end_date, contract_end_date
                                    FROM employees
                                    WHERE id=%s
                                    """, (id,))
                        return cursor.fetchone()
                    elif priv_data and not work_data:
                        cursor.execute("""
                                    SELECT id, employee, personal_id, phone, email, address
                                    FROM employees
                                    WHERE id=%s
                                    """, (id,))
                        return cursor.fetchone()
        except Exception as e:
            print(e)
            return None


    def insert_employee(self, values, end_contract=None):
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    if end_contract:
                        cursor.execute("""
                            INSERT INTO employees (
                                    employee, personal_id, phone, email, address, position, work_shift, contract_type,
                                    week_hours, salary, entry_time, exit_time, employee_status, employment_start_date, contract_end_date)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", 
                            (*values, end_contract)
                        )
                        inserted = cursor.lastrowid
                    else:
                        cursor.execute("""
                            INSERT INTO employees (
                                    employee, personal_id, phone, email, address, position, work_shift, contract_type,
                                    week_hours, salary, entry_time, exit_time, employee_status, employment_start_date)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", 
                            values
                        )
                        inserted = cursor.lastrowid
                connection.commit()
                return inserted
        except Exception as e:
            print(e)
            return None
    
    def get_employee_by_data(self, email=None, personal_id=None, name=None):
        """Busca coincidencias en la base de datos según email, personal_id o nombre.

            Args:
                email (str, optional): Correo electrónico del empleado.
                personal_id (str, optional): Identificador personal del empleado.
                name (str, optional): Nombre del empleado.

            Returns:
                str: "email" si el email ya está registrado.
                str: "personal_id" si el ID ya está registrado.
                tuple[str, int]: Si hay coincidencias por nombre (no únicos).
                str: "error" si ocurre un error en la consulta.
                None: Si no se encuentra ninguna coincidencia.
            """
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    if email:
                        cursor.execute("SELECT 1 FROM employees WHERE email=%s", (email,))
                        result = cursor.fetchone()
                        if result:
                            return "email"
                    if personal_id:
                        cursor.execute("SELECT 1 FROM employees WHERE personal_id=%s", (personal_id,))
                        result = cursor.fetchone()
                        if result:
                            return "personal_id"
                    if name:
                        cursor.execute("SELECT employee FROM employees WHERE employee=%s", (name,))
                        result = cursor.fetchall()
                        if result:
                            return (name, len(result))
            return None
        except Exception as e:
            print(e)
            return "error"


    def update_employee_data(self, employee_id, values, end_contract=None):
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    if end_contract:
                        query = """
                            UPDATE employees SET
                                employee = %s,
                                personal_id = %s,
                                phone = %s,
                                email = %s,
                                address = %s,
                                position = %s,
                                work_shift = %s,
                                contract_type = %s,
                                week_hours = %s,
                                salary = %s,
                                entry_time = %s,
                                exit_time = %s,
                                employment_start_date = %s,
                                contract_end_date = %s
                            WHERE id = %s
                        """
                        cursor.execute(query, (*values, end_contract, employee_id))
                    else:
                        query = """
                            UPDATE employees SET
                                employee = %s,
                                personal_id = %s,
                                phone = %s,
                                email = %s,
                                address = %s,
                                position = %s,
                                work_shift = %s,
                                contract_type = %s,
                                week_hours = %s,
                                salary = %s,
                                entry_time = %s,
                                exit_time = %s,
                                employment_start_date = %s,
                                contract_end_date = NULL
                            WHERE id = %s
                        """
                        cursor.execute(query, (*values, employee_id))
                connection.commit()
            return True
        except Exception as e:
            print(e)
            return None
        
    def delete_employee(self, id_list):
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    cursor.executemany("DELETE FROM employees WHERE id=%s", id_list)
                connection.commit()
                return True
        except IntegrityError as e:
            return "IntegrityError"
        except Exception as e:
            print(e)
            return None
    
    def get_active_inactive_status(self, employee_id=None):
        # If employee_id is provided, returns its status (active or inactive). Else, returns all the employees_id and its respective status
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    if employee_id:
                        cursor.execute("SELECT employee_status FROM employees WHERE id=%s", (employee_id,))
                        return cursor.fetchone()
                    else:
                        cursor.execute("SELECT id, employee_status FROM employees")
                        return cursor.fetchall()
        except Exception as e:
            print(e)
            return None
    
    def update_status(self, employee_id, employee_status):
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE employees SET employee_status=%s WHERE id=%s", (employee_status, employee_id))
                connection.commit()
                return True
        except Exception as e:
            print(e)
            return None
    
    def update_contract_path(self, employee_id, contract_path=None):
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    if contract_path:
                        cursor.execute("UPDATE employees SET contract_filepath=%s WHERE id=%s", (contract_path, employee_id))
                    else:
                        cursor.execute("UPDATE employees SET contract_filepath=NULL WHERE id=%s", (employee_id,))
                connection.commit()
            return True
        except Exception as e:
            print(e)
            return None
    
    def get_contract_data(self, employee_id):
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("""
                                   SELECT contract_type, employment_start_date, contract_end_date, employment_end_date, contract_filepath 
                                   FROM employees WHERE id=%s"""
                                   , (employee_id,))
                    return cursor.fetchone()
        except Exception as e:
            print(e)
            return None
    
    def terminate_contract(self, employee_id, end_date):
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE employees SET employee_status='Inactivo', contract_end_date=%s, employment_end_date=%s WHERE id=%s", (end_date, end_date, employee_id))
                connection.commit()
            return True
        except Exception as e:
            print(e)
            return None

    
# ----------------------------------- TABLE: TEMP_LEAVES (employee_status) ----------------------------------- #
    def insert_inactive_status_data(self, values, end_date=None):
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    if end_date:
                        cursor.execute("""
                                    INSERT INTO temp_leaves (employee_id, employee_status, status_start_date, status_end_date)
                                    VALUES (%s, %s, %s, %s)
                                    """, (*values, end_date))
                    else:
                        cursor.execute("""
                                    INSERT INTO temp_leaves (employee_id, employee_status, status_start_date)
                                    VALUES (%s, %s, %s)
                                    """, values)
                    connection.commit()
                    return True
        except Exception as e:
            print(e)
            return None

    def get_inactive_status_data(self, employee_id, end_date=None):
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    if not end_date:
                        cursor.execute("""
                            SELECT id, employee_status, status_start_date 
                            FROM temp_leaves WHERE employee_id=%s and status_end_date IS NULL
                            """, (employee_id,))
                        return cursor.fetchone()
                    else:
                        cursor.execute("""
                            SELECT id, employee_status, status_start_date, status_end_date 
                            FROM temp_leaves WHERE employee_id=%s and status_end_date IS NOT NULL
                            """, (employee_id,))
                        return cursor.fetchall()

        except Exception as e:
            print(e)
            return None
        
    def get_inactivity_history(self, employee_id):
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT id, employee_status, status_start_date, status_end_date
                        FROM temp_leaves WHERE employee_id=%s
                        """, (employee_id,))
                    return cursor.fetchall()
        except Exception as e:
            print(e)
            return None
        
    def close_inactive_status_data(self, status_id, end_date):
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE temp_leaves SET status_end_date=%s WHERE id=%s", (end_date, status_id))
                connection.commit()
            return True
        except Exception as e:
            print(e)
            return None
    

                