
The core architectural plan and roadmap for our Django backend—including the **Atomic Booking Logic** and the use of **Django REST Framework (DRF)** with **JWT** for authentication—is still the gold standard for our tech stack. Next.js is designed to consume this exact type of API.

our focus should be on **refining security and data transmission best practices** to align perfectly with Next.js's strengths.

---

## 🔒 Backend Refinement for Next.js Integration

The shift to Next.js (especially using Server Components and Middleware) requires absolute clarity and security from the Django API.

### 1. Security: JWT Management is Key

using **stateless authentication (JWT)**, which is perfect for a decoupled app.

* **Django's Role (DRF-SimpleJWT):**
    * **Access Token:** Short-lived (e.g., 5-15 minutes). Used for every protected request (e.g., loading the Agency Dashboard).
    * **Refresh Token:** Long-lived (e.g., 7 days). Used only to get a new Access Token when the old one expires.
    * **Critical Action:** Ensure Django exposes the standard refresh endpoint (`/api/auth/token/refresh/`). Next.js will use this to silently renew the session without forcing a user to re-login.
* **Next.js Interaction:** Next.js **Client Components** will store and manage these tokens securely using client-side **cookies** (`js-cookie` is a common library for this). The tokens are attached to every API request as an `Authorization: Bearer <token>` header.

### 2. Data Transmission: Serializers and DTOs

Django's serializers are our API contract.

* **Data Transfer Objects (DTOs):** Ensure our serializers only expose the necessary data to the client (i.e., Do not send the Car's `license_plate` or the Agency's sensitive `license_no` to the public customer search API).
* **Pre-calculate Status:** For the main car search, make sure our serializer's `available` field is a simple boolean that has already been calculated by the complex availability logic in the DRF view (from Sprint 3), rather than forcing Next.js to run complex availability checks itself.

### 3. API Structure: Clear Resource Endpoints

A RESTful structure is vital for Next.js to manage its data fetching efficiently using `fetch` on the server. 

| Resource Type | Endpoint (DRF ViewSet) | Primary Purpose | Next.js Rendering Strategy |
| :--- | :--- | :--- | :--- |
| **Public Search** | `/api/v1/cars/` | Search with dates/location, returns limited fields. | **SSR/SC** (Server Side Rendering / Server Component) for SEO. |
| **Customer Booking** | `/api/v1/bookings/` | Create a new reservation, view customer history. | **CSR/CC** (Client Side Rendering / Client Component) for interactive forms. |
| **Agency Management** | `/api/v1/agency/cars/` | CRUD for cars, only accessible to admins. | **CSR/CC** (Protected routes with Middleware). |

---

## ⚙️ Backend Roadmap: Key Adjustments

The core roadmap is sound, but we will add explicit checks for Next.js compatibility.

### Sprint 1: Setup & Authentication

* **CORS Configuration:** Use `django-cors-headers`. This is mandatory for a decoupled app. I must explicitly allow the domain where our Next.js application will be running (e.g., `http://localhost:3000` during development).
* **User Endpoint:** Ensure I have a simple `/api/v1/auth/user/` endpoint that uses JWT to return the current user's profile and **role** (`is_agency_admin`). Next.js uses this immediately after login to set up the authentication context.

### Sprint 3: High-Performance Search & Availability

* **Pagination:** Implement proper DRF pagination (e.g., **Limit/Offset** or **Cursor-based**) on the search endpoint (`/api/v1/cars/`). This prevents our Next.js Server Component from trying to render thousands of cars at once, improving load time and core web vitals.

### Sprint 4: Atomic Booking & Business Logic

* **Clear Error Codes:** Ensure our DRF views return clear HTTP status codes (e.g., `409 Conflict` if the atomic check fails due to a double-booking) and detailed, JSON-formatted error messages. This allows Next.js to provide a precise and user-friendly error to the customer.