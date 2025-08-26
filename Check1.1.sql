CREATE DATABASE Check1;
USE Check1;


-- CUSTOMER
CREATE TABLE CUSTOMER (
    CustomerID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    ContactInfo VARCHAR(255) NOT NULL,
    Address VARCHAR(255) NOT NULL
);

-- SUPPLIER
CREATE TABLE SUPPLIER (
    SupplierID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    ContactInfo VARCHAR(255) NOT NULL
);

-- PRODUCT
CREATE TABLE PRODUCT (
    ProductID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    Description TEXT,
    SupplierID INT,
    FOREIGN KEY (SupplierID) REFERENCES SUPPLIER(SupplierID) ON DELETE CASCADE
);

-- WAREHOUSE
CREATE TABLE WAREHOUSE (
    WarehouseID INT AUTO_INCREMENT PRIMARY KEY,
    Location VARCHAR(255) NOT NULL,
    Capacity INT NOT NULL
);


-- USERS TABLE
CREATE TABLE USERS (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    Username VARCHAR(255) NOT NULL UNIQUE,
    PasswordHash VARCHAR(255) NOT NULL,
    Role ENUM('Admin', 'Manager', 'Employee') NOT NULL,
    IsActive BOOLEAN DEFAULT TRUE
);


-- SHIPMENT
CREATE TABLE SHIPMENT (
    ShipmentID INT AUTO_INCREMENT PRIMARY KEY,
    ShipmentDate DATE NOT NULL,
    WarehouseID INT,
    FOREIGN KEY (WarehouseID) REFERENCES WAREHOUSE(WarehouseID) ON DELETE CASCADE
);

-- ORDERS 
CREATE TABLE ORDERS (
    OrderID INT AUTO_INCREMENT PRIMARY KEY,
    OrderDate DATE NOT NULL,
    CustomerID INT,
    ShipmentID INT,
    FOREIGN KEY (CustomerID) REFERENCES CUSTOMER(CustomerID) ON DELETE CASCADE,
    FOREIGN KEY (ShipmentID) REFERENCES SHIPMENT(ShipmentID) ON DELETE CASCADE
);

-- ORDER_PRODUCT 
CREATE TABLE ORDER_PRODUCT (
    OrderProductID INT AUTO_INCREMENT PRIMARY KEY,
    OrderID INT,
    ProductID INT,
    QuantityOrdered INT NOT NULL, 
    FOREIGN KEY (OrderID) REFERENCES ORDERS(OrderID) ON DELETE CASCADE,
    FOREIGN KEY (ProductID) REFERENCES PRODUCT(ProductID) ON DELETE CASCADE
);

-- WAREHOUSE_INVENTORY
CREATE TABLE WAREHOUSE_INVENTORY (
    WarehouseInventoryID INT AUTO_INCREMENT PRIMARY KEY,
    WarehouseID INT,
    ProductID INT,
    Quantity INT NOT NULL DEFAULT 0,
    FOREIGN KEY (WarehouseID) REFERENCES WAREHOUSE(WarehouseID) ON DELETE CASCADE,
    FOREIGN KEY (ProductID) REFERENCES PRODUCT(ProductID) ON DELETE CASCADE
);

-- INVENTORY_MOVEMENT
CREATE TABLE INVENTORY_MOVEMENT (
    MovementID INT AUTO_INCREMENT PRIMARY KEY,
    ProductID INT,
    WarehouseFromID INT,
    WarehouseToID INT,
    OrderID INT,
    ShipmentID INT,
    QuantityMoved INT NOT NULL,
    MovementDate DATE NOT NULL,
    MovementType ENUM('Transfer', 'Restock', 'Sale') NOT NULL,
    FOREIGN KEY (ProductID) REFERENCES PRODUCT(ProductID) ON DELETE CASCADE,
    FOREIGN KEY (WarehouseFromID) REFERENCES WAREHOUSE(WarehouseID) ON DELETE CASCADE,
    FOREIGN KEY (WarehouseToID) REFERENCES WAREHOUSE(WarehouseID) ON DELETE CASCADE,
    FOREIGN KEY (OrderID) REFERENCES ORDERS(OrderID) ON DELETE CASCADE,
    FOREIGN KEY (ShipmentID) REFERENCES SHIPMENT(ShipmentID) ON DELETE CASCADE
);

-- USER-WAREHOUSE MAPPING (only for Managers)
CREATE TABLE USER_WAREHOUSE (
    UserID INT,
    WarehouseID INT,
    PRIMARY KEY (UserID, WarehouseID),
    FOREIGN KEY (UserID) REFERENCES USERS(UserID) ON DELETE CASCADE,
    FOREIGN KEY (WarehouseID) REFERENCES WAREHOUSE(WarehouseID) ON DELETE CASCADE
);



-- Inserting sample data

