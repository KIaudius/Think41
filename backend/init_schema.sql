-- Use the database
USE ecommerce_ai;

-- Drop if exists
DROP TABLE IF EXISTS OrderItem, OrderTable, InventoryItem, Product, DistributionCenter, UserTable;

-- User Table
CREATE TABLE UserTable (
    id INT PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(200),
    age INT,
    gender CHAR(1),
    state VARCHAR(100),
    city VARCHAR(100),
    country VARCHAR(100),
    traffic_source VARCHAR(100),
    created_at DATETIME
);

-- Distribution Centers
CREATE TABLE DistributionCenter (
    id INT PRIMARY KEY,
    name VARCHAR(200),
    latitude FLOAT,
    longitude FLOAT
);

-- Products
CREATE TABLE Product (
    id INT PRIMARY KEY,
    name VARCHAR(255),
    brand VARCHAR(100),
    category VARCHAR(100),
    department VARCHAR(50),
    sku VARCHAR(100),
    cost FLOAT,
    retail_price FLOAT,
    distribution_center_id INT,
    FOREIGN KEY (distribution_center_id) REFERENCES DistributionCenter(id)
);

-- Inventory Items
CREATE TABLE InventoryItem (
    id INT PRIMARY KEY,
    product_id INT,
    created_at DATETIME,
    sold_at DATETIME,
    cost FLOAT,
    product_category VARCHAR(100),
    product_name VARCHAR(255),
    product_brand VARCHAR(100),
    product_retail_price FLOAT,
    product_department VARCHAR(100),
    product_sku VARCHAR(100),
    product_distribution_center_id INT,
    FOREIGN KEY (product_id) REFERENCES Product(id)
);

-- Orders
CREATE TABLE OrderTable (
    order_id INT PRIMARY KEY,
    user_id INT,
    status VARCHAR(50),
    gender CHAR(1),
    created_at DATETIME,
    returned_at DATETIME,
    shipped_at DATETIME,
    delivered_at DATETIME,
    num_of_item INT,
    FOREIGN KEY (user_id) REFERENCES UserTable(id)
);

-- Order Items
CREATE TABLE OrderItem (
    id INT PRIMARY KEY,
    order_id INT,
    user_id INT,
    product_id INT,
    inventory_item_id INT,
    status VARCHAR(50),
    created_at DATETIME,
    shipped_at DATETIME,
    delivered_at DATETIME,
    returned_at DATETIME,
    sale_price FLOAT,
    FOREIGN KEY (order_id) REFERENCES OrderTable(order_id),
    FOREIGN KEY (user_id) REFERENCES UserTable(id),
    FOREIGN KEY (product_id) REFERENCES Product(id)
);
