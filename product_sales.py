# from sqlalchemy import create_engine
from sqlalchemy import text
from flask import Flask, request, render_template, redirect, jsonify
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import traceback

# Create connection and engine with mysql database
# con_sqlalchemy = 'mysql+pymysql://thanhphaolo:duongnhatthanh@database-3.c18iwmgyqpdp.ap-southeast-2.rds.amazonaws.com:3306/product_sales'
# engine = create_engine(con_sqlalchemy)

# Create Flask instance
app = Flask(__name__)

# Connect with sqlite database
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///product_sales.db"
db = SQLAlchemy(app)

purchase_order_details = db.Table('purchaseorderdetails',
                                  db.Column('purchaseOrderID', db.String(10), db.ForeignKey('purchaseorder.purchaseOrderID'), primary_key = True),
                                  db.Column('productID', db.String(10), db.ForeignKey('product.productID'), primary_key = True),
                                  db.Column('quantity', db.Integer))

sales_order_details = db.Table('salesorderdetails',
                                  db.Column('salesOrderID', db.String(10), db.ForeignKey('salesorder.salesOrderID'), primary_key = True),
                                  db.Column('productID', db.String(10), db.ForeignKey('product.productID'), primary_key = True),
                                  db.Column('quantity', db.Integer))

class Customer(db.Model):
    customerID = db.Column(db.String(10), primary_key=True)
    customerName = db.Column(db.String(30), nullable = False)
    customerPhone = db.Column(db.String(10), unique=True, nullable=False)
    customerAddress = db.Column(db.String(200))

    def create_id():
        last_customer = Customer.query.order_by(
            db.func.cast(db.func.substring(Customer.customerID, 2), db.Integer).desc()).first()
        if last_customer:
            last_id = int(last_customer.customerID[1:])
            new_id = f'C{last_id+1}'
        else:
            new_id = 'C1'
        return new_id

class Supplier(db.Model):
    supplierID = db.Column(db.String(10), primary_key=True)
    supplierName = db.Column(db.String(30), nullable = False)
    supplierPhone = db.Column(db.String(10), unique=True, nullable=False)
    supplierAddress = db.Column(db.String(200))

    def create_id():
        last_supplier = Supplier.query.order_by(
            db.func.cast(db.func.substring(Supplier.supplierID, 2), db.Integer).desc()).first()
        if last_supplier:
            last_id = int(last_supplier.supplierID[1:])
            new_id = f'S{last_id+1}'
        else:
            new_id = 'S1'
        return new_id

class Product(db.Model):
    productID = db.Column(db.String(10), primary_key = True)
    productName = db.Column(db.String(30), unique=True, nullable=False)
    productCategory = db.Column(db.String(30))
    productDescription = db.Column(db.String(100))
    unit = db.Column(db.String(30))
    purchasingPrice = db.Column(db.Integer, nullable = False)
    sellingPrice = db.Column(db.Integer, nullable = False)
    supplierID = db.Column(db.String(10), db.ForeignKey('supplier.supplierID'), nullable = False)
    purchaseOrders = db.relationship('PurchaseOrder', secondary = purchase_order_details, backref = 'products')
    salesOrders = db.relationship('SalesOrder', secondary = sales_order_details, backref = 'products')

    def create_id():
        last_product = Product.query.order_by(
            db.func.cast(db.func.substring(Product.productID, 2), db.Integer).desc()).first()
        if last_product:
            last_id = int(last_product.productID[1:])
            new_id = f'P{last_id+1}'
        else:
            new_id = 'P1'
        return new_id

class PurchaseOrder(db.Model):
    __tablename__ = 'purchaseorder'  
    purchaseOrderID = db.Column(db.String(10), primary_key = True)
    orderingDate = db.Column(db.Date)
    paymentDate = db.Column(db.Date)
    supplierID = db.Column(db.String(10), db.ForeignKey('supplier.supplierID'), nullable = False)

    def create_id():
        last_purchase_order = PurchaseOrder.query.order_by(
            db.func.cast(db.func.substring(PurchaseOrder.purchaseOrderID, 3), db.Integer).desc()).first()
        if last_purchase_order:
            last_id = int(last_purchase_order.purchaseOrderID[2:])
            new_id = f'PO{last_id+1}'
        else:
            new_id = 'PO1'
        return new_id
    
class SalesOrder(db.Model):
    __tablename__ = 'salesorder'  
    salesOrderID = db.Column(db.String(10), primary_key = True)
    receivedDate = db.Column(db.Date)
    orderingDate = db.Column(db.Date)
    completedDate = db.Column(db.Date)
    paymentDate = db.Column(db.Date)
    customerID = db.Column(db.String(10), db.ForeignKey('customer.customerID'), nullable = False)

    def create_id():
        last_sales_order = SalesOrder.query.order_by(
            db.func.cast(db.func.substring(SalesOrder.salesOrderID, 3), db.Integer).desc()).first()
        if last_sales_order:
            last_id = int(last_sales_order.salesOrderID[2:])
            new_id = f'SO{last_id+1}'
        else:
            new_id = 'SO1'
        return new_id

def empty_string(data):
    data = data.strip()
    return data if data else None

def date_handler(data):
    if data == '':
        return None
    else:
        return datetime.strptime(data, '%Y-%m-%d')
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sales_record')
def sales_record():
    return render_template('sales_record.html')

