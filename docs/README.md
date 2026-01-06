# Payments Application

This application handles all financial transactions for the Car Rental platform, primarily integrating with **Stripe** to manage booking fees and security deposits.

## 🚀 Key Features

- **Split Payment Workflow**: Handles both immediate `RENTAL_FEE` captures and `SECURITY_DEPOSIT` holds (authorized-only).
- **Stripe Checkout Integration**: Uses Stripe's hosted checkout sessions for simplified PCI compliance.
- **Robust Webhooks**: Asynchronous status updates for successful payments, failures, and manual refunds.
- **Automated Booking Confirmation**: Integrated signals that automatically confirm a booking once the rental fee is marked as `COMPLETED`.

---

## 🛠 Recent Fixes & Improvements

Based on a technical audit, the following critical improvements were implemented:

### 1. High-Precision Currency Handling
- **Why**: Floating-point math (e.g., `19.99 * 100`) in Python can result in precision errors, leading to incorrect transaction amounts.
- **How**: All currency calculations now use the `decimal.Decimal` class.
- **Implementation**: `unit_amount = int(payment.amount * Decimal('100'))`

### 2. Robust Webhook Signal System
- **Why**: The system previously only acknowledged successful checkouts. Failed payments or refunds triggered via the Stripe Dashboard were not reflected in the database.
- **How**: Expanded the `StripeWebhookView` to handle `payment_intent.payment_failed` and `charge.refunded` events.
- **Safety**: Added `try-except` blocks and structured logging to event handlers to ensure a single failing event doesn't crash the webhook listener.

### 3. Actual Refund Implementation
- **Why**: The security deposit release logic was previously a placeholder.
- **How**: Implemented `stripe.Refund.create` in the `release_security_deposit` service.
- **Result**: When a booking is marked as returned, the security hold is now actually released on the gateway side.

### 4. Frontend-Friendly API
- **Why**: Server-side 303 redirects are difficult for modern SPA (React) frontends to intercept.
- **How**: The session creation endpoint now returns a JSON response containing the `checkout_url`.

---

## 🏗 Architecture

- **`models.py`**: Defines the `Payment` model with a UUID for security and fields for tracking gateway IDs and raw responses.
- **`views.py`**: Contains the logic for creating Stripe sessions and the webhook listener.
- **`services.py`**: Business logic layer for interacting with the Stripe API (e.g., refunds).
- **`signals.py`**: Asynchronous glue logic that links payment success to booking status updates.

---

## ⚙️ Configuration

Ensure the following variables are set in your `.env` file:

```env
STRIPE_TEST_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
SITE_URL=http://localhost:3000
```

## 🧪 Testing

To verify the payment logic without a full Stripe integration:

1. **Precision Check**:
   ```bash
   python3 manage.py shell -c "from decimal import Decimal; print(int(Decimal('19.99') * Decimal('100')))"
   ```
2. **Migration Sync**:
   ```bash
   python3 manage.py migrate payments
   ```
3. **Webhook Simulation**:
   Use the Stripe CLI:
   ```bash
   stripe trigger payment_intent.succeeded
   ```
