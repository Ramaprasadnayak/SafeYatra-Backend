-- Active: 1762100041554@@127.0.0.1@3306@maruthi_medical
CREATE DATABASE Maruthi_Medical;
USE Maruthi_Medical;
CREATE TABLE customers(
    usr_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(15) NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE medicines (
    med_id INT AUTO_INCREMENT PRIMARY KEY,
    medicine_name VARCHAR(255) NOT NULL,
    category VARCHAR(255) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    stock BOOLEAN NOT NULL DEFAULT TRUE,
    sales INT NOT NULL DEFAULT 0,
    image_url VARCHAR(255)
);
CREATE TABLE address(
    addressid INT AUTO_INCREMENT PRIMARY KEY,
    usr_id INT NOT NULL, 
    address VARCHAR(255),
    Foreign Key (usr_id) REFERENCES customers(usr_id) ON DELETE CASCADE
);
CREATE TABLE orders(
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    usr_id INT NOT NULL,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usr_id) REFERENCES customers(usr_id) ON DELETE CASCADE
);
CREATE TABLE order_items(
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    med_id INT NOT NULL,
    quantity INT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (med_id) REFERENCES medicines(med_id) ON DELETE CASCADE
);
CREATE TABLE cart (
    cart_id INT AUTO_INCREMENT PRIMARY KEY,
    usr_id INT NOT NULL,
    med_id INT NOT NULL,
    quantity INT DEFAULT 1,
    FOREIGN KEY (usr_id) REFERENCES customers(usr_id) ON DELETE CASCADE,
    FOREIGN KEY (med_id) REFERENCES medicines(med_id) ON DELETE CASCADE,
    UNIQUE (usr_id, med_id)
);
SELECT * FROM customers;
SELECT * FROM address;
SELECT * FROM medicines;
SELECT * FROM cart;
SELECT * FROM order_items;
SELECT * FROM orders;