CREATE DATABASE bankdb;
USE bankdb;

CREATE TABLE users (
	fName VARCHAR(20) NOT NULL,
    lName VARCHAR(20) NOT NULL,
    SSN INT NOT NULL PRIMARY KEY,
    Address VARCHAR(20) NOT NULL,
    phoneNum VARCHAR(20) NOT NULL,
    pw VARCHAR(20) NOT NULL
);
SELECT * FROM users;
INSERT INTO users (fName, lName, SSN, Address, phoneNum, pw)
VALUES ('Admin', 'Account', '1', '123 Admin Street', 'adminNum', 'admin123');
ALTER TABLE users MODIFY COLUMN SSN VARCHAR(20);
ALTER TABLE users ADD balance INT;
ALTER TABLE users ADD accNUm INT;
ALTER TABLE users RENAME COLUMN accNUm TO accNum;

ALTER TABLE users ADD COLUMN status VARCHAR(10) NOT NULL DEFAULT 'pending';
ALTER TABLE users ADD COLUMN isAdmin TINYINT(1) NOT NULL DEFAULT 0;
UPDATE users SET status = 'approved', isAdmin = 1 WHERE SSN = 'your_admin_SSN';
SET SQL_SAFE_UPDATES = 0;
UPDATE users SET status = 'approved' WHERE SSN = '1';
ALTER TABLE users MODIFY COLUMN accNum VARCHAR(20);