@app.route('/sales', methods=['GET'])
def sales():
    customers = Customer.query.all()

    stock_list = db.session.execute(
        text(
            """
            SELECT 
                P.productName, COALESCE(PURCHASED.quantity, 0) - COALESCE(SOLD.quantity, 0) AS quantity
            FROM PRODUCT P
            LEFT JOIN (
                SELECT productID, SUM(quantity) AS quantity 
                FROM PURCHASEORDERDETAILS 
                GROUP BY productID
            ) PURCHASED ON P.productID = PURCHASED.productID
            LEFT JOIN (
                SELECT SOD.productID, SUM(SOD.quantity) AS quantity 
                FROM SALESORDERDETAILS SOD 
                JOIN SALESORDER SO ON SOD.salesOrderID = SO.salesOrderID
                WHERE SO.orderingDate IS NOT NULL
                GROUP BY SOD.productID
            ) SOLD ON P.productID = SOLD.productID
            WHERE COALESCE(PURCHASED.quantity, 0) - COALESCE(SOLD.quantity, 0) > 0
            """
        )
    ).fetchall()

    ordering_list = db.session.execute(
        text(
            """
            SELECT 
                S.supplierID, S.supplierName, P.productID, P.productName, 
                COALESCE(SOLD.quantity, 0) - COALESCE(PURCHASED.quantity, 0) AS quantity
            FROM SUPPLIER S, PRODUCT P
            LEFT JOIN (
                SELECT productID, SUM(quantity) AS quantity 
                FROM PURCHASEORDERDETAILS 
                GROUP BY productID
            ) PURCHASED ON P.productID = PURCHASED.productID
            LEFT JOIN (
                SELECT productID, SUM(quantity) AS quantity 
                FROM SALESORDERDETAILS
                GROUP BY productID
            ) SOLD ON P.productID = SOLD.productID
            WHERE 
                S.supplierID = P.supplierID
                AND COALESCE(SOLD.quantity, 0) - COALESCE(PURCHASED.quantity, 0) > 0
            """
        )
    ).fetchall()

    ordering_dict = {}
    for order in ordering_list:
        supplierID, supplierName, productID, productName, quantity = order

        if supplierID not in ordering_dict:
            ordering_dict[supplierID] = {'supplierName': supplierName, 'details': []}
        
        ordering_dict[supplierID]['details'].append({
            'productID': productID,
            'productName': productName,
            'quantity': quantity
        })

    finalizingOrders = db.session.execute(
        text(
            """
            SELECT SO.salesOrderID, C.customerName, P.productID, P.productName, SOD.quantity, P.sellingPrice
            FROM SALESORDER SO, CUSTOMER C
            LEFT JOIN SALESORDERDETAILS SOD ON SO.salesOrderID = SOD.salesOrderID
            LEFT JOIN PRODUCT P ON SOD.productID = P.productID
            WHERE C.customerID = SO.customerID AND SO.orderingDate IS NULL AND SO.completedDate IS NULL
            """
        )
    ).fetchall()

    finalizing_dict = {}
    for order in finalizingOrders:
        salesOrderID, customerName, productID, productName, quantity, price = order

        if salesOrderID not in finalizing_dict:
            finalizing_dict[salesOrderID] = {'customerName': customerName, 'details': []}

        finalizing_dict[salesOrderID]['details'].append({
            "productID": productID,
            "productName": productName,
            "quantity": quantity,
            "price": price
        })

    deliveringOrders = db.session.execute(
        text(
            """
            SELECT SO.salesOrderID, C.customerName, strftime('%d-%m-%Y', SO.receivedDate) AS receivedDate,
            P.productID, P.productName, SOD.quantity, P.sellingPrice
            FROM PRODUCT P, CUSTOMER C, SALESORDER SO, SALESORDERDETAILS SOD
            WHERE SO.salesOrderID = SOD.salesOrderID AND SOD.productID = P.productID 
            AND C.customerID = SO.customerID AND SO.orderingDate IS NOT NULL AND SO.completedDate IS NULL 
            """
        )
    ).fetchall()

    delivering_dict = {}
    for order in deliveringOrders:
        salesOrderID, customerName, receivedDate, productID, productName, quantity, price = order

        if customerName not in delivering_dict:
            delivering_dict[customerName] = {}

        if salesOrderID not in delivering_dict[customerName]:
            delivering_dict[customerName][salesOrderID] = {'receivedDate': receivedDate, 'details': []}

        delivering_dict[customerName][salesOrderID]['details'].append({
            "productID": productID,
            "productName": productName,
            "quantity": quantity,
            "price": price
        })
    
    products = Product.query.order_by(db.func.cast(db.func.substring(Product.productID, 2), db.Integer)).all()

    return render_template('sales.html', customers = customers,
                           stock_list = stock_list,
                           ordering_list = ordering_dict.items(), 
                           finalizingOrders = finalizing_dict.items(),
                           deliveringOrders = delivering_dict.items(),
                           products = products)

