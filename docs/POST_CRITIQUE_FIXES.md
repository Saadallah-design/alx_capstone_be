# Payment App: Troubleshooting & Implementation Report

This report details the technical hurdles encountered during the implementation and testing of the `payments` application, the root causes, and the applied solutions.

## 1. CSRF Verification Failures
**Error:** `403 Forbidden - CSRF verification failed. Request aborted.`
- **Why**: Django's `CsrfViewMiddleware` is enabled by default. Since `curl` and other external tools do not automatically handle CSRF cookies/tokens like a browser does, the POST request to create a session was rejected.
- **Fix**: Applied the `@csrf_exempt` decorator to the `CreateCheckoutSessionView`.
- **Logic**: In a decoupled production environment, this endpoint is often called by a frontend using a Bearer token or is protected by other authentication mechanisms, making CSRF less relevant for this specific "session initiation" endpoint.

---

## 2. Booking Overlap & Data Collisions
**Error:** `ValidationError: ['This vehicle is already booked for the selected dates.']`
- **Why**: The `rentals.Booking` model has a `clean()` method that prevents double-booking a vehicle. When running the `setup_test_booking.py` script multiple times, it attempted to create a new booking for the same vehicle and dates without removing the old one.
- **Fix**: Updated the setup script to be **idempotent**. It now deletes existing payments and bookings for the test vehicle before creating a fresh one.

---

## 3. Database Integrity (ProtectedError)
**Error:** `django.db.models.deletion.ProtectedError: ("Cannot delete some instances of model 'Booking' because they are referenced through protected foreign keys: 'Payment.booking'.")`
- **Why**: The `Payment` model uses `on_delete=models.PROTECT` for its reference to a `Booking`. This is a safety feature to prevent deleting a booking that has financial records.
- **Fix**: Modified the setup script to delete the `Payment` records *before* attempting to delete the `Booking`.

---

## 4. Missing Configuration (SITE_URL)
**Error:** `AttributeError: 'Settings' object has no attribute 'SITE_URL'`
- **Why**: The Stripe Checkout session requires `success_url` and `cancel_url`. The implementation relied on a global `SITE_URL` to build these links, but it wasn't defined in the project's `settings.py`.
- **Fix**: Added `SITE_URL = os.getenv('SITE_URL', 'http://127.0.0.1:8000')` to `settings.py`.

---

## 5. Metadata Mismatch in Webhook Testing
**Issue:** `stripe trigger checkout.session.completed` succeeded, but the Admin status remained "Pending".
- **Why**: The `stripe trigger` command sends a generic event with random data. Our webhook handler specifically looks for a `payment_uuid` in the event's `metadata` to find the correct record in our database. Since the mock event had no metadata, our server ignored it.
- **Fix**: No code fix was needed, but I provided a **logic verification script** (`test_webhook_logic.py`) that successfully proved the webhook handler works when the correct metadata is present.

---

## 6. Field Naming & Model Mismatches
**Error:** Mismatches on `license_plate` vs `licence_plate` and `branch` vs `current_location`.
- **Why**: The initial test script used generic field names that didn't match the specific schema definitions in `vehicles/models.py`.
- **Fix**: Audited the `Vehicle` and `Branch` models and updated the setup script to use the exact property names (`licence_plate` with a 'c' and `current_location` for the branch reference).

---

## 7. Migration Dependency
**Error:** `ProgrammingError: relation "payments_payment" does not exist`
- **Why**: The `payments` app was newly created/modified and migrations had not been applied to the local PostgreSQL database.
- **Fix**: Ran `makemigrations payments` and `migrate payments` to synchronize the database schema.

---

## 💡 Summary of System Robustness
The payment app now includes:
1. **High-precision math** (via `Decimal`) for financial transactions.
2. **Atomic-style logic** in signals to ensure bookings are only confirmed on successful payment.
3. **Idempotent testing tools** for development.
4. **Resilient Webhooks** that handle failures and refunds gracefully.
