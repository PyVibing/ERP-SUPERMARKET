from .connection import Database

class SalesDAO:

    def __init__(self, db):
        self.db = db
    
    def get_sales_by_date(self, date=None, date_range=None):
        if date and date_range:
            return
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    if date_range:
                        cursor.execute("""
                            SELECT sales.id, sales.date, sales.prod_id, products.product, sales.quantity, sales.sell_price, sales.total, sales.employee_id
                            FROM sales 
                            JOIN products ON sales.prod_id=products.id
                            WHERE DATE(sales.date) BETWEEN %s AND %s""",
                            date_range
                        )
                        sales = cursor.fetchall()
                        if len(sales) > 0:
                            sorted_sales = sorted(sales, key=lambda item: item[1], reverse=True)
                            return sorted_sales
                        else:
                            return None
                    else:
                        if date is None:
                            cursor.execute("""
                                SELECT sales.id, sales.date, sales.prod_id, products.product, sales.quantity, sales.sell_price, sales.total, sales.employee_id
                                FROM sales 
                                JOIN products ON sales.prod_id=products.id""",
                            )
                            sales = cursor.fetchall()
                            if len(sales) > 0:
                                sorted_sales = sorted(sales, key=lambda item: item[1], reverse=True)
                                return sorted_sales
                            else:
                                return None
                
                        else:
                            cursor.execute("""
                                SELECT sales.id, sales.date, sales.prod_id, products.product, sales.quantity, sales.sell_price, sales.total, sales.employee_id
                                FROM sales 
                                JOIN products ON sales.prod_id=products.id
                                WHERE DATE(sales.date)=%s""",
                                (date,)
                            )
                            sales = cursor.fetchall()
                            if len(sales) > 0:
                                return sales
                            else:
                                return None
        except Exception as e:
            print(e)
            return None
        
    def get_sales_by_date_and_prod_id(self, prod_id, date=None, date_range=None):
        if (date and date_range) or (not date and not date_range):
            return
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    if date:
                        cursor.execute("""
                                SELECT sales.id, sales.date, sales.prod_id, products.product, sales.quantity, sales.sell_price, sales.total, sales.employee_id
                                FROM sales 
                                JOIN products ON sales.prod_id=products.id
                                WHERE DATE(sales.date)=%s AND sales.prod_id=%s""",
                                (date, prod_id))
                        sales = cursor.fetchall()
                        if len(sales) < 1:
                            return None
                        else:
                            return sales
                    elif date_range:
                        cursor.execute("""
                                SELECT sales.id, sales.date, sales.prod_id, products.product, sales.quantity, sales.sell_price, sales.total, sales.employee_id
                                FROM sales 
                                JOIN products ON sales.prod_id=products.id
                                WHERE DATE(sales.date) BETWEEN %s AND %s AND sales.prod_id=%s""",
                                (*date_range, prod_id))
                        sales = cursor.fetchall()
                        if len(sales) < 1:
                            return None
                        else:
                            return sales
        except Exception as e:
            print(e)
            return None
    
    def register_sale(self, values):
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    cursor.executemany("INSERT INTO sales (prod_id, quantity, buy_price, sell_price, total, profit, date, employee_id) " \
                                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", values)
                connection.commit()
            return True
        except Exception as e:
            return None

    def delete_sales(self, sales_id):
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    cursor.executemany("DELETE FROM sales WHERE id=%s", (sales_id))
                connection.commit()
            return True
        except Exception as e:
            print(e)
            return None
        
    def get_sales_by_general_cat(self, general_cat, date_range):
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT products.product, sales.total
                        FROM products
                        JOIN sales ON products.id = sales.prod_id
                        WHERE products.category_general=%s and sales.date BETWEEN %s and %s
                    """, (general_cat, *date_range))
                    result = cursor.fetchall()
                    if len(result) < 1:
                        return None
                    else:
                        return result
        except Exception as e:
            print(e)
            return None
        

    def update_sell_price(self, prod_id, sell_price):
        try:
            with self.db.connect_db() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        UPDATE products SET sell_price=%s WHERE id=%s
                    """, (sell_price, prod_id))
                connection.commit()
            return True
        except Exception as e:
            print(e)
            return None