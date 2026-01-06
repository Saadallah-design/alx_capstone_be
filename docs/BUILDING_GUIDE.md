# Building a Robust Payment System for Rentals 🚗💳

Implementing a payment system for a rental platform (cars, bikes, apartments) is significantly different from a standard e-commerce "buy now" flow. It involves deposits, holds, and complex status management.

This guide outlines the architecture, best practices, and pitfalls to avoid based on the technical implementation performed in this project.

---

## 🏗 1. Core Architecture Pattern

### The Model: Linking, Not Copying
Your `Payment` model should be the "financial shadow" of your `Booking`.
- **Reference**: Link to the `Booking` via a Foreign Key.
- **UUIDs**: Use a `uuid` field for external references (API requests/urls) to prevent ID enumeration attacks.
- **Types**: Differentiate between `RENTAL_FEE` and `SECURITY_DEPOSIT`.

### The Gateway Flow: Two-Step Verification
For rentals, always use **Manual Capture** for deposits:
1. **Authorize**: Lock the funds on the user's card (ensures they have it).
2. **Capture**: Take the money later (e.g., if there's damage).
3. **Release**: Return the hold if the vehicle is returned safely.

---

## ⭐ 2. Best Practices

### ✅ Use Decimals for Everything
**Mistake to Avoid**: Using `float` for prices. Floating-point math is imprecise (e.g., `0.1 + 0.2 != 0.3`).
**Best Practice**: Use `Decimal` in Django and always convert to the gateway's smallest unit (cents) using `int(amount * Decimal('100'))`.

### ✅ Webhooks are Mandatory
**Why**: A user might close their browser while the Stripe page is loading. Without webhooks, your server will never know if they paid.
**Best Practice**: Implement a listener for `checkout.session.completed`, `payment_intent.payment_failed`, and `charge.refunded`.

### ✅ Idempotency & Metadata
Gateways like Stripe allow you to pass `metadata`. 
- **CRITICAL**: Always send your internal `payment_uuid` in the metadata. This is the only way to "find" the correct record when the webhook event comes back.

### ✅ Signal-Driven Business Logic
Keep your views "thin." 
- When a payment is successful, updated the `Payment` record.
- Use a Django **Signal** (`post_save`) to listen for `status='COMPLETED'` and then update the `Booking` status. This keeps the code decoupled and clean.

---

## ⚠️ 3. Mistakes to Avoid

### ❌ Storing Card Data
**Never** store credit card numbers, CVVs, or expiry dates in your database. 
- **The Fix**: Use Stripe Elements or Checkout Sessions. The sensitive data stays on their PCI-compliant servers; you only store an "obfuscated" token or the `payment_intent_id`.

### ❌ Ignoring Idempotency in Tests
If you run a script to create a "Test Booking" multiple times, it will eventually fail due to "Overlap" validation errors.
- **The Fix**: Setup scripts should delete previous test records before creating new ones.

### ❌ Incomplete Webhook Handling
Many developers only handle "Success."
- **The Pitfall**: If a payment fails 10 minutes after the user leaves the site, you need a failure webhook to mark the booking as cancelled or pending.

### ❌ Blocking Webhook Workers
Webhook views should be extremely fast. 
- **Best Practice**: If you need to send a complex "Booking Confirmed" email or generate a PDF invoice, do it in a background task (like Celery) triggered by the signal, not directly inside the Webhook view response.

---

## 🛠 4. Checklist for a New Project

- [ ] **Environments**: Separate keys for `TEST` and `LIVE` environments.
- [ ] **CSRF**: Decide if your session-initiation endpoint needs CSRF or if it's protected by JWT/OAuth.
- [ ] **Precision**: Write a test case for `Decimal` to `cents` conversion.
- [ ] **Cleanup**: Implement `on_delete=models.PROTECT` for payments to ensure financial history is never accidentally deleted.
- [ ] **Logging**: Log the `raw_gateway_response` for every transaction. It is your only evidence if a dispute occurs.

---

## 📄 Final Summary for Success
A great payment app doesn't just take money; it **manages financial state**. By separating the "Request" (Session) from the "Confirmation" (Webhook) and the "Business Logic" (Signals), you create a system that can handle network failures, user errors, and manual gateway intervention without losing track of a single cent.