@app.route('/sales/place_an_order', methods = ['POST'])
def place_an_order():
    supplierIDs = request.form.getlist('supplierID[]')
    productIDs = request.form.getlist('productID[]')
    quantities = request.form.getlist('quantity[]')
    
    ordering_dict = {}
    for supplierID, productID, quantity in zip(supplierIDs, productIDs, quantities):
        if supplierID not in ordering_dict:
            ordering_dict[supplierID] = []
        ordering_dict[supplierID].append({
            'productID': productID,
            'quantity': quantity
        })
    
    for supplierID, details in ordering_dict.items():
        try:
            new_order = PurchaseOrder(
                purchaseOrderID = PurchaseOrder.create_id(),
                orderingDate = datetime.today().date(),
                paymentDate = None,
                supplierID = supplierID
            )
            db.session.add(new_order)
            db.session.commit()
        except:
            return f'There was a problem ordering from {Supplier.query.get(supplierID).supplierName}'
        for detail in details:
            try:
                db.session.execute(
                    purchase_order_details.insert().values(
                        purchaseOrderID = new_order.purchaseOrderID,
                        productID = detail['productID'],
                        quantity = detail['quantity']))
                db.session.commit()
            except:
                return f"There was a problem ordering {Product.query.get(detail['productID']).productName}"
            
    try:
        SalesOrder.query.filter_by(orderingDate = None).update(
            {'orderingDate': datetime.today().date()}
        )
        db.session.commit()
    except:
        return 'There was a problem updating sales order'
    
    return redirect('/sales')

@app.route('/sales/new_sales_order', methods = ['POST'])    
def new_sales_order():
    customerName = empty_string(request.form['customerName'])
    customerPhone = empty_string(request.form['customerPhone'])
    customerAddress = empty_string(request.form['customerAddress'])
    productNames = request.form.getlist('productName[]')
    quantities = request.form.getlist('quantity[]')

    filtered_data = [(productName, quantity)
                     for productName, quantity in zip(productNames, quantities)
                     if empty_string(productName) and empty_string(quantity)]
    if not filtered_data:
        return 'No valid products entered'
    
    existingCustomer = Customer.query.filter_by(customerPhone = customerPhone).first()
    
    if not existingCustomer:
        return render_template('new_customer.html',
                               details = filtered_data,
                               customerName = customerName,
                               customerPhone = customerPhone,
                               customerAddress = customerAddress)
        
    new_order = SalesOrder(
        salesOrderID = SalesOrder.create_id(),
        receivedDate = datetime.today().date(),
        orderingDate = None,
        completedDate = None,
        paymentDate = None,
        customerID = existingCustomer.customerID)
        
    try:
        db.session.add(new_order)
        db.session.commit()
    except:
        return 'There was a problem adding this sales order'

    for productName, quantity in filtered_data:
        product = Product.query.filter_by(productName = productName).first()

        if product:
            productID = product.productID
            try:
                db.session.execute(
                    sales_order_details.insert().values(
                        salesOrderID = new_order.salesOrderID,
                        productID = productID,
                        quantity = quantity))
                db.session.commit()         
            except:
                return "There was a problem adding this detail"
        else:
            return f"Product '{productName}' not found in database."
    
    return redirect('/sales')  

@app.route('/sales/add_customer', methods=['POST'])
def sales_add_customer():
    customerName = empty_string(request.form['customerName'])
    customerPhone = empty_string(request.form['customerPhone'])
    customerAddress = empty_string(request.form['customerAddress'])
    productNames = request.form.getlist('productName[]')
    quantities = request.form.getlist('quantity[]')

    # Create new customer in the database
    new_customer = Customer(
        customerID=Customer.create_id(),
        customerName=customerName,
        customerPhone=customerPhone,
        customerAddress=customerAddress
    )
    try:
        db.session.add(new_customer)
        db.session.commit()
        customerID = new_customer.customerID
    except:
        return 'There was a problem adding this customer'
        
    new_order = SalesOrder(
        salesOrderID = SalesOrder.create_id(),
        receivedDate = datetime.today().date(),
        orderingDate = None,
        completedDate = None,
        paymentDate = None,
        customerID = customerID)
        
    try:
        db.session.add(new_order)
        db.session.commit()
    except:
        return 'There was a problem adding this sales order'

    for productName, quantity in zip(productNames, quantities):
        product = Product.query.filter_by(productName = productName).first()

        if product:
            productID = product.productID
            try:
                db.session.execute(
                    sales_order_details.insert().values(
                        salesOrderID = new_order.salesOrderID,
                        productID = productID,
                        quantity = quantity))
                db.session.commit()         
                
            except:
                return 'There was a problem adding this detail'
        else:
            return f"Product '{productName}' not found in database."
    
    return redirect('/sales')

@app.route('/sales/update_finalizing_order', methods = ['POST'])
def sales_update_finalizing_order():
    salesOrderID = request.form['salesOrderID']
    action = request.form['action']

    if action == 'Update Order':
        productNames = request.form.getlist('productName[]')
        quantities = request.form.getlist('quantity[]')

        filtered_data = [(productName, quantity)
                        for productName, quantity in zip(productNames, quantities)
                        if empty_string(productName) and empty_string(quantity)]
        
        if not filtered_data:
            return redirect('/sales')
        
        try:
            db.session.execute(
                sales_order_details.delete().where(
                    sales_order_details.c.salesOrderID == salesOrderID
                )
            )
            db.session.commit()
        except:
            return 'There was a problem updating this order'
        
        for productName, quantity in filtered_data:
            product = Product.query.filter_by(productName = productName).first()
            if product:
                productID = product.productID
                try:
                    db.session.execute(
                        sales_order_details.insert().values(
                            salesOrderID = salesOrderID,
                            productID = productID,
                            quantity = quantity))
                    db.session.commit()         
                except Exception as e:
                    return str(e)
            else:
                return f"Product '{productName}' not found in database."

    if action == 'delete':
        productID = request.form['productID']
        try:
            stmt = sales_order_details.delete().where(
                (sales_order_details.c.salesOrderID == salesOrderID) &
                (sales_order_details.c.productID == productID)
            )
            db.session.execute(stmt)
            db.session.commit()
        except Exception as e:
            return str(e)
    
    return redirect('/sales')

