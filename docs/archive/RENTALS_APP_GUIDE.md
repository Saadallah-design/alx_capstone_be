# Rentals App - Implementation Guide

## What This App Does
Manages the complete booking lifecycle for vehicle rentals, from reservation to completion.

## Already Implemented ✅
The `Booking` model in `rentals/models.py` has:
- **Robust validation** (date checks, overlap prevention)
- **Auto cost calculation** with grace period logic
- **Database constraints** (PostgreSQL exclusion for overlaps)
- **Agency integrity** checks

## What We're Building

### 1. Serializers
- **`Booking ListSerializer`**: Lightweight for dashboards
- **`BookingDetailSerializer`**: Full info with nested data
- **`BookingCreateSerializer`**: Handles creation + validation

### 2. Views
- **`BookingListCreateView`**: Customers book & view their rentals
- **`BookingDetailView`**: View details, cancel bookings
- **`AgencyBookingListView`**: Agency dashboard (optional)

### 3. Permissions
- **`IsBookingParticipant`**: Customer OR agency can access booking

### 4. Business Rules
- Cost locked at booking time (won't change if rates update)
- Customers can only cancel, not modify dates/vehicle
- No hard deletes (soft delete via `CANCELLED` status)
- Overlaps prevented at both API and database level

## API Endpoints (Planned)
```
GET/POST  /api/bookings/           # List my bookings / Create new
GET/PATCH /api/bookings/{id}/      # View detail / Cancel
GET       /api/bookings/agency/    # Agency dashboard (optional)
```

## Key Validation Logic
1. Start date cannot be in the past
2. End date must be after start date
3. No bookings > 365 days in advance
4. Vehicle must be available (no overlaps)
5. Booking agency must match vehicle owner

## Files to Create
1. `rentals/serializers.py`
2. `rentals/permissions.py`
3. `rentals/views.py`
4. `rentals/urls.py`
5. `test_rentals.py`

For detailed implementation guide, see `implementation_plan.md`.
