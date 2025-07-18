from mysql.connector import IntegrityError


class ProviderDAO:

    def __init__(self, db):
        self.db = db
        
    def get_all_providers(self):
        connection = self.db.connect_db()
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, provider, phone, email, address FROM providers")
                providers = cursor.fetchall()
                
        return providers
    
    def insert_provider(self, provider, phone, email, address):
        connection = self.db.connect_db()
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO providers (provider, phone, email, address) VALUES (%s, %s, %s, %s)", (provider, phone, email, address))
                provider_id = cursor.lastrowid
            connection.commit()
            return provider_id
    
    def delete_provider(self, values):
        try:
            connection = self.db.connect_db()
            with connection:
                with connection.cursor() as cursor:
                    cursor.executemany("DELETE FROM providers WHERE id=%s", (values))
                connection.commit()
                return True
        except IntegrityError as e: 
            return "IntegrityError"
        except Exception as e:
            print(e)
            return None
            
    def get_prov_id(self, provider_name):
        try:
            connection = self.db.connect_db()
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT id FROM providers WHERE provider=%s", (provider_name,))
                    prov_id = cursor.fetchone()
                    if prov_id:
                        return prov_id[0]
                    else:
                        return None
        except Exception as e:
            print(e)
            return None
    
    def get_provider_for_id(self, provider_id):
        connection = self.db.connect_db()
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT provider FROM providers WHERE id=%s", (provider_id,))
                prov_name = cursor.fetchone()
                return prov_name[0]
            
    def get_provider_data(self, prov_id):
        try:
            connection = self.db.connect_db()
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT id, provider, phone, email, address FROM providers WHERE id=%s", (prov_id,))
                    prov_data = cursor.fetchone()
                    return prov_data
        except Exception as e:
            print(e)
            return None

        
    def update_provider(self, id, prov, phone, email, address):
        # Excepto categoria
        try:
            connection = self.db.connect_db()
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE providers SET provider=%s, phone=%s, email=%s, address=%s WHERE id=%s", (prov, phone, email, address, id))
                connection.commit()
                return True
        except Exception as e:
            print(e)
            return None