@app.route('/sales/update_delivering_order', methods = ['POST'])
def sales_update_delivering_order():
    salesOrderID = request.form['salesOrderID']
    action = request.form['action']

    if action == 'Update Order':
        productNames = request.form.getlist('productName[]')
        quantities = request.form.getlist('quantity[]')

        filtered_data = [(productName, quantity)
                        for productName, quantity in zip(productNames, quantities)
                        if empty_string(productName) and empty_string(quantity)]
        
        if not filtered_data:
            return redirect('/sales')
        
        try:
            db.session.execute(
                sales_order_details.delete().where(
                    sales_order_details.c.salesOrderID == salesOrderID
                )
            )
            db.session.commit()
        except:
            return 'There was a problem updating this order'
        
        for productName, quantity in filtered_data:
            product = Product.query.filter_by(productName = productName).first()
            if product:
                productID = product.productID
                try:
                    db.session.execute(
                        sales_order_details.insert().values(
                            salesOrderID = salesOrderID,
                            productID = productID,
                            quantity = quantity))
                    db.session.commit()         
                except Exception as e:
                    return str(e)
            else:
                return f"Product '{productName}' not found in database."

    if action == 'delete':
        productID = request.form['productID']
        try:
            stmt = sales_order_details.delete().where(
                (sales_order_details.c.salesOrderID == salesOrderID) &
                (sales_order_details.c.productID == productID)
            )
            db.session.execute(stmt)
            db.session.commit()
        except Exception as e:
            return str(e)
    
    return redirect('/sales')

@app.route('/sales/deliver_an_order', methods = ['POST'])
def deliver_an_order():
    customerName = request.form['customerName']
    receivedDate = request.form['receivedDate']
    
    customerID = Customer.query.filter_by(customerName = customerName).first().customerID
    receivedDate = datetime.strptime(receivedDate, "%d-%m-%Y").date()
    try:
        SalesOrder.query.filter_by(customerID = customerID, receivedDate = receivedDate).update(
            {'completedDate': datetime.today().date()}
        )
        db.session.commit()
    except Exception as e:
        return str(e)
    return redirect('/sales')

@app.route('/procurement', methods=['GET'])
def procurement():
    supplier_details = db.session.execute(
        text(
            """
            SELECT S.supplierID, S.supplierName, P.productName, P.productCategory, P.productDescription, P.unit,
            P.purchasingPrice, P.sellingPrice
            FROM SUPPLIER S
            LEFT JOIN PRODUCT P ON S.supplierID = P.supplierID
            """
        )
    ).fetchall()

    supplier_dict = {}
    for detail in supplier_details:
        supplierID, supplierName, productName, productCategory, productDescription, unit, purchasingPrice, sellingPrice = detail

        if supplierID not in supplier_dict:
            supplier_dict[supplierID] = {'supplierName': supplierName, 'products':[]}

        supplier_dict[supplierID]['products'].append({
            "productName": productName,
            "productCategory": productCategory,
            "productDescription": productDescription,
            "unit": unit,
            "purchasingPrice": purchasingPrice,
            "sellingPrice": sellingPrice
        })
    
    return render_template('procurement.html', supplierDetails = supplier_dict.items())

@app.route('/procurement/new_supplier', methods = ['POST'])
def procurement_new_supplier():
    supplierName = empty_string(request.form['supplierName'])
    supplierPhone = empty_string(request.form['supplierPhone'])
    supplierAddress = empty_string(request.form['supplierAddress'])

    supplier = Supplier.query.filter_by(supplierPhone = supplierPhone).first()

    if supplier:
        return redirect('/procurement')
    
    supplier_to_add = Supplier(supplierID = Supplier.create_id(), supplierName = supplierName,
                               supplierPhone = supplierPhone, supplierAddress = supplierAddress)

    try:
        db.session.add(supplier_to_add)
        db.session.commit()
    except:
        return 'There was a problem adding this supplier'

    return redirect('/procurement')    

@app.route('/procurement/add_product', methods = ['POST'])
def procurement_add_product():
    supplierID = request.form['supplierID']
    productNames = request.form.getlist('productName[]')
    productCategory = request.form.getlist('productCategory[]')
    productDescription = request.form.getlist('productDescription[]')
    unit = request.form.getlist('unit[]')
    purchasingPrice = request.form.getlist('purchasingPrice[]')
    sellingPrice = request.form.getlist('sellingPrice[]')

    filtered_data = [(productName, empty_string(productCategory), empty_string(productDescription), 
                      empty_string(unit), purchasingPrice, sellingPrice)
                     for productName, productCategory, productDescription, unit, purchasingPrice, sellingPrice 
                     in zip(productNames, productCategory, productDescription, unit, purchasingPrice, sellingPrice)
                     if empty_string(productName) and empty_string(purchasingPrice) and empty_string(sellingPrice)]
    
    if not filtered_data:
        return redirect('/procurement')
    
    supplier_to_add = Supplier.query.get_or_404(supplierID)

    for productName, productCategory, productDescription, unit, purchasingPrice, sellingPrice in filtered_data:
        try:
            new_product = Product(productID = Product.create_id(), productName = productName,
                                  productCategory = productCategory, productDescription = productDescription,
                                  unit = unit, purchasingPrice = purchasingPrice, sellingPrice = sellingPrice, 
                                  supplierID = supplier_to_add.supplierID)
            db.session.add(new_product)
            db.session.commit()
        except:
            return 'There was a problem adding this product' 
    
    return redirect('/procurement')

