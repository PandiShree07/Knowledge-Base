-- Run this in MySQL as an administrator.
-- This creates a SEPARATE demo database and dedicated accounts; it does not touch your existing database.
CREATE DATABASE IF NOT EXISTS uka_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'uka_demo_reader'@'localhost' IDENTIFIED BY 'change_me_reader_password';
CREATE USER IF NOT EXISTS 'uka_demo_reader'@'127.0.0.1' IDENTIFIED BY 'change_me_reader_password';
GRANT SELECT, SHOW VIEW ON uka_demo.* TO 'uka_demo_reader'@'localhost';
GRANT SELECT, SHOW VIEW ON uka_demo.* TO 'uka_demo_reader'@'127.0.0.1';

CREATE USER IF NOT EXISTS 'uka_demo_seed'@'localhost' IDENTIFIED BY 'change_me_seed_password';
CREATE USER IF NOT EXISTS 'uka_demo_seed'@'127.0.0.1' IDENTIFIED BY 'change_me_seed_password';
GRANT SELECT, INSERT, CREATE, ALTER, INDEX ON uka_demo.* TO 'uka_demo_seed'@'localhost';
GRANT SELECT, INSERT, CREATE, ALTER, INDEX ON uka_demo.* TO 'uka_demo_seed'@'127.0.0.1';
FLUSH PRIVILEGES;

-- If you change passwords here, update the matching values in .env.