-- CUSTOMER
INSERT INTO CUSTOMER (Name, ContactInfo, Address)
VALUES
('Amit Sharma', 'amit.sharma@gmail.com', 'Sector 15, Gurugram, Haryana'),
('Priya Iyer', 'priya.iyer@gmail.com', 'JP Nagar, Bangalore, Karnataka'),
('Rahul Singh', 'rahul.singh@gmail.com', 'Powai, Mumbai, Maharashtra'),
('Neha Verma', 'neha.verma@gmail.com', 'Salt Lake, Kolkata, West Bengal'),
('Ravi Patel', 'ravi.patel@gmail.com', 'Satellite, Ahmedabad, Gujarat');


-- SUPPLIER
INSERT INTO SUPPLIER (Name, ContactInfo)
VALUES
('Bharat Electronics Ltd.', 'contact@belindia.com'),
('Tata Advanced Systems', 'support@tataas.com'),
('Havells India Ltd.', 'info@havells.com'),
('Godrej Consumer Products', 'care@godrej.com'),
('Samsung India Electronics', 'service@samsungindia.com');

-- PRODUCT
INSERT INTO PRODUCT (Name, Description, SupplierID)
VALUES
('Smartphone Z1', '5G-enabled smartphone with AI camera', 5),
('LED TV 55"', '55-inch 4K Ultra HD Smart TV', 3),
('Refrigerator DX200', 'Double-door frost-free refrigerator', 4),
('Laptop Elite 15', 'High-performance laptop for professionals', 2),
('Air Conditioner Pro', '1.5 Ton Inverter AC with WiFi control', 1);

-- WAREHOUSE
INSERT INTO WAREHOUSE (Location, Capacity)
VALUES
('Delhi', 5000),
('Mumbai', 4500),
('Bangalore', 4000),
('Chennai', 3500),
('Hyderabad', 3000);

-- SHIPMENT
INSERT INTO SHIPMENT (ShipmentDate, WarehouseID)
VALUES
('2024-03-10', 1),
('2024-03-15', 2),
('2024-03-20', 3),
('2024-04-01', 4),
('2024-04-05', 5);

-- ORDERS 
INSERT INTO ORDERS (OrderDate, CustomerID, ShipmentID)
VALUES
('2024-03-11', 1, 1),
('2024-03-16', 2, 2),
('2024-03-21', 3, 3),
('2024-04-02', 4, 4),
('2024-04-06', 5, 5),
('2024-04-08', 1, 1), 
('2024-04-10', 2, 2); 

-- ORDER_PRODUCT 
INSERT INTO ORDER_PRODUCT (OrderID, ProductID, QuantityOrdered)
VALUES
(1, 1, 2),
(1, 2, 1),
(2, 3, 3),
(3, 4, 2),
(4, 5, 5),
(5, 1, 3),
(6, 2, 2),
(6, 3, 1),
(7, 4, 4),
(7, 5, 2);

-- WAREHOUSE_INVENTORY
INSERT INTO WAREHOUSE_INVENTORY (WarehouseID, ProductID, Quantity)
VALUES
  (1, 1, 50),   
  (1, 2, 30),   
  (2, 3, 20),   
  (3, 4, 15),   
  (4, 5, 25),   
  (5, 1, 10),   
  (2, 2, 40); 

-- INVENTORY_MOVEMENT
INSERT INTO INVENTORY_MOVEMENT (ProductID, WarehouseFromID, WarehouseToID, OrderID, ShipmentID, QuantityMoved, MovementDate, MovementType)
VALUES
  (1, 1, 2, 1, 1, 5, '2024-03-11', 'Transfer'), 
  (2, 1, 3, 1, 1, 3, '2024-03-11', 'Sale'),      
  (3, 2, 2, 2, 2, 7, '2024-03-16', 'Sale'),      
  (4, 3, 4, 3, 3, 4, '2024-03-21', 'Transfer'),  
  (5, 4, 5, 4, 4, 10, '2024-04-02', 'Restock'),  
  (1, 5, 1, 5, 5, 2, '2024-04-06', 'Transfer');  


-- Queries
-- 1. Listing All Customers
SELECT * FROM CUSTOMER;

-- 2. Listing Products with Their Supplier Names
SELECT 
    p.ProductID, 
    p.Name AS ProductName, 
    p.Description, 
    s.Name AS SupplierName
FROM PRODUCT p
JOIN SUPPLIER s ON p.SupplierID = s.SupplierID;

-- 3. Listing Orders with Customer and Shipment Details
SELECT 
    o.OrderID, 
    o.OrderDate, 
    c.Name AS CustomerName, 
    sh.ShipmentDate
FROM ORDERS o
JOIN CUSTOMER c ON o.CustomerID = c.CustomerID
JOIN SHIPMENT sh ON o.ShipmentID = sh.ShipmentID;

-- 4. Listing Order Details: Products and Quantities
SELECT 
    op.OrderID, 
    p.Name AS ProductName, 
    op.QuantityOrdered