@app.route('/suggest_customer', methods=['GET'])
def get_customer():
    name = request.args.get('name')
    # Query the database for the existing customer
    customer = Customer.query.filter_by(customerName=name).first()
    
    if customer:
        return jsonify({"phone": customer.customerPhone, "address": customer.customerAddress})
    
    return jsonify({"phone": "", "address": ""})

@app.route('/customer', methods = ['GET', 'POST'])
def customer():
    # if the user enters customer's info, create a new customer and insert it into the database and return to homepage
    if request.method == 'POST':
        customerID = Customer.create_id()
        customerName = empty_string(request.form['customerName'])
        customerPhone = empty_string(request.form['customerPhone'])
        customerAddress = empty_string(request.form['customerAddress'])

        phones = [phone[0] for phone in Customer.query.with_entities(Customer.customerPhone).all()]
        if customerPhone not in phones:
            new_customer = Customer(customerID = customerID, customerName = customerName, 
                                customerPhone = customerPhone, customerAddress = customerAddress)
        
            try:
                db.session.add(new_customer)
                db.session.commit()
                return redirect('/customer')
        
            except:
                return 'There was a problem adding this customer'
        else: 
            return redirect('/customer')
    
    # If no customer to be inserted left, display all customers in the database
    else:
        customers = Customer.query.order_by(
            db.func.cast(db.func.substring(Customer.customerID, 2), db.Integer)).all()
        return render_template('customer.html', customers = customers)

@app.route('/customer/delete/<id>')
def delete_customer(id):
    #Get customer by their id in the URL, delete it and return to homepage
    customer_to_delete = Customer.query.get_or_404(id)

    try:
        db.session.delete(customer_to_delete)
        db.session.commit()
        return redirect('/customer')
    except:
        return 'There was an issue deleting this customer'
    
@app.route('/customer/update/<id>', methods = ['GET', 'POST'])
def update_customer(id):
    #Get customer by their id in the URL
    customer_to_update = Customer.query.get_or_404(id)
    
    #Assign the customer's info according to the user's input, insert into the database and return to homepage
    if request.method == 'POST':
        customer_to_update.customerName = empty_string(request.form['customerName'])
        customer_to_update.customerPhone = empty_string(request.form['customerPhone'])
        customer_to_update.customerAddress = empty_string(request.form['customerAddress'])

        try:
            db.session.commit()
            return redirect('/customer')
        except:
            return 'There was a problem updating this customer'

    #Turn to the updating page of the customer when the customer press the Update button    
    else:
        return render_template('update_customer.html', customer = customer_to_update)

@app.route('/supplier', methods = ['GET', 'POST'])
def supplier():
    # if the user enters supplier's info, create a new supplier and insert it into the database and return to homepage
    if request.method == 'POST':
        supplierID = Supplier.create_id()
        supplierName = empty_string(request.form['supplierName'])
        supplierPhone = empty_string(request.form['supplierPhone'])
        supplierAddress = empty_string(request.form['supplierAddress'])
        phones = [phone[0] for phone in Supplier.query.with_entities(Supplier.supplierPhone).all()]

        if supplierPhone not in phones:
            new_supplier = Supplier(supplierID = supplierID, supplierName = supplierName, 
                                    supplierPhone = supplierPhone, supplierAddress = supplierAddress)
            try:
                db.session.add(new_supplier)
                db.session.commit()
                return redirect('/supplier')
            
            except:
                return 'There was a problem adding this supplier'
        else:
            return redirect('/supplier')
    
    # If no supplier to be inserted left, display all suppliers in the database
    else:
        suppliers = Supplier.query.order_by(
            db.func.cast(db.func.substring(Supplier.supplierID, 2), db.Integer)).all()
        return render_template('supplier.html', suppliers = suppliers)

@app.route('/supplier/delete/<id>')
def delete_supplier(id):
    #Get supplier by their id in the URL, delete it and return to homepage
    supplier_to_delete = Supplier.query.get_or_404(id)

    try:
        db.session.delete(supplier_to_delete)
        db.session.commit()
        return redirect('/supplier')
    except:
        return 'There was an issue deleting this supplier'
    
@app.route('/supplier/update/<id>', methods = ['GET', 'POST'])
def update_supplier(id):
    #Get supplier by their id in the URL
    supplier_to_update = Supplier.query.get_or_404(id)
    
    #Assign the supplier's info according to the user's input, insert into the database and return to homepage
    if request.method == 'POST':
        supplier_to_update.supplierName = empty_string(request.form['supplierName'])
        supplier_to_update.supplierPhone = empty_string(request.form['supplierPhone'])
        supplier_to_update.supplierAddress = empty_string(request.form['supplierAddress'])

        try:
            db.session.commit()
            return redirect('/supplier')
        except:
            return 'There was a problem updating this supplier'

    #Turn to the updating page of the supplier when the supplier press the Update button    
    else:
        return render_template('update_supplier.html', supplier = supplier_to_update)



