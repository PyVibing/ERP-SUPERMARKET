from decimal import Decimal
from datetime import datetime
from mysql.connector import IntegrityError

class ProductDAO:

    def __init__(self, db):
        self.db = db
                
    def get_all_products(self):
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM products")
                    products = cursor.fetchall()
            return products
        except Exception:
            return None
        
    def get_products_by_prov(self, prov_id, category=None):
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    if category is None:
                        cursor.execute("SELECT * FROM products WHERE provider_id=%s", (prov_id,))
                        products = cursor.fetchall()
                    else:
                        cursor.execute("SELECT * FROM products WHERE provider_id=%s AND category_general=%s", (prov_id, category))
                        products = cursor.fetchall()
            return products
        except Exception:
            return None
    
    def get_products_with_no_stock(self, category=None):
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    if not category:
                        cursor.execute("SELECT * FROM products WHERE stock = 0")
                        products = cursor.fetchall()
                        if len(products) > 0:
                            return products
                        else:
                            return None
                    else:
                        cursor.execute("SELECT * FROM products WHERE stock = 0 AND category=%s", (category,))
                        products = cursor.fetchall()
                        if len(products) > 0:
                            return products
                        else:
                            return None
            return products
        except Exception:
            return None
    
    def get_all_products_with_stock(self, category=None):
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    if not category:
                        cursor.execute("SELECT * FROM products WHERE stock > 0")
                        products = cursor.fetchall()
                    else:
                        cursor.execute("SELECT * FROM products WHERE stock > 0 AND category=%s", (category,))
                        products = cursor.fetchall()
            return products
        except Exception:
            return None
    
    def get_product_stock(self, prod_id):
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT stock FROM products WHERE id = %s", (prod_id,))
                    product = cursor.fetchone()
            return product[0]
        except Exception as e:
            print(e)
            return None
        
    def get_product_price_stock(self, prod_id):
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT sell_price, stock FROM products WHERE stock > 0 and id = %s", (prod_id,))
                    prod = cursor.fetchone()
            return prod
        except Exception as e:
            print(e)
            return None
        
    def get_product_by_id(self, prod_id):
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM products WHERE id=%s", (prod_id,))
                    product = cursor.fetchone()
            return product
        except Exception:
            return None
        
    def get_product_by_name(self, prod_name):
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM products WHERE product=%s", (prod_name,))
                    product = cursor.fetchone()
            return product
        except Exception:
            return None
    
    def insert_products(self, values):
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    cursor.executemany("""
                        INSERT INTO products (product, category_general, category, stock, buy_price, sell_price, provider_id, prod_date, exp_date)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (values)
                    )
                    connection.commit()
                    last_row_id = cursor.lastrowid
                if len(values) > 1:
                    return True
                else:
                    return last_row_id
        except Exception as e:
            print(e)
            return None

    
    def insert_product(self, product, category_general, category, stock, buy_price, sell_price, provider_id, prod_date, exp_date):
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO products (product, category_general, category, stock, buy_price, sell_price, provider_id, prod_date, exp_date)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""", 
                        (product, category_general, category, stock, buy_price, sell_price, provider_id, prod_date, exp_date)
                    )
                    connection.commit()
            return True
        except Exception as e:
            print(e)
            return None
        
    def check_if_product_exist(self, product, category, buy_price, sell_price, provider_id, category_general, prod_date, exp_date):
        # Check if product with same data already exists
        product_in_db = self.get_product_by_name(product)
        if product_in_db:
            if (
                product_in_db[1] == product.strip().title() and 
                product_in_db[2] == category_general.strip().title() and
                product_in_db[3] == category.strip().capitalize() and 
                product_in_db[5] == Decimal(str(buy_price)).quantize(Decimal("0.01")) and 
                product_in_db[6] == Decimal(str(sell_price)).quantize(Decimal("0.01")) and 
                product_in_db[7] == provider_id and 
                product_in_db[8] == prod_date and 
                product_in_db[9] == exp_date
            ):
                return (product_in_db[0], product_in_db[4])
            
        return (None, None)
    
    def delete_product(self, products_id):
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    cursor.executemany("DELETE FROM products WHERE id=%s", (products_id))
                connection.commit()
                return True
        except IntegrityError:
            return "IntegrityError"
        except Exception as e:
            print(e)
            return None
    
    def get_categories(self, category_general=None):
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    if category_general:
                        cursor.execute("SELECT category FROM products WHERE category_general = %s", (category_general,))
                        categories = cursor.fetchall()
                    else:
                        cursor.execute("SELECT category FROM products")
                        categories = cursor.fetchall()
            return categories
        except Exception as e:
            print(e)
            return None
        
    def get_general_categories(self, prod_category=None, prov_id=None):
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    if prod_category:
                        cursor.execute("SELECT category_general FROM products WHERE category = %s", (prod_category,))
                        categories = cursor.fetchall()
                    elif prov_id:
                        cursor.execute("SELECT category_general FROM products WHERE provider_id = %s", (prov_id,))
                        categories = cursor.fetchall()
                    else:
                        cursor.execute("SELECT category_general FROM products")
                        categories = cursor.fetchall()
            return categories
        except Exception as e:
            print(e)
            return None
    
    def update_prod_stock(self, values):
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    cursor.executemany("UPDATE products SET stock=%s WHERE id=%s", (values))
                connection.commit()
            return True
        except Exception as e:
            print(e)
            return None
        
    def update_prod_data(self, values, prod_id):
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        UPDATE products SET product=%s, category_general=%s, category=%s, stock=%s, buy_price=%s, sell_price=%s, provider_id=%s, prod_date=%s, exp_date=%s
                        WHERE id=%s"""
                        ,(*values, prod_id)
                    )
                connection.commit()
            return True
        except Exception as e:
            print(e)
            return None

    def add_product_stock(self, product_id, new_stock):
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE products SET stock=%s WHERE id=%s", (new_stock, product_id))
                connection.commit()
            return True
        except Exception as e:
            print(e)
            return None
        
    def get_buy_price(self, prod_id):
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT buy_price FROM products WHERE id=%s", (prod_id,))
                    buy_price = cursor.fetchone()
            return buy_price[0]
        except Exception as e:
            return None
      
    def declare_lost_product(self, prod_id, decrease_quantity, motive, employee_id):
        product = self.get_product_by_id(prod_id)
        buy_price = product[5]
        total = decrease_quantity * buy_price
        
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO lost_products (prod_id, quantity, buy_price, total, concept, date, employee_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)""", 
                        (prod_id, decrease_quantity, buy_price, total, motive, datetime.now(), employee_id)
                    )
                    connection.commit()
                    inserted_lost_prod_id = cursor.lastrowid
            return inserted_lost_prod_id
        except Exception as e:
            print(e)
            return None

    def get_all_lost_products(self, date=None, date_range=None):
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    if date_range:
                        cursor.execute("""
                            SELECT lost_products.id, products.id, products.product, lost_products.quantity, lost_products.buy_price, lost_products.total, 
                                    lost_products.concept, lost_products.date, employees.id, employees.employee
                            FROM lost_products
                            JOIN products
                                ON products.id = lost_products.prod_id
                            JOIN employees
                                ON employees.id = lost_products.employee_id
                            WHERE lost_products.date BETWEEN %s and %s
                            """, date_range)
                        lost_products = cursor.fetchall()

                    elif date:
                        cursor.execute("""
                            SELECT lost_products.id, products.id, products.product, lost_products.quantity, lost_products.buy_price, lost_products.total, 
                                    lost_products.concept, lost_products.date, employees.id, employees.employee
                            FROM lost_products
                            JOIN products
                                ON products.id = lost_products.prod_id
                            JOIN employees
                                ON employees.id = lost_products.employee_id
                            WHERE lost_products.date = %s
                            """, (date,))
                        lost_products = cursor.fetchall()
                    
                    else:
                        cursor.execute("""
                            SELECT lost_products.id, products.id, products.product, lost_products.quantity, lost_products.buy_price, lost_products.total, 
                                    lost_products.concept, lost_products.date, employees.id, employees.employee
                            FROM lost_products
                            JOIN products
                                ON products.id = lost_products.prod_id
                            JOIN employees
                                ON employees.id = lost_products.employee_id
                            """)
                        lost_products = cursor.fetchall()
            return lost_products
        except Exception:
            return None
        
    def delete_lost_product(self, products_id):
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    for prod_id in products_id:
                        cursor.execute("DELETE FROM lost_products WHERE id=%s", (prod_id,))
                connection.commit()
                return True
        except IntegrityError as e:
            print("IntegrityError: {e}")
            return "IntegrityError"
        except Exception as e:
            print("Exception: {e}")
            return None