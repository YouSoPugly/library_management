-- proj2-makeSchema.sql
-- University Library Project
-- Team: Daniel P, Dylan P, Thomas P, Gentry R, Chris R (Group 10)
-- Creates the database and all tables for the library system.
-- MySQL 8.x

-- ============================================================
-- DATABASE SETUP
-- ============================================================
-- Drops and recreates the database to ensure a clean state.
-- Useful for development/testing so schema is always consistent.
-- ============================================================

DROP DATABASE IF EXISTS university_library;
CREATE DATABASE university_library;
USE university_library;

-- ============================================================
-- 1. UNIVERSITY / LOCATION / LIBRARY
-- ============================================================
-- Models the hierarchy:
-- University → Location → Library
--
-- A university can have multiple locations (campuses/suburbs),
-- and each location can contain multiple libraries.
-- ============================================================

CREATE TABLE UNIVERSITY (
    university_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(150) NOT NULL
);

CREATE TABLE LOCATION (
    location_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(150) NOT NULL,
    city VARCHAR(100) NOT NULL,
    suburb_or_campus VARCHAR(100),
    university_id INT NOT NULL, -- Each location belongs to a university

    CONSTRAINT fk_location_university
        FOREIGN KEY (university_id)
        REFERENCES UNIVERSITY(university_id)
        ON DELETE RESTRICT   -- Prevent deleting university if locations exist
        ON UPDATE CASCADE    -- Propagate updates to IDs
);

CREATE TABLE LIBRARY (
    library_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(150) NOT NULL,
    location_id INT NOT NULL, -- Library exists within a location

    CONSTRAINT fk_library_location
        FOREIGN KEY (location_id)
        REFERENCES LOCATION(location_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- ============================================================
-- 2. PATRONS, STUDENTS, FACULTY, STAFF
-- ============================================================
-- PATRON is a base entity for all people interacting with the system.
-- STUDENT and FACULTY extend PATRON using a one-to-one relationship.
-- STAFF is separate because staff are employees, not patrons.
-- ============================================================

CREATE TABLE PATRON (
    patron_id INT PRIMARY KEY AUTO_INCREMENT,
    patron_type ENUM('Student', 'Faculty') NOT NULL, -- Indicates subtype
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(20)
);

CREATE TABLE STUDENT (
    student_id INT PRIMARY KEY AUTO_INCREMENT,
    patron_id INT NOT NULL UNIQUE, -- One-to-one with PATRON
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    university_id INT NOT NULL, -- Student belongs to a university

    CONSTRAINT fk_student_patron
        FOREIGN KEY (patron_id)
        REFERENCES PATRON(patron_id)
        ON DELETE CASCADE -- Deleting patron deletes student
        ON UPDATE CASCADE,

    CONSTRAINT fk_student_university
        FOREIGN KEY (university_id)
        REFERENCES UNIVERSITY(university_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE FACULTY (
    faculty_id INT PRIMARY KEY AUTO_INCREMENT,
    patron_id INT NOT NULL UNIQUE, -- One-to-one with PATRON
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    department VARCHAR(100),
    university_id INT NOT NULL,

    CONSTRAINT fk_faculty_patron
        FOREIGN KEY (patron_id)
        REFERENCES PATRON(patron_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_faculty_university
        FOREIGN KEY (university_id)
        REFERENCES UNIVERSITY(university_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE STAFF (
    staff_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    library_id INT NOT NULL, -- Staff works at a specific library

    CONSTRAINT fk_staff_library
        FOREIGN KEY (library_id)
        REFERENCES LIBRARY(library_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- ============================================================
-- 3. ACCESS CONTROL
-- ============================================================
-- Implements Role-Based Access Control (RBAC):
-- - Roles define job responsibilities
-- - Permissions define allowed actions
-- - STAFF_ROLE assigns roles to staff
-- - ROLE_PERMISSION maps roles to permissions
-- ============================================================

CREATE TABLE ROLE (
    role_id INT PRIMARY KEY AUTO_INCREMENT,
    role_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE PERMISSION (
    permission_id INT PRIMARY KEY AUTO_INCREMENT,
    permission_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE ROLE_PERMISSION (
    role_id INT NOT NULL,
    permission_id INT NOT NULL,
    PRIMARY KEY (role_id, permission_id),

    CONSTRAINT fk_role_permission_role
        FOREIGN KEY (role_id)
        REFERENCES ROLE(role_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_role_permission_permission
        FOREIGN KEY (permission_id)
        REFERENCES PERMISSION(permission_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE STAFF_ROLE (
    staff_id INT NOT NULL,
    role_id INT NOT NULL,
    PRIMARY KEY (staff_id, role_id),

    CONSTRAINT fk_staff_role_staff
        FOREIGN KEY (staff_id)
        REFERENCES STAFF(staff_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_staff_role_role
        FOREIGN KEY (role_id)
        REFERENCES ROLE(role_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- ============================================================
-- 4. LIBRARY ITEMS / AUTHORS
-- ============================================================
-- ITEM_TITLE represents the abstract item (book/media).
-- ITEM_COPY represents physical copies of that item.
-- This separation allows multiple copies per title.
-- ============================================================

CREATE TABLE ITEM_TITLE (
    item_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    media_type VARCHAR(50) NOT NULL, -- Book, DVD, etc.
    loc_classification VARCHAR(50),  -- Library classification system
    publication_date DATE,
    is_electronic BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE AUTHOR (
    author_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL
);

-- Many-to-many relationship between items and authors
CREATE TABLE ITEM_AUTHOR (
    item_id INT NOT NULL,
    author_id INT NOT NULL,
    PRIMARY KEY (item_id, author_id),

    CONSTRAINT fk_item_author_item
        FOREIGN KEY (item_id)
        REFERENCES ITEM_TITLE(item_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_item_author_author
        FOREIGN KEY (author_id)
        REFERENCES AUTHOR(author_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE ITEM_COPY (
    copy_id INT PRIMARY KEY AUTO_INCREMENT,
    item_id INT NOT NULL,
    library_id INT NOT NULL,
    status ENUM('Available', 'Checked Out', 'On hold', 'Damaged', 'Lost') NOT NULL,
    available_for_checkout BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT fk_item_copy_item
        FOREIGN KEY (item_id)
        REFERENCES ITEM_TITLE(item_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_item_copy_library
        FOREIGN KEY (library_id)
        REFERENCES LIBRARY(library_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- ============================================================
-- 5. CHECKOUTS / HOLDS / INTER-LIBRARY LOANS / FINES
-- ============================================================
-- These tables handle borrowing, reservations, transfers,
-- and penalties in the system.
-- ============================================================

CREATE TABLE CHECKOUT (
    checkout_id INT PRIMARY KEY AUTO_INCREMENT,
    patron_id INT NOT NULL,
    copy_id INT NOT NULL,
    checkout_date DATE NOT NULL,
    due_date DATE NOT NULL,
    return_date DATE,

    CONSTRAINT fk_checkout_patron
        FOREIGN KEY (patron_id)
        REFERENCES PATRON(patron_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_checkout_copy
        FOREIGN KEY (copy_id)
        REFERENCES ITEM_COPY(copy_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    -- Ensure logical date relationships
    CONSTRAINT chk_checkout_dates
        CHECK (due_date >= checkout_date),

    CONSTRAINT chk_return_date
        CHECK (return_date IS NULL OR return_date >= checkout_date)
);

CREATE TABLE HOLD (
    hold_id INT PRIMARY KEY AUTO_INCREMENT,
    patron_id INT NOT NULL,
    item_id INT NOT NULL,
    hold_date DATE NOT NULL,
    hold_status VARCHAR(50) NOT NULL,

    CONSTRAINT fk_hold_patron
        FOREIGN KEY (patron_id)
        REFERENCES PATRON(patron_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_hold_item
        FOREIGN KEY (item_id)
        REFERENCES ITEM_TITLE(item_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE INTER_LIBRARY_LOAN (
    loan_id INT PRIMARY KEY AUTO_INCREMENT,
    copy_id INT NOT NULL,
    source_library_id INT NOT NULL,
    destination_library_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    loan_status VARCHAR(50) NOT NULL,

    CONSTRAINT fk_ill_copy
        FOREIGN KEY (copy_id)
        REFERENCES ITEM_COPY(copy_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_ill_source_library
        FOREIGN KEY (source_library_id)
        REFERENCES LIBRARY(library_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_ill_destination_library
        FOREIGN KEY (destination_library_id)
        REFERENCES LIBRARY(library_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT chk_ill_dates
        CHECK (end_date IS NULL OR end_date >= start_date)
);

CREATE TABLE FINE (
    fine_id INT PRIMARY KEY AUTO_INCREMENT,
    patron_id INT NOT NULL,
    checkout_id INT NOT NULL,
    amount DECIMAL(8,2) NOT NULL,
    reason VARCHAR(255) NOT NULL,
    assessed_date DATE NOT NULL,
    paid_status BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT fk_fine_patron
        FOREIGN KEY (patron_id)
        REFERENCES PATRON(patron_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_fine_checkout
        FOREIGN KEY (checkout_id)
        REFERENCES CHECKOUT(checkout_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT chk_fine_amount
        CHECK (amount >= 0)
);

-- ============================================================
-- 6. ROOMS / RESERVATIONS
-- ============================================================
-- Allows patrons to reserve rooms in a library.
-- ============================================================

CREATE TABLE ROOM (
    room_id INT PRIMARY KEY AUTO_INCREMENT,
    library_id INT NOT NULL,
    room_name VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    capacity INT NOT NULL,

    CONSTRAINT fk_room_library
        FOREIGN KEY (library_id)
        REFERENCES LIBRARY(library_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT chk_room_capacity
        CHECK (capacity > 0)
);

CREATE TABLE ROOM_RESERVATION (
    reservation_id INT PRIMARY KEY AUTO_INCREMENT,
    room_id INT NOT NULL,
    patron_id INT NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    reservation_status VARCHAR(50) NOT NULL,

    CONSTRAINT fk_room_reservation_room
        FOREIGN KEY (room_id)
        REFERENCES ROOM(room_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_room_reservation_patron
        FOREIGN KEY (patron_id)
        REFERENCES PATRON(patron_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT chk_room_reservation_times
        CHECK (end_time > start_time)
);

-- ============================================================
-- 7. INDEXES
-- ============================================================
-- Improves performance for common lookup queries.
-- Especially important for joins and filtering.
-- ============================================================

CREATE INDEX idx_location_university_id ON LOCATION(university_id);
CREATE INDEX idx_library_location_id ON LIBRARY(location_id);

CREATE INDEX idx_student_university_id ON STUDENT(university_id);
CREATE INDEX idx_faculty_university_id ON FACULTY(university_id);
CREATE INDEX idx_staff_library_id ON STAFF(library_id);

CREATE INDEX idx_item_copy_item_id ON ITEM_COPY(item_id);
CREATE INDEX idx_item_copy_library_id ON ITEM_COPY(library_id);
CREATE INDEX idx_item_copy_status ON ITEM_COPY(status);

CREATE INDEX idx_checkout_patron_id ON CHECKOUT(patron_id);
CREATE INDEX idx_checkout_copy_id ON CHECKOUT(copy_id);
CREATE INDEX idx_checkout_due_date ON CHECKOUT(due_date);

CREATE INDEX idx_hold_patron_id ON HOLD(patron_id);
CREATE INDEX idx_hold_item_id ON HOLD(item_id);

CREATE INDEX idx_ill_copy_id ON INTER_LIBRARY_LOAN(copy_id);
CREATE INDEX idx_ill_source_library_id ON INTER_LIBRARY_LOAN(source_library_id);
CREATE INDEX idx_ill_destination_library_id ON INTER_LIBRARY_LOAN(destination_library_id);

CREATE INDEX idx_fine_patron_id ON FINE(patron_id);
CREATE INDEX idx_fine_checkout_id ON FINE(checkout_id);

CREATE INDEX idx_room_library_id ON ROOM(library_id);
CREATE INDEX idx_room_reservation_room_id ON ROOM_RESERVATION(room_id);
CREATE INDEX idx_room_reservation_patron_id ON ROOM_RESERVATION(patron_id);
CREATE INDEX idx_room_reservation_start_time ON ROOM_RESERVATION(start_time);