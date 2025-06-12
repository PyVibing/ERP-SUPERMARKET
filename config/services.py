from database import *
from database.connection import Database



# Instancias únicas compartidas
db = Database()
product_dao = ProductDAO(db)
provider_dao = ProviderDAO(db)
sales_dao = SalesDAO(db)
employees_dao = EmployeesDAO(db)
users_dao = UsersDAO(db)


