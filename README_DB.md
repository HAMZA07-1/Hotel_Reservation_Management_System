## Database overview

This document describes the database schema used by the Hotel Reservation Management System, explains relationships between tables, outlines integrity enforcement mechanisms, and lists practical future extension ideas (tax handling, room categories, pricing, etc.). The project currently uses SQLite for local development; the notes below attempt to be compatible with production databases (Postgres, MySQL) where relevant.

## Purpose of each table and relationships

- `rooms`
  - Purpose: store inventory of hotel rooms and per-room properties used for availability and pricing.
  - Important columns:
    - `room_id` (PK) — integer primary key.
    - `room_number` — human-facing identifier (string/text). Consider enforcing `UNIQUE` if room numbers are unique across the property.
    - `room_type` — e.g., 'Single', 'Double', 'Suite'. Useful for grouping and search.
    - `capacity` — maximum number of guests.
    - `price` — default price per night (decimal/real).
    - `is_available` — simple flag (0/1) to mark rooms unavailable for general booking (maintenance, offline, etc.).

- `guests`
  - Purpose: store guest/contact information. Linked from reservations.
  - Important columns:
    - `guest_id` (PK) — integer primary key.
    - `first_name`, `last_name` — textual names.
    - `email` — contact email. Consider `UNIQUE` to avoid duplicate guest accounts.
    - `phone`, `address` — optional contact details.

- `reservations`
  - Purpose: store individual bookings linking a guest and a room to a date range and status.
  - Important columns:
    - `reservation_id` (PK)
    - `guest_id` (FK -> `guests.guest_id`) — the booking party.
    - `room_id` (FK -> `rooms.room_id`) — reserved room.
    - `check_in_date`, `check_out_date` — date strings in ISO format `YYYY-MM-DD`.
    - `total_price` — numeric amount for the reservation (taxes/discounts included if computed here).
    - `status` — booking lifecycle (e.g. `Confirmed`, `Cancelled`, `Checked-in`, `Checked-out`, `No-show`).

Relationship Summary:
- reservations reference guests and rooms; a guest can have multiple resrvations and one room can have multiple reservations throughout time.

## Integrity Enforcement
- The following is to ensure data consistency and prevent invalid booking states

### Primary constraints
- `rooms.rooms_id`, `guests.guest_id`, and `reservations.reservation_id` are unique therefore no duplicate records can exist.

### Foreign Constraints
- `reservations.guest_id` -> `guests.guest_id`: Reservation must reference an existing guest.
- `reservations.guest_id` -> `rooms.rooms_id` : Every reservation must reference an existing room

### Unique Constraints
- `rooms.room_number` : Should be unique to each reservation. No overlapping reservations of the same room
- `guests.email` : Recommended to prevent duplicate guest accounts.

### Check Constraints (domain validation)
- `reservations.check_in_date < reservations.check_out_date`: check-in must be before check-out to prevent same day or inverted ranges.
- `reservations.total_price >= 0`: prices should not be negative.
- `rooms.price >= 0`: room base prices should be non-negative.
- `rooms.capacity > 0`: room capacity must be positive (at least 1 guest).
- `rooms.is_available IN (0, 1)`: simple boolean flag (0 = unavailable, 1 = available).

## Integrity Enforcment
*insert Integrity Enforcement detailing here*

## Availability and Occupied-statuses decisions
- `is_available` indicates whether the room is bookable (maintenance/out-of-service - 0 means not bookable)

- `statuses` in `reservations` indicates the reservations life cycle.
    - `confirmed` (booking is both active and exists)
    - `checked in` (guest has arrived)
    - `checked out` (reservation completed)
    - `cancelled` (reservation not active)
    - `No-show` (no show 0-0)

## Future extension considerations

### 1. Tax and Fee Handling
- **New table:** `taxes` (id, name, rate, description).
- **New table:** `fees` (id, name, amount, applied_to_reservation).
- **New column in `reservations`:** `tax_amount`, `fees_amount`, `subtotal` to break down pricing.
- **Purpose:** Support multiple tax jurisdictions and per-reservation surcharges (cleaning fee, resort fee, pet fee, etc.).
- **Implementation:** calculate and store tax/fee amounts at booking time; separate line-item reporting in invoices.

### 2. Guest Preferences and Loyalty
- **New table:** `guest_preferences` (id, guest_id, preferred_room_type, notes, dietary_restrictions).
- **New table:** `loyalty_programs` (id, guest_id, tier, points_balance, member_since).
- **Purpose:** personalize service and track repeat customer engagement.
- **Implementation:** auto-recommend preferred room types; discount bookings based on loyalty tier.

### 3. Housekeeping and Maintenance Workflow
- **New table:** `housekeeping_tasks` (id, room_id, task_type, status, assigned_to, due_date).
- **New table:** `maintenance_requests` (id, room_id, issue_description, priority, assigned_to, resolved_date).
- **Purpose:** track cleaning schedules and maintenance tasks.
- **Implementation:** mark rooms unavailable during housekeeping; alert staff of maintenance needs.