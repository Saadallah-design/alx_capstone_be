# ALX Vehicle Rental - Backend API 🚗💨

## 🌟 The Vision & Utility
**ALX Vehicle Rental** is more than just a vehicle booking script; it is a **comprehensive Multi-Tenant Fleet Management Ecosystem**. 

### The Problem
Most vehicle rental solutions are either "single-shop" (one company, one fleet) or "unmanaged marketplaces" where data isolation and administrative control are messy and insecure.

### The Solution (Utility)
This project aims to solve this by providing a high-performance, secure backend that serves two distinct audiences through a single API:

1.  **For Car Rental Agencies (The B2B Utility)**:
    - **Digital Transformation**: Small to medium agencies can digitize their entire fleet management, from branch inventory to complex booking schedules.
    - **Multi-Tenant Security**: Strict data isolation ensures an agency's fleet, staff, and financial data are completely private from competitors using the same platform.
    - **Write-Aggressive Dashboarding**: A specialized API layer optimized for "Fleet Management" (JSON-nested specs, absolute image pathing, and license plate tracking) that prevents the typical "state-reset" bugs found in simpler CRMs.

2.  **For Customers (The B2C Utility)**:
    - **Unified Search**: A streamlined, filtered search experience across all verified agencies and branches.
    - **Real-Time Availability**: Powered by PostgreSQL `ExclusionConstraints` to ensure a car is never double-booked, even at high volumes.
    - **Frictionless Payments**: Integrated Stripe checkout for a modern, secure, and trust-building booking experience.

---

## 🚀 Live Demo
**Backend API**: [https://alx-car-rental-api.onrender.com/](https://alx-car-rental-api.onrender.com/)  
**Public Dashboard**: [https://alx-capstone-fe.vercel.app/](https://alx-capstone-fe.vercel.app/)

---

## ✨ Key Features

### 🏢 Multi-Tenancy & Agency Management
- **Data Isolation**: Agency administrators can only manage vehicles and bookings associated with their own agency.
- **Fleet Management**: Robust CRUD for vehicles, including technical specs and image uploads.
- **Branch Control**: Manage multiple physical locations for vehicle pick-up and drop-off.

### 💳 Payments & Bookings
- **Stripe Integration**: Secure payment processing with real-time webhook synchronization.
- **Booking Overlap Prevention**: Advanced PostgreSQL constraints (`ExclusionConstraint`) to prevent double-booking.
- **Dynamic Pricing**: Automatic rental rate calculations.

### 🔐 Security & Auth
- **JWT Authentication**: Secure stateless authentication for all users.
- **Role-Based Access Control (RBAC)**: Distinct permissions for Customers, Agency Staff, Agency Admins, and Platform Admins.
- **Absolute URL Integrity**: Consistent image pathing for cross-domain frontend consumption.

---

## 🛠️ Tech Stack
- **Framework**: Django & Django REST Framework (DRF)
- **Database**: PostgreSQL (with `btree_gist` extension)
- **Payments**: Stripe API
- **Documentation**: Swagger/OpenAPI via `drf-spectacular`
- **Hosting**: Render (Backend) & Vercel (Frontend)

---

## 📦 Installation & Setup

### Prerequisites
- Python 3.10+
- PostgreSQL
- Stripe Account (for payment features)

### Local Development
1. **Clone the repository**:
   ```bash
   git clone https://github.com/Saadallah-design/alx_capstone_be.git
   cd alx_capstone_be
   ```

2. **Setup virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Mac/Linux
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Create a `.env` file in the root directory (see `carRentalConfig/settings.py` for required variables).

4. **Run Migrations & Seed Data**:
   ```bash
   python manage.py migrate
   python manage.py seed_data
   ```

5. **Start the server**:
   ```bash
   python manage.py runserver
   ```
