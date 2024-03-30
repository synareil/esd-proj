LOAD DATA INFILE '/var/lib/mysql-files/item.csv'
INTO TABLE item
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
(name, description, qty, category, price, salesPrice, image);
