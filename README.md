# Retail Management Web App
A web app designed for small retailers to efficiently track customer, supplier, product data as well as manage procurement, sales, stock and debts.

This app is built using Flask for the back-end, HTML, CSS, and JavaScript for the front-end, and SQLite as the database system.

## Prerequisites

1. Clone this repository and navigate into the project directory:

   ```bash
   git clone https://github.com/nhatthanhduong/Sales-Management
   cd Sales-Management
   ```
2. Build and run the Docker container
    ```shell
    docker-compose up -d
    ```
This will set up and run the app inside the Docker container

## User Guide

1. The app has 4 main parts:
    - Home Page & Navigation Bar: Access different sections of the app
    - Sales: Manage customer orders, stock tracking, ordering list, deliveries and payments.
    - Procurement: Manage suppliers and their products
    - Database: Store and display information about customers, suppliers, products, purchase orders and sales orders

![image](https://github.com/nhatthanhduong/Sales-Management/blob/master/user_guide/home.png)

2. Procurement:
    - Click the "+" button to add a new supplier
    - Click on a supplier’s card to view their products or add a new product

![image](https://github.com/nhatthanhduong/Sales-Management/blob/master/user_guide/procurement.png)
![image](https://github.com/nhatthanhduong/Sales-Management/blob/master/user_guide/procurement_add.png)

3. Sales:
    1. Managing Orders:
        - Use the "+" button to create a new sales order
        - Enter customer details (existing customers will be auto-fetched based on phone number)
        - Select products and quantities for the order
        - Click on the Stock button to track stock and List button to view list of ordering from suppliers
    2. Finalizing Orders:
        - Newly created orders appear in the Finalizing section
        - Once finalized, the system updates stock availability and generates a procurement order if needed
    3. Ordering from Suppliers:
        - Items that need to be replenished appear in the Ordering List
        - Once an order is placed with suppliers, all related sales orders move to the Delivering section
    4. Delivering Orders:
        - Orders waiting for delivery are listed in the Delivering section
        - Once an order is delivered, click the "Delivered" button to update its status
    5. Unpaid Orders:
        - Delivered orders appear in the Unpaid section
        - Click the "Paid" button to mark an order as paid
        - Once paid, the order is removed from the pending list
    6. Viewing All Orders: 
        - Click "View All Orders" to access the full order history

![image](https://github.com/nhatthanhduong/Sales-Management/blob/master/user_guide/sales.png)
![image](https://github.com/nhatthanhduong/Sales-Management/blob/master/user_guide/sales_add.png)

4. Database:
    - The Database Page displays all data related to customers, suppliers, products, purchase orders, and sales orders
    - User can add, delete or update records directly from this page

![image](https://github.com/nhatthanhduong/Sales-Management/blob/master/user_guide/database.png)



