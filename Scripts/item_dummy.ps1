docker cp item.csv esd-proj-inventory-db-1:/var/lib/mysql-files/item.csv
Get-Content item_dummy.sql | docker exec -i esd-proj-inventory-db-1 mysql -uroot -ppassword proj_inventory
Get-Content cart_dummy.sql | docker exec -i esd-proj-cart-db-1 mysql -uroot -ppassword proj_cart 