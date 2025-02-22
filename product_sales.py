# from sqlalchemy import create_engine
from sqlalchemy import text
from flask import Flask, request, render_template, redirect
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

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
                                  db.Column('quantity', db.Integer),
                                  db.Column('price', db.Integer))

sales_order_details = db.Table('salesorderdetails',
                                  db.Column('salesOrderID', db.String(10), db.ForeignKey('salesorder.salesOrderID'), primary_key = True),
                                  db.Column('productID', db.String(10), db.ForeignKey('product.productID'), primary_key = True),
                                  db.Column('quantity', db.Integer),
                                  db.Column('price', db.Integer))

class Customer(db.Model):
    customerID = db.Column(db.String(10), primary_key=True)
    customerName = db.Column(db.String(30))
    customerPhone = db.Column(db.String(10))
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
    supplierPhone = db.Column(db.String(10))
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
    productName = db.Column(db.String(30))
    productCategory = db.Column(db.String(30))
    productDescription = db.Column(db.String(100))
    unit = db.Column(db.String(30))
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
    orderDate = db.Column(db.Date)
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
    orderDate = db.Column(db.Date)
    paymentDate = db.Column(db.Date)
    paymentMethod = db.Column(db.String(30))
    deliveryFee = db.Column(db.Integer)
    discount = db.Column(db.Integer)
    deliveryPerson = db.Column(db.String(30))
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
    if data =='':
        return None
    else:
        return data

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
        supplierID = empty_string(request.form['supplierID'])
        supplierName = empty_string(request.form['supplierName'])

        supplierIDs = [supplier_id[0] for supplier_id in Supplier.query.with_entities(
            Supplier.supplierID).filter(Supplier.supplierName == supplierName).all()]
        product_names = [product_name[0] for product_name in Product.query.with_entities(Product.productName).all()]

        if productName not in product_names:
            if supplierID:
                new_product = Product(productID = productID, productName = productName,
                                      productCategory = productCategory, productDescription = productDescription,
                                      unit = unit, supplierID = supplierID)
            elif supplierName:
                supplierIDs = [supplier_id[0] for supplier_id in Supplier.query.with_entities(
                    Supplier.supplierID).filter(Supplier.supplierName == supplierName).all()]
                if len(supplierIDs) > 1:
                    return 'You have to enter this product with Supplier ID'
                elif len(supplierIDs) == 1:
                    new_product = Product(productID = productID, productName = productName,
                                          productCategory = productCategory, productDescription = productDescription,
                                          unit = unit, supplierID = supplierIDs[0])
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
        orderDate = date_handler(request.form['orderDate'])
        paymentDate = date_handler(request.form['paymentDate'])
        supplierID = empty_string(request.form['supplierID'])
        supplierName = empty_string(request.form['supplierName'])

        if supplierID:
            new_purchase_order = PurchaseOrder(purchaseOrderID = purchaseOrderID, orderDate = orderDate,
                                               paymentDate = paymentDate, supplierID = supplierID)
        if supplierName:
            supplierIDs = [supplier_id[0] for supplier_id in Supplier.query.with_entities(
                Supplier.supplierID).filter(Supplier.supplierName == supplierName).all()]
            if len(supplierIDs) > 1:
                return 'You have to enter this purchase order with Supplier ID'
            elif len(supplierIDs) == 1:
                new_purchase_order = PurchaseOrder(purchaseOrderID = purchaseOrderID, orderDate = orderDate,
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
            PurchaseOrder.orderDate,
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
        purchase_order_to_update.orderDate = date_handler(request.form['orderDate'])
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
        price = request.form['price']

        try:
            db.session.execute(
                purchase_order_details.insert().values(
                    purchaseOrderID = purchaseOrderID,
                    productID = productID,
                    quantity = quantity,
                    price = price))
            db.session.commit()
            return redirect(f'/purchase_order/add_products/{id}')
        
        except:
            return 'There was a problem inserting this product'
    else:
        results = db.session.query(purchase_order_details.c.purchaseOrderID,
                                   purchase_order_details.c.productID,
                                   Product.productName,
                                   purchase_order_details.c.quantity,
                                   purchase_order_details.c.price
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
        orderDate = date_handler(request.form['orderDate'])
        paymentDate = date_handler(request.form['paymentDate'])
        paymentMethod = empty_string(request.form['paymentMethod'])
        deliveryFee = request.form['deliveryFee']
        discount = request.form['discount']
        deliveryPerson = empty_string(request.form['deliveryPerson'])
        customerID = empty_string(request.form['customerID'])
        customerName =empty_string(request.form['customerName'])
        print(customerName)

        if customerID:
            new_sales_order = SalesOrder(salesOrderID = salesOrderID, orderDate = orderDate,
                                         paymentDate = paymentDate, paymentMethod = paymentMethod,
                                         deliveryFee = deliveryFee, discount = discount,
                                         deliveryPerson = deliveryPerson, customerID = customerID)
        elif customerName:
            customerIDs = [customer_id[0] for customer_id in Customer.query.with_entities(
                Customer.customerID).filter(Customer.customerName == customerName).all()]
            if len(customerIDs) >1:
                return 'You have to enter this sales order with Customer ID'
            elif len(customerIDs) == 1:
                new_sales_order = SalesOrder(salesOrderID = salesOrderID, orderDate = orderDate,
                                             paymentDate = paymentDate, paymentMethod = paymentMethod,
                                             deliveryFee = deliveryFee, discount = discount,
                                             deliveryPerson = deliveryPerson, customerID = customerIDs[0])
        
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
            SalesOrder.orderDate,
            SalesOrder.paymentDate,
            SalesOrder.paymentMethod,
            SalesOrder.deliveryFee,
            SalesOrder.discount,
            SalesOrder.deliveryPerson,
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
        sales_order_to_update.orderDate = date_handler(request.form['orderDate'])
        sales_order_to_update.paymentDate = date_handler(request.form['paymentDate'])
        sales_order_to_update.paymentMethod = empty_string(request.form['paymentMethod'])
        sales_order_to_update.deliveryFee = request.form['deliveryFee']
        sales_order_to_update.discount = request.form['discount']
        sales_order_to_update.deliveryPerson = empty_string(request.form['deliveryPerson'])
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
        price = request.form['price']

        try:
            db.session.execute(
                sales_order_details.insert().values(
                    salesOrderID = salesOrderID,
                    productID = productID,
                    quantity = quantity,
                    price = price))
            db.session.commit()
            return redirect(f'/sales_order/add_products/{id}')
        
        except:
            return 'There was a problem inserting this product'
    else:
        results = db.session.query(sales_order_details.c.salesOrderID,
                                   sales_order_details.c.productID,
                                   Product.productName,
                                   sales_order_details.c.quantity,
                                   sales_order_details.c.price
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
        text("""SELECT C.customerName, P.productName, SO.orderDate, SOD.quantity, SOD.price, SOD.quantity*SOD.price as total 
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
                        PO_INNER.orderDate = (
                            SELECT 
                                MAX(PO_INNER2.orderDate) 
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