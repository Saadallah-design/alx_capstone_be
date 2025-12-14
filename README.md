## 💡 Project Idea
**Car Rental API** using Django REST Framework (DRF).

## ✨ Features

- **CRUD Operations:** Basic data management for cars, branches, and rentals.
- **Security & Permissions:**
	- Token-based authentication for all non-read operations.
	- Rental ownership: Only the creator can modify/cancel their rental.
	- Admin/staff: Only staff or superusers can manage cars and branches.
- **Search & Availability:**
	- Endpoint for searching available cars by branch and time slot.
	- Advanced filtering (location, time, car features).
	- Time zone conversion for accurate booking.
- **Transactional Logic:**
	- Prevent overlapping rentals (concurrency validation).
	- Automatic price calculation based on duration and daily rate.
	- One-way rental support (different pick-up/drop-off branches).

## 🗂️ Core Models

- **RentalBranch:** Physical locations for pick-up/drop-off.
- **Car:** Inventory of vehicles available for rent.
- **Rental:** Booking records, including time, car, and user.
- **User:** Customer and author of rental (Django auth).

## 🛠️ Project Plan

### Phase 1: Setup & Core Models
- Initialize Django project and app.
- Install DRF and configure settings.
- Define `RentalBranch`, `Car`, and `Rental` models with correct relationships.
- Run migrations and create test data via Django Admin.

### Phase 2: Basic CRUD & Routing
- Create serializers for core models.
- Implement ViewSets for CRUD operations.
- Set up routers and test endpoints with Browsable API.

### Phase 3: Authentication & Security
- Add token authentication and permissions.
- Implement custom permissions for ownership and admin control.
- Secure endpoints and test access control.

### Phase 4: Geo-Temporal Logic
- Implement concurrency validation to prevent overlapping rentals.
- Add availability search endpoint with advanced filtering.

### Phase 5: Polish & Documentation
- Add pricing logic to rental creation.
- Write clear documentation for setup, usage, and endpoints.
- Add basic unit tests for permissions and concurrency.
- Prepare final presentation materials.

## 📄 Documentation & Testing

- Comprehensive README with setup and API usage instructions.
- Unit tests for custom permissions and booking logic.