FROM ORDER_PRODUCT op
JOIN PRODUCT p ON op.ProductID = p.ProductID;

-- 5. Counting the Number of Orders per Customer
SELECT 
    c.CustomerID, 
    c.Name AS CustomerName, 
    COUNT(o.OrderID) AS TotalOrders
FROM CUSTOMER c
JOIN ORDERS o ON c.CustomerID = o.CustomerID
GROUP BY c.CustomerID, c.Name;

-- 6. Total Quantity Ordered for Each Product
SELECT 
    p.ProductID, 
    p.Name AS ProductName, 
    SUM(op.QuantityOrdered) AS TotalQuantityOrdered
FROM PRODUCT p
JOIN ORDER_PRODUCT op ON p.ProductID = op.ProductID
GROUP BY p.ProductID, p.Name;

-- 7. Inventory Summary by Warehouse and Product
SELECT 
    w.WarehouseID, 
    w.Location, 
    p.ProductID, 
    p.Name AS ProductName, 
    wi.Quantity
FROM WAREHOUSE_INVENTORY wi
JOIN WAREHOUSE w ON wi.WarehouseID = w.WarehouseID
JOIN PRODUCT p ON wi.ProductID = p.ProductID;

-- 8. Total Shipments per Warehouse
SELECT 
    w.WarehouseID, 
    w.Location, 
    COUNT(sh.ShipmentID) AS ShipmentCount
FROM WAREHOUSE w
JOIN SHIPMENT sh ON w.WarehouseID = sh.WarehouseID
GROUP BY w.WarehouseID, w.Location;

-- 9. Inventory Movement details with Customer and Product Information
SELECT 
    im.MovementID, 
    im.MovementDate, 
    im.MovementType, 
    p.Name AS ProductName, 
    c.Name AS CustomerName, 
    im.QuantityMoved
FROM INVENTORY_MOVEMENT im
JOIN PRODUCT p ON im.ProductID = p.ProductID
JOIN ORDERS o ON im.OrderID = o.OrderID
JOIN CUSTOMER c ON o.CustomerID = c.CustomerID;

-- 10. Total Quantity Moved per Movement Type
SELECT 
    im.MovementType, 
    SUM(im.QuantityMoved) AS TotalQuantityMoved
FROM INVENTORY_MOVEMENT im
GROUP BY im.MovementType;




-- Insert sample warehouses
INSERT INTO WAREHOUSE (Location, Capacity) VALUES
('New York', 1000),
('Los Angeles', 800),
('Chicago', 1200);

-- Insert sample users
INSERT INTO USERS (Username, PasswordHash, Role) VALUES
('admin1', 'hash_admin1', 'Admin'),
('admin2', 'hash_admin2', 'Admin'),
('manager1', 'hash_manager1', 'Manager'),
('manager2', 'hash_manager2', 'Manager'),
('manager3', 'hash_manager3', 'Manager');


-- Assuming auto-increment starts at 1 and above insertions are done in order,
-- UserIDs: 1-5, WarehouseIDs: 1-3

-- Map managers to warehouses
INSERT INTO USER_WAREHOUSE (UserID, WarehouseID) VALUES
(3, 1),
(3, 2),
(4, 2),
(5, 1),
(5, 3);
DELIMITER //

-- Before INSERT trigger
CREATE TRIGGER check_warehouse_capacity_before_insert
BEFORE INSERT ON WAREHOUSE_INVENTORY
FOR EACH ROW
BEGIN
    DECLARE total_current INT;
    DECLARE capacity_limit INT;

    SELECT IFNULL(SUM(Quantity), 0) INTO total_current
    FROM WAREHOUSE_INVENTORY
    WHERE WarehouseID = NEW.WarehouseID;

    SELECT Capacity INTO capacity_limit
    FROM WAREHOUSE
    WHERE WarehouseID = NEW.WarehouseID;

    IF (total_current + NEW.Quantity) > capacity_limit THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cannot add inventory: warehouse capacity exceeded.';
    END IF;
END;
//
Delimiter ;





Delimiter //
-- Before UPDATE trigger
CREATE TRIGGER check_warehouse_capacity_before_update
BEFORE UPDATE ON WAREHOUSE_INVENTORY
FOR EACH ROW
BEGIN
    DECLARE total_other INT;
    DECLARE capacity_limit INT;

    SELECT IFNULL(SUM(Quantity), 0) INTO total_other
    FROM WAREHOUSE_INVENTORY
    WHERE WarehouseID = NEW.WarehouseID AND ProductID != OLD.ProductID;

    SELECT Capacity INTO capacity_limit
    FROM WAREHOUSE
    WHERE WarehouseID = NEW.WarehouseID;

    IF (total_other + NEW.Quantity) > capacity_limit THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cannot update inventory: warehouse capacity exceeded.';
    END IF;
END;
//

DELIMITER ;