@app.route('/product', methods = ['GET', 'POST'])
def product():
    if request.method == 'POST':
        productID = Product.create_id()
        productName = empty_string(request.form['productName'])
        productCategory = empty_string(request.form['productCategory'])
        productDescription = empty_string(request.form['productDescription'])
        unit = empty_string(request.form['unit'])
        purchasingPrice = empty_string(request.form['purchasingPrice'])
        sellingPrice = empty_string(request.form['sellingPrice'])
        supplierID = empty_string(request.form['supplierID'])
        supplierName = empty_string(request.form['supplierName'])

        supplierIDs = [supplier_id[0] for supplier_id in Supplier.query.with_entities(
            Supplier.supplierID).filter(Supplier.supplierName == supplierName).all()]
        product_names = [product_name[0] for product_name in Product.query.with_entities(Product.productName).all()]

        if productName not in product_names:
            if supplierID:
                new_product = Product(productID = productID, productName = productName,
                                      productCategory = productCategory, productDescription = productDescription,
                                      unit = unit, purchasingPrice = purchasingPrice, sellingPrice = sellingPrice, 
                                      supplierID = supplierID)
            elif supplierName:
                supplierIDs = [supplier_id[0] for supplier_id in Supplier.query.with_entities(
                    Supplier.supplierID).filter(Supplier.supplierName == supplierName).all()]
                if len(supplierIDs) > 1:
                    return 'You have to enter this product with Supplier ID'
                elif len(supplierIDs) == 1:
                    new_product = Product(productID = productID, productName = productName,
                                          productCategory = productCategory, productDescription = productDescription,
                                          unit = unit, purchasingPrice = purchasingPrice, sellingPrice = sellingPrice,
                                          supplierID = supplierIDs[0])
                else:
                    return 'Supplier Name does not exist'
            try:
                db.session.add(new_product)
                db.session.commit()
                return redirect('/product')
            
            except:
                return 'There was a problem adding this product'
        else:
            return 'Product name already used'
    else:
        products = db.session.query(
            Product.productID,
            Product.productName,
            Product.productCategory,
            Product.productDescription,
            Product.unit,
            Product.purchasingPrice,
            Product.sellingPrice,
            Product.supplierID,
            Supplier.supplierName
        ).join(
            Supplier, Supplier.supplierID == Product.supplierID
        ).order_by(
             db.func.cast(db.func.substring(Product.productID, 2), db.Integer)
        ).all()
        suppliers = Supplier.query.order_by(
            db.func.cast(db.func.substring(Supplier.supplierID, 2), db.Integer)).all()
        return render_template('product.html', products = products, suppliers = suppliers)
    
@app.route('/product/delete/<id>')
def delete_product(id):
    product_to_delete = Product.query.get_or_404(id)
    try:
        db.session.delete(product_to_delete)
        db.session.commit()
        return redirect('/product')
    except:
        return 'There was a problem deleting this product'

@app.route('/product/update/<id>', methods = ['GET', 'POST'])
def update_product(id):
    product_to_update = Product.query.get_or_404(id)

    if request.method == 'POST':
        product_to_update.productName = empty_string(request.form['productName'])
        product_to_update.productCategory = empty_string(request.form['productCategory'])
        product_to_update.productDescription = empty_string(request.form['productDescription'])
        product_to_update.unit = empty_string(request.form['unit'])
        product_to_update.purchasingPrice = empty_string(request.form['purchasingPrice'])
        product_to_update.sellingPrice = empty_string(request.form['sellingPrice'])
        product_to_update.supplierID = request.form['supplierID']
        try:
            db.session.commit()
            return redirect('/product')
        except:
            return 'There was a problem updating this product'
    else:
        return render_template('update_product.html', product = product_to_update)

@app.route('/purchase_order', methods = ['GET', 'POST'])
def purchase_order():
    if request.method == 'POST':
        purchaseOrderID = PurchaseOrder.create_id()
        orderingDate = date_handler(request.form['orderingDate'])
        paymentDate = date_handler(request.form['paymentDate'])
        supplierID = empty_string(request.form['supplierID'])
        supplierName = empty_string(request.form['supplierName'])

        if supplierID:
            new_purchase_order = PurchaseOrder(purchaseOrderID = purchaseOrderID, orderingDate = orderingDate,
                                               paymentDate = paymentDate, supplierID = supplierID)
        if supplierName:
            supplierIDs = [supplier_id[0] for supplier_id in Supplier.query.with_entities(
                Supplier.supplierID).filter(Supplier.supplierName == supplierName).all()]
            if len(supplierIDs) > 1:
                return 'You have to enter this purchase order with Supplier ID'
            elif len(supplierIDs) == 1:
                new_purchase_order = PurchaseOrder(purchaseOrderID = purchaseOrderID, orderingDate = orderingDate,
                                                   paymentDate = paymentDate, supplierID = supplierIDs[0])
        try:
            db.session.add(new_purchase_order)
            db.session.commit()
            return redirect('/purchase_order')
        except:
            return 'There was a problem adding this purchase order'
    else:
        today = datetime.today().strftime('%Y-%m-%d')
        purchase_orders = db.session.query(
            PurchaseOrder.purchaseOrderID,
            PurchaseOrder.orderingDate,
            PurchaseOrder.paymentDate,
            PurchaseOrder.supplierID,
            Supplier.supplierName
            ).join(
                Supplier, Supplier.supplierID == PurchaseOrder.supplierID
                ).order_by(
                    db.func.cast(
                        db.func.substring(PurchaseOrder.purchaseOrderID, 3), db.Integer
                    )
                ).all()
        suppliers = Supplier.query.order_by(
            db.func.cast(db.func.substring(Supplier.supplierID, 2), db.Integer)).all()
        return render_template('purchase_order.html', purchase_orders = purchase_orders, suppliers = suppliers, today = today)
    
