-- Create the store database and tables
-- Initial

DELIMITER $$

CREATE TRIGGER decrease_quantity_after_order
AFTER INSERT ON orders FOR EACH ROW
BEGIN
 UPDATE items
   SET quantity = quantity - 1
   WHERE id = NEW.item_id;
END;
$$

DELIMITER ;
