-- Active: 1762100041554@@127.0.0.1@3306@maruthi_medical
DROP DATABASE Maruthi_medical;
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
    image_url VARCHAR(255)
);

CREATE TABLE address(
    addressid INT AUTO_INCREMENT PRIMARY KEY,
    usr_id INT NOT NULL, 
    address VARCHAR(255) NOT NULL DEFAULT "No address saved yet.",
    Foreign Key (usr_id) REFERENCES customers(usr_id)
);

ALTER TABLE customers DROP COLUMN address;
ALTER TABLE medicines
ADD COLUMN sales INT NOT NULL DEFAULT 0;
CREATE TABLE orders(
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    usr_id INT NOT NULL,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (usr_id)
    REFERENCES customers(usr_id)
);
CREATE TABLE order_items(
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,

    order_id INT NOT NULL,
    med_id INT NOT NULL,

    quantity INT NOT NULL,

    FOREIGN KEY (order_id)
    REFERENCES orders(order_id),

    FOREIGN KEY (med_id)
    REFERENCES medicines(med_id)
);

CREATE TABLE cart (
    cart_id INT AUTO_INCREMENT PRIMARY KEY,
    usr_id INT NOT NULL,
    med_id INT NOT NULL,
    quantity INT DEFAULT 1,
    FOREIGN KEY (usr_id) REFERENCES customers(usr_id),
    FOREIGN KEY (med_id) REFERENCES medicines(med_id),
    UNIQUE (usr_id, med_id)
);
SELECT * FROM customers;
SELECT * FROM address;
SELECT * FROM medicines;

SELECT * FROM cart;


INSERT INTO customers(username,password,phone)
VALUES("ramprasad","Ramprasad@18","8277615951");
INSERT INTO cart(usr_id,med_id,quantity)
VALUES(3,10,2);

SELECT * FROM cart WHERE usr_id=3;

INSERT INTO medicines(medicine_name,price,stock,image_url)
VALUES("Dolo650",32,True,"C:\Users\Ramaprasad\Downloads\Untitled Folder\dolo650.avif");

UPDATE customers SET address="No address saved yet.";


UPDATE medicines SET image_url="https://res.cloudinary.com/ubt9l5i7/image/upload/v1783698900/comingsoon_dqtsr7.png"
WHERE med_id>100;

ALTER TABLE customers
ADD COLUMN address VARCHAR(255) NOT NULL DEFAULT '';


SELECT
    m.medicine_name,
    m.category,
    m.price,
    m.stock,
    m.image_url,
    c.quantity
FROM cart c
JOIN medicines m
    ON c.med_id = m.med_id
WHERE c.usr_id = 3;


SELECT c.usr_id,c.username,a.address 
FROM customers c
JOIN address a
ON c.usr_id=3

INSERT INTO address(usr_id,address)
VALUES(4,"Devi ganesh main road kaup");

SELECT * FROM address



DELIMITER //

CREATE TRIGGER after_customer_insert
AFTER INSERT ON customers
FOR EACH ROW
BEGIN
    INSERT INTO address (usr_id)
    VALUES (NEW.usr_id);
END //

DELIMITER ;