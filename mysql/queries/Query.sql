-- Query.sql
-- University Library Project
-- Team: Daniel P, Dylan P, Thomas P, Gentry R, Chris R (Group 10)
-- MySQL 8.x

USE university_library;

-- ============================================================
-- Query 1
-- Current checked-out items
-- Business purpose:
-- Staff can see which item copies are currently borrowed,
-- who borrowed them, and when they are due.
-- ============================================================

SELECT
    c.checkout_id,
    p.patron_id,
    p.patron_type,
    p.email,
    it.title,
    ic.copy_id,
    l.name AS library_name,
    c.checkout_date,
    c.due_date
FROM CHECKOUT c
JOIN PATRON p ON c.patron_id = p.patron_id
JOIN ITEM_COPY ic ON c.copy_id = ic.copy_id
JOIN ITEM_TITLE it ON ic.item_id = it.item_id
JOIN LIBRARY l ON ic.library_id = l.library_id
WHERE c.return_date IS NULL
ORDER BY c.due_date ASC;


-- ============================================================
-- Query 2
-- Overdue checked-out items
-- Business purpose:
-- Staff can identify patrons with overdue materials.
-- ============================================================

SELECT
    c.checkout_id,
    p.patron_id,
    p.patron_type,
    p.email,
    it.title,
    c.checkout_date,
    c.due_date,
    DATEDIFF(CURRENT_DATE, c.due_date) AS days_overdue
FROM CHECKOUT c
JOIN PATRON p ON c.patron_id = p.patron_id
JOIN ITEM_COPY ic ON c.copy_id = ic.copy_id
JOIN ITEM_TITLE it ON ic.item_id = it.item_id
WHERE c.return_date IS NULL
  AND c.due_date < CURRENT_DATE
ORDER BY days_overdue DESC;


-- ============================================================
-- Query 3
-- Available inventory by library
-- Business purpose:
-- Shows how many available item copies each library currently has.
-- ============================================================

SELECT
    l.library_id,
    l.name AS library_name,
    loc.name AS location_name,
    COUNT(ic.copy_id) AS available_copies
FROM LIBRARY l
JOIN LOCATION loc ON l.location_id = loc.location_id
LEFT JOIN ITEM_COPY ic
    ON l.library_id = ic.library_id
    AND ic.status = 'Available'
GROUP BY l.library_id, l.name, loc.name
ORDER BY available_copies DESC;


-- ============================================================
-- Query 4
-- Search for available items by title keyword
-- Business purpose:
-- Patrons or staff can search for available library items.
-- ============================================================

SELECT
    it.item_id,
    it.title,
    it.media_type,
    it.loc_classification,
    ic.copy_id,
    l.name AS library_name,
    ic.status
FROM ITEM_TITLE it
JOIN ITEM_COPY ic ON it.item_id = ic.item_id
JOIN LIBRARY l ON ic.library_id = l.library_id
WHERE LOWER(it.title) LIKE '%database%'
  AND ic.status = 'Available'
ORDER BY it.title, l.name;


-- ============================================================
-- Query 5
-- Most frequently checked-out item titles
-- Business purpose:
-- Helps the library identify popular items.
-- ============================================================

SELECT
    it.item_id,
    it.title,
    it.media_type,
    COUNT(c.checkout_id) AS times_checked_out
FROM CHECKOUT c
JOIN ITEM_COPY ic ON c.copy_id = ic.copy_id
JOIN ITEM_TITLE it ON ic.item_id = it.item_id
GROUP BY it.item_id, it.title, it.media_type
ORDER BY times_checked_out DESC;


-- ============================================================
-- Query 6
-- Patrons with multiple active checkouts
-- Business purpose:
-- Helps staff monitor patrons currently borrowing multiple items.
-- ============================================================

SELECT
    p.patron_id,
    p.patron_type,
    p.email,
    COUNT(c.checkout_id) AS active_checkouts
FROM PATRON p
JOIN CHECKOUT c ON p.patron_id = c.patron_id
WHERE c.return_date IS NULL
GROUP BY p.patron_id, p.patron_type, p.email
HAVING COUNT(c.checkout_id) > 1
ORDER BY active_checkouts DESC;


-- ============================================================
-- Query 7
-- Active holds by item title
-- Business purpose:
-- Shows which patrons are waiting for items and in what order.
-- ============================================================

SELECT
    h.hold_id,
    it.title,
    p.patron_id,
    p.patron_type,
    p.email,
    h.hold_date,
    h.hold_status
FROM HOLD h
JOIN PATRON p ON h.patron_id = p.patron_id
JOIN ITEM_TITLE it ON h.item_id = it.item_id
WHERE h.hold_status = 'Active'
ORDER BY it.title, h.hold_date ASC;


-- ============================================================
-- Query 8
-- Unpaid fines by patron
-- Business purpose:
-- Staff can see which patrons owe money and how much.
-- ============================================================

SELECT
    p.patron_id,
    p.patron_type,
    p.email,
    COUNT(f.fine_id) AS unpaid_fine_count,
    SUM(f.amount) AS total_unpaid_fines
FROM FINE f
JOIN PATRON p ON f.patron_id = p.patron_id
WHERE f.paid_status = FALSE
GROUP BY p.patron_id, p.patron_type, p.email
ORDER BY total_unpaid_fines DESC;


-- ============================================================
-- Query 9
-- Inter-library loan activity
-- Business purpose:
-- Tracks item transfers between university library locations.
-- ============================================================

SELECT
    ill.loan_id,
    it.title,
    ic.copy_id,
    source.name AS source_library,
    destination.name AS destination_library,
    ill.start_date,
    ill.end_date,
    ill.loan_status
FROM INTER_LIBRARY_LOAN ill
JOIN ITEM_COPY ic ON ill.copy_id = ic.copy_id
JOIN ITEM_TITLE it ON ic.item_id = it.item_id
JOIN LIBRARY source ON ill.source_library_id = source.library_id
JOIN LIBRARY destination ON ill.destination_library_id = destination.library_id
ORDER BY ill.start_date DESC;


-- ============================================================
-- Query 10
-- Room reservation schedule
-- Business purpose:
-- Staff can review room reservations by library and patron.
-- ============================================================

SELECT
    rr.reservation_id,
    r.room_name,
    r.capacity,
    l.name AS library_name,
    p.patron_id,
    p.patron_type,
    p.email,
    rr.start_time,
    rr.end_time,
    rr.reservation_status
FROM ROOM_RESERVATION rr
JOIN ROOM r ON rr.room_id = r.room_id
JOIN LIBRARY l ON r.library_id = l.library_id
JOIN PATRON p ON rr.patron_id = p.patron_id
ORDER BY rr.start_time;