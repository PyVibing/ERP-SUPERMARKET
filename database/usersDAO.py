from .connection import Database

class UsersDAO:

    def __init__(self, db):
        self.db = db
    
    def get_user_data(self, employee_id=None, email=None):
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    if employee_id:
                        cursor.execute("SELECT email, password_hash, role FROM users WHERE employee_id=%s", (employee_id,))
                        return cursor.fetchone()
                    elif email:
                        cursor.execute("SELECT employee_id, password_hash, role FROM users WHERE email=%s", (email,))
                        return cursor.fetchone()
                    else:
                        cursor.execute("SELECT employee_id, email, password_hash, role FROM users")
                        return cursor.fetchall()
        except Exception as e:
            print(e)
            return None
        
    def create_user(self, values):
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("INSERT INTO users (employee_id, email, password_hash, role) VALUES (%s, %s, %s, %s)", values)
                connection.commit()
            return True
        except Exception as e:
            print(e)
            return None
    
    def update_user(self, employee_id, password_hash=None, role=None):
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    if password_hash and role:
                        cursor.execute("UPDATE users SET password_hash=%s, role=%s WHERE employee_id=%s", 
                                       (password_hash, role, employee_id))
                    elif password_hash and not role:
                        cursor.execute("UPDATE users SET password_hash=%s WHERE employee_id=%s", 
                                       (password_hash, employee_id))
                    elif role and not password_hash:
                        cursor.execute("UPDATE users SET role=%s WHERE employee_id=%s", 
                                       (role, employee_id))
                connection.commit()
            return True
        except Exception as e:
            print(e)
            return None
        
    def delete_user_data(self, employee_id):
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM users WHERE employee_id=%s", (employee_id,))
                connection.commit()
            return True
        except Exception as e:
            print(e)
            return None
    
