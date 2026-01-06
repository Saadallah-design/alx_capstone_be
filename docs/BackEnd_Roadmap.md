## 🗺️ Backend Roadmap: Phuket Rental API (MVP Focus)

The roadmap is divided into four sequential Sprints, with a heavy emphasis on **reliability** and **performance** in the core booking logic.

---

## ⚡ Sprint 1: Setup & Authentication (1 Week)

The goal is to establish the secure foundation and enable user roles (Customer and Agency Admin).

| Task Category | Feature | Implementation Detail |
| :--- | :--- | :--- |
| **Project Setup** | Initialize Project & Dependencies | Install **Django**, **DRF**, **PostgreSQL** (for production consistency), and **`django-environ`** for managing environment variables. |
| **Base Models** | Core Model Creation | Create **`User`** model (AbstractBaseUser or custom fields on default) with `is_agency_admin` boolean field. Create **`Agency`** model, linking it **One-to-One** with the `User`. |
| **Authentication** | JWT Implementation | Integrate **`djangorestframework-simplejwt`** for token-based authentication (stateless is better for APIs). |
| **Endpoints** | Auth APIs | Create endpoints for **`/api/v1/auth/register/`** (supporting both user types) and **`/api/v1/auth/token/`** (login). |
| **Access Control** | Permissions Setup | Define custom **DRF Permissions** (e.g., `IsAgencyAdmin`, `IsCustomer`), ensuring only Agency Admins can create and edit car listings. |

---

## 🛠️ Sprint 2: Agency & Car Management (2 Weeks)

The goal is to allow agencies to manage their Phuket car/scooter inventory and enable the public search.

| Task Category | Feature | Implementation Detail |
| :--- | :--- | :--- |
| **Listing Models** | **`Car`** and **`CarImage`** Models | Add fields like `daily_rate`, `transmission`, `car_type` (for filtering), and `is_published`. **Crucially, add `db_index=True`** to `daily_rate` and `car_type` for faster filtering. |
| **Image Upload** | Cloud Storage Integration | Configure **`django-storages`** (e.g., to connect to AWS S3 or Cloudinary) for permanent, high-performance static file storage. |
| **Agency Dashboard API**| Agency Car CRUD | Implement **`ModelViewSet`** for `Car` under **`/api/v1/agency/cars/`**. This endpoint *must* use `IsAgencyAdmin` permission and filter results to show only *their* cars. |
| **Search Model** | **`Booking`** Model Stub | Create the **`Booking`** model with `start_date`, `end_date`, `car` FK, and `status` (Pending, Confirmed). This is needed for the next task. |

---

## 🔍 Sprint 3: High-Performance Search & Availability (2 Weeks)

This is the **most complex and critical** sprint. Getting the availability logic right prevents double-bookings and ensures a fast user experience.

| Task Category | Feature | Implementation Detail |
| :--- | :--- | :--- |
| **Public Search API** | Optimized Car Listing Endpoint | Create a **`ListAPIView`** at **`/api/v1/cars/`** that accepts `start_date` and `end_date` as required query parameters. |
| **Availability Logic** | Date Range Conflict Check | Use a custom filter to exclude cars that have an **overlapping booking** using the **Non-Overlapping Condition** query structure on the `Booking` model. $$\text{Exclude Booking where: } (Booking.\text{end\_date} \ge \text{RequestedStart}) \text{ AND } (Booking.\text{start\_date} \le \text{RequestedEnd})$$
| **Data Optimization** | Filtering & Indexing | Implement **`django-filter`** for easy filtering by `car_type`, `price`, and `transmission`. Ensure `select_related()` is used on the `Car` queryset to fetch related `Agency` data in one query. |
| **Single Car View** | Car Details Endpoint | Create **`/api/v1/cars/{id}/`** to display full car details and the current availability for the specified dates. |

---

## 💳 Sprint 4: Atomic Booking & Business Logic (3 Weeks)

The goal is to guarantee data integrity during a transaction and prepare for payment integration.

| Task Category | Feature | Implementation Detail |
| :--- | :--- | :--- |
| **Atomic Booking API** | Reservation Creation Endpoint | Create **`POST /api/v1/bookings/`**. The core logic **MUST** be wrapped in **`@transaction.atomic`** (or `with transaction.atomic():`).  |
| **Transaction Logic** | Prevent Race Conditions | Inside the atomic block, re-run the exact **Availability Check** query from Sprint 3 one last time. If no conflict is found, create the `Booking` record with `status='Pending'`. If a conflict is found, raise an exception to **rollback** the entire transaction. |
| **Pricing Model** | Final Price Calculation | Implement logic to calculate `total_price` based on `daily_rate_at_booking`, duration, and any fixed fees/taxes, ensuring this price is saved *at the time of booking* to prevent future manipulation. |
| **Booking Management** | Agency Booking List | Create **`/api/v1/agency/bookings/`** to allow Agency Admins to view and update the status (`Pending` $\rightarrow$ `Confirmed`, `Cancelled`, `Completed`). |
| **Payment Placeholder**| Initial Payment Setup | Integrate **Stripe** or other payment library (e.g., using **webhooks** for post-payment confirmation). For MVP, this might only capture deposit/reservation fees, leaving the balance to be paid to the agency in Phuket. |

---

## 📈 Future Sprints (Post-MVP)

These features will be critical for scaling and market advantage:

| Priority | Feature | Implementation Detail |
| :--- | :--- | :--- |
| **P5 (Reviews)** | Review/Rating System | New **`Review`** model linked to `Booking`. Use Django **Signals** to automatically update the `Agency.rating_average` field whenever a new review is submitted. |
| **P6 (Notifications)** | Email/SMS Notifications | Use a background task queue like **Celery** to handle asynchronous tasks: sending booking confirmation emails, reservation reminders, and status updates to the Agency. |
| **P7 (Geo-Search)** | Location Filtering | Integrate a service like **PostGIS** (PostgreSQL extension) for geospatial queries, allowing customers to search for cars within a 5km radius of a specific Phuket landmark. |