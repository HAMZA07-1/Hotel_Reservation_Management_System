-- This script inserts the initial 151 rooms into the 'rooms' table.
-- The room_id column is omitted as it is configured to auto-increment.
-- The 'smoking' column is included. Non-smoking = 0, Smoking = 1.

INSERT INTO rooms (room_number, room_type, smoking, capacity, price, is_available) VALUES
-- 1st Floor (Non-Smoking Family Rooms near Pool)
('101', 'Two Queens + Pullout', 0, 6, 150.00, 1),
('102', 'Two Queens + Pullout', 0, 6, 150.00, 1),
('103', 'Two Queens + Pullout', 0, 6, 150.00, 1),
('104', 'Two Queens + Pullout', 0, 6, 150.00, 1),
('105', 'Two Queens + Pullout', 0, 6, 150.00, 1),
('106', 'Two Queens + Pullout', 0, 6, 150.00, 1),
('107', 'Two Queens + Pullout', 0, 6, 150.00, 1),
('108', 'Two Queens + Pullout', 0, 6, 150.00, 1),
('109', 'Two Queens + Pullout', 0, 6, 150.00, 1),
('110', 'Two Queens + Pullout', 0, 6, 150.00, 1),

-- 1st Floor Standard Rooms
('111', 'Two Queens', 0, 4, 120.00, 1),
('112', 'Two Queens', 0, 4, 120.00, 1),
('113', 'Two Queens', 0, 4, 120.00, 1),
('114', 'Two Queens', 0, 4, 120.00, 1),
('115', 'Two Queens', 0, 4, 120.00, 1),
('116', 'Two Queens', 0, 4, 120.00, 1),
('117', 'Two Queens', 0, 4, 120.00, 1),
('118', 'Two Queens', 0, 4, 120.00, 1),
('119', 'Two Queens', 0, 4, 120.00, 1),
('120', 'Two Queens', 0, 4, 120.00, 1),

-- 2nd Floor (Family Suites, slightly cheaper)
('201', 'Two Queens + Pullout', 0, 6, 130.00, 1),
('202', 'Two Queens + Pullout', 0, 6, 130.00, 1),
('203', 'Two Queens + Pullout', 0, 6, 130.00, 1),
('204', 'Two Queens + Pullout', 0, 6, 130.00, 1),
('205', 'Two Queens + Pullout', 0, 6, 130.00, 1),
('206', 'Two Queens + Pullout', 0, 6, 130.00, 1),
('207', 'Two Queens + Pullout', 0, 6, 130.00, 1),
('208', 'Two Queens + Pullout', 0, 6, 130.00, 1),
('209', 'Two Queens + Pullout', 0, 6, 130.00, 1),
('210', 'Two Queens + Pullout', 0, 6, 130.00, 1),

-- 2nd Floor Smoking Section (Budget)
('211', 'Two Queens', 1, 4, 100.00, 1),
('212', 'Two Queens', 1, 4, 100.00, 1),
('213', 'Two Queens', 1, 4, 100.00, 1),
('214', 'Two Queens', 1, 4, 100.00, 1),
('215', 'Two Queens', 1, 4, 100.00, 1),
('216', 'Two Queens', 1, 4, 100.00, 1),
('217', 'Two Queens', 1, 4, 100.00, 1),
('218', 'Two Queens', 1, 4, 100.00, 1),
('219', 'Two Queens', 1, 4, 100.00, 1),
('220', 'Two Queens', 1, 4, 100.00, 1),

-- Executive King Suites
('301', 'King Suite', 0, 2, 250.00, 1),
('302', 'King Suite', 0, 2, 250.00, 1),
('303', 'King Suite', 0, 2, 250.00, 1),
('304', 'King Suite', 0, 2, 250.00, 1),
('305', 'King Suite', 0, 2, 250.00, 1),
('306', 'King Suite', 0, 2, 250.00, 1),
('307', 'King Suite', 0, 2, 250.00, 1),
('308', 'King Suite', 0, 2, 250.00, 1),
('309', 'King Suite', 0, 2, 250.00, 1),
('310', 'King Suite', 0, 2, 250.00, 1),

-- Business Singles
('401', 'Single Business', 0, 1, 90.00, 1),
('402', 'Single Business', 0, 1, 90.00, 1),
('403', 'Single Business', 0, 1, 90.00, 1),
('404', 'Single Business', 0, 1, 90.00, 1),
('405', 'Single Business', 0, 1, 90.00, 1),
('406', 'Single Business', 0, 1, 90.00, 1),
('407', 'Single Business', 0, 1, 90.00, 1),
('408', 'Single Business', 0, 1, 90.00, 1),
('409', 'Single Business', 0, 1, 90.00, 1),
('410', 'Single Business', 0, 1, 90.00, 1);