@app.route('/purchase_order/delete/<id>')
def delete_purchase_order(id):
    purchase_order_to_delete = PurchaseOrder.query.get_or_404(id)

    try:
        db.session.delete(purchase_order_to_delete)
        db.session.commit()
        return redirect('/purchase_order')
    except:
        return 'There was a problem deleting this purchase order'

@app.route('/purchase_order/update/<id>', methods = ['GET', 'POST'])
def update_purchase_order(id):
    purchase_order_to_update = PurchaseOrder.query.get_or_404(id)
    if request.method == 'POST':
        purchase_order_to_update.orderingDate = date_handler(request.form['orderingDate'])
        purchase_order_to_update.paymentDate = date_handler(request.form['paymentDate'])
        purchase_order_to_update.supplierID = request.form['supplierID']

        try:
            db.session.commit()
            return redirect('/purchase_order')
        except:
            return 'There was a problem updating this purchase order'
        
    else:
        return render_template('update_purchase_order.html', purchase_order = purchase_order_to_update)

@app.route('/purchase_order/add_products/<id>', methods = ['GET','POST'])
def add_products_purchase_order(id):
    purchase_order_to_add = PurchaseOrder.query.get_or_404(id)
    if request.method =='POST':
        product = Product.query.filter(Product.productName == request.form['productName']).first()
        purchaseOrderID = purchase_order_to_add.purchaseOrderID
        productID = product.productID
        quantity = request.form['quantity']

        try:
            db.session.execute(
                purchase_order_details.insert().values(
                    purchaseOrderID = purchaseOrderID,
                    productID = productID,
                    quantity = quantity))
            db.session.commit()
            return redirect(f'/purchase_order/add_products/{id}')
        
        except:
            return 'There was a problem inserting this product'
    else:
        results = db.session.query(purchase_order_details.c.purchaseOrderID,
                                   purchase_order_details.c.productID,
                                   Product.productName,
                                   purchase_order_details.c.quantity,
                                   Product.purchasingPrice
                                   ).join(Product, purchase_order_details.c.productID == Product.productID).filter(
                                       purchase_order_details.c.purchaseOrderID == id
                                   ).all()
        products = Product.query.filter(
            Product.supplierID == purchase_order_to_add.supplierID
            ).order_by(db.func.cast(db.func.substring(Product.productID, 2), db.Integer)).all()
        
        return render_template('add_products_purchase_order.html', 
                               purchase_order = purchase_order_to_add,
                               results = results,
                               products = products)

@app.route('/purchase_order/add_products/delete/<purchaseOrderID>/<productID>')
def delete_purchase_order_details(purchaseOrderID, productID):
    try:
        db.session.execute(
            text("""
                 DELETE FROM purchaseorderdetails 
                 WHERE purchaseOrderID = :purchaseOrderID
                 AND productID = :productID"""),
                 {'purchaseOrderID': purchaseOrderID, 'productID': productID})
        db.session.commit()
        return redirect(f'/purchase_order/add_products/{purchaseOrderID}')
    
    except:
        return 'There was a problem deleting this product'

@app.route('/sales_order', methods = ['GET', 'POST'])
def sales_order():
    if request.method == 'POST':
        salesOrderID = SalesOrder.create_id()
        receivedDate = date_handler(request.form['receivedDate'])
        orderingDate = date_handler(request.form['orderingDate'])
        paymentDate = date_handler(request.form['paymentDate'])
        completedDate = date_handler(request.form['completedDate'])
        customerID = empty_string(request.form['customerID'])
        customerName =empty_string(request.form['customerName'])
        print(customerName)

        if customerID:
            new_sales_order = SalesOrder(salesOrderID = salesOrderID, receivedDate = receivedDate,
                                          orderingDate = orderingDate, completedDate = completedDate, 
                                         paymentDate = paymentDate, customerID = customerID)
        elif customerName:
            customerIDs = [customer_id[0] for customer_id in Customer.query.with_entities(
                Customer.customerID).filter(Customer.customerName == customerName).all()]
            if len(customerIDs) >1:
                return 'You have to enter this sales order with Customer ID'
            elif len(customerIDs) == 1:
                new_sales_order = SalesOrder(salesOrderID = salesOrderID, orderingDate = orderingDate,
                                             completedDate = completedDate, paymentDate = paymentDate, 
                                             customerID = customerIDs[0])
        
        try:
            db.session.add(new_sales_order)
            db.session.commit()
            return redirect('/sales_order')
        except:
            return 'There was a problem adding this sales order'
    else:
        customers = Customer.query.order_by(
            db.func.cast(db.func.substring(Customer.customerID, 2), db.Integer)).all()
        today = datetime.today().strftime('%Y-%m-%d')
        sales_orders = db.session.query(
            SalesOrder.salesOrderID,
            SalesOrder.receivedDate,
            SalesOrder.orderingDate,
            SalesOrder.completedDate,
            SalesOrder.paymentDate,
            SalesOrder.customerID,
            Customer.customerName
            ).join(
                Customer, Customer.customerID == SalesOrder.customerID
                ).order_by(
                    db.func.cast(
                        db.func.substring(SalesOrder.salesOrderID, 3), db.Integer
                    )
                ).all()

        return render_template('sales_order.html', sales_orders = sales_orders, customers = customers, today = today)
    
