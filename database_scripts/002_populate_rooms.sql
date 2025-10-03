
-- This scrip inserts the initial 15 rooms into 'rooms' table for the MVP.
-- The room_id column is omitted as it is configured to auto-increment.

INSERT INTO rooms (room_number, room_type, capacity, price, is_available)
VALUES
('101', 'Standard Queen', 2, 150.00, 1),
('102', 'Standard Queen', 2, 150.00, 0),
('201', 'Deluxe Double', 4, 180.50, 1),
('202', 'Deluxe Double', 4, 180.50, 1),
('301', 'King Suite', 3, 250.75, 0),
('302', 'King Suite', 3, 250.75, 1),
('401', 'Standard Queen', 2, 150.00, 1),
('402', 'Deluxe Double', 4, 180.50, 1),
('403', 'King Suite', 3, 250.75, 0),
('501', 'Standard Queen', 2, 150.00, 1),
('502', 'Deluxe Double', 4, 180.50, 0),
('503', 'King Suite', 3, 250.75, 1),
('504', 'Standard Queen', 2, 150.00, 1),
('505', 'Deluxe Double', 4, 180.50, 0),
('506', 'King Suite', 3, 250.75, 1);