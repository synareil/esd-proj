-- Insert into Cart
INSERT INTO cart (cartID, userID, active) VALUES
(11, '0', TRUE),
(12, '1', TRUE),
(13, '2', TRUE);

-- Insert into CartItem
INSERT INTO cartItem (cartID, itemID, quantity) VALUES
(11, '1', 2),
(11, '2', 1),
(12, '2', 5),
(13, '1', 3),
(13, '3', 2);