@app.route('/sales_order/delete/<id>')
def delete_sales_order(id):
    sales_order_to_delete = SalesOrder.query.get_or_404(id)

    try:
        db.session.delete(sales_order_to_delete)
        db.session.commit()
        return redirect('/sales_order')
    except:
        return 'There was a problem deleting this sales order'

@app.route('/sales_order/update/<id>', methods = ['GET', 'POST'])
def update_sales_order(id):
    sales_order_to_update = SalesOrder.query.get_or_404(id)
    if request.method == 'POST':
        sales_order_to_update.receivedDate = date_handler(request.form['receivedDate'])
        sales_order_to_update.orderingDate = date_handler(request.form['orderingDate'])
        sales_order_to_update.paymentDate = date_handler(request.form['paymentDate'])
        sales_order_to_update.customerID = request.form['customerID']

        try:
            db.session.commit()
            return redirect('/sales_order')
        except:
            return 'There was a problem updating this sales order'
        
    else:
        return render_template('update_sales_order.html', sales_order = sales_order_to_update)

@app.route('/sales_order/add_products/<id>', methods = ['GET','POST'])
def add_products_sales_order(id):
    sales_order_to_add = SalesOrder.query.get_or_404(id)
    if request.method == 'POST':
        product = Product.query.filter(Product.productName == request.form['productName']).first()
        salesOrderID = sales_order_to_add.salesOrderID
        productID = product.productID
        quantity = request.form['quantity']

        try:
            db.session.execute(
                sales_order_details.insert().values(
                    salesOrderID = salesOrderID,
                    productID = productID,
                    quantity = quantity))
            db.session.commit()
            return redirect(f'/sales_order/add_products/{id}')
        
        except:
            return 'There was a problem inserting this product'
    else:
        results = db.session.query(sales_order_details.c.salesOrderID,
                                   sales_order_details.c.productID,
                                   Product.productName,
                                   sales_order_details.c.quantity,
                                   Product.sellingPrice
                                   ).join(Product, sales_order_details.c.productID == Product.productID).filter(
                                       sales_order_details.c.salesOrderID == id
                                   ).all()
        products = Product.query.order_by(db.func.cast(db.func.substring(Product.productID, 2), db.Integer)).all()
        
        return render_template('add_products_sales_order.html', 
                               sales_order = sales_order_to_add,
                               results = results,
                               products = products)

@app.route('/sales_order/add_products/delete/<salesOrderID>/<productID>')
def delete_sales_order_details(salesOrderID, productID):
    try:
        db.session.execute(
            text("""
                 DELETE FROM salesorderdetails 
                 WHERE salesOrderID = :salesOrderID
                 AND productID = :productID"""),
                 {'salesOrderID': salesOrderID, 'productID': productID})
        db.session.commit()
        return redirect(f'/sales_order/add_products/{salesOrderID}')
    

    except Exception as e:
        print(f"Error: {e}")
        return 'There was a problem deleting this product'

@app.route('/management')
def management():
    return render_template('management.html')

@app.route('/management/customer_debt')
def customer_debt():
    results = db.session.execute(
        text("""SELECT C.customerID, C.customerName, SOD.quantity*SOD.price as debt 
             FROM customer C, salesorder SO, salesorderdetails SOD
             WHERE C.customerID = SO.customerID AND SO.salesOrderID = SOD.salesOrderID""")
    )
    return render_template('customer_debt.html', results = results)

@app.route('/management/customer_debt/details/<id>')
def customer_debt_details(id):
    results = db.session.execute(
        text("""SELECT C.customerName, P.productName, SO.receivedDate, SOD.quantity, SOD.price, SOD.quantity*SOD.price as total 
             FROM customer C, product P, salesorder SO, salesorderdetails SOD
             WHERE C.customerID = SO.customerID AND SO.salesOrderID = SOD.salesOrderID 
             AND SOD.productID = P.productID AND C.customerID = :id"""),{'id':id}
    )
    return render_template('customer_debt_details.html', results = results)

@app.route('/management/stock')
def stock():
    results = list(db.session.execute(
        text("""
            SELECT 
                P.productName, 
                SUM(POD.quantity)-SUM(SOD.quantity) as quantity,
                (SUM(POD.quantity)-SUM(SOD.quantity))*LATESTPRICE.price as totalPrice
            FROM 
                product P, purchaseorderdetails POD, salesorderdetails SOD, (
                    SELECT 
                        POD_INNER.productID, POD_INNER.price 
                    FROM 
                        purchaseorder PO_INNER, purchaseorderdetails POD_INNER
                    WHERE 
                        PO_INNER.purchaseOrderID = POD_INNER.purchaseOrderID
                    AND 
                        PO_INNER.receivedDate = (
                            SELECT 
                                MAX(PO_INNER2.receivedDate) 
                            FROM 
                                purchaseorder PO_INNER2, purchaseorderdetails POD_INNER2
                            WHERE 
                                PO_INNER2.purchaseOrderID = POD_INNER2.purchaseOrderID
                            AND 
                                POD_INNER.productID = POD_INNER2.productID)) LATESTPRICE
            WHERE 
                P.productID = SOD.productID AND P.productID = POD.productID 
            AND 
                LATESTPRICE.productID = P.productID
            GROUP BY P.productName, LATESTPRICE.price"""))
    )
    total_value = sum(row.totalPrice for row in results)
    return render_template('stock.html', results = results, total_value = total_value)

#Run the web and create the database with the app's context
if __name__ == '__main__':
    app.app_context().push()
    db.create_all()
    app.run(host='0.0.0.0', debug=True)