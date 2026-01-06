# 🚗 Car Rental API (alx_capstone_be)

## Project Idea (Brief)
A robust Car Rental API built with Django REST Framework (DRF), designed to manage car inventory, rental branches, and bookings. The API supports secure, role-based access, advanced availability search, and transactional booking logic to prevent double-bookings and ensure data integrity.

---

## What Has Been Done So Far
- **Project Initialization:**
  - Django project and main app structure created
  - Virtual environment and PostgreSQL database configured
- **Core Models:**
  - Custom `User` model with agency/admin roles
  - `Agency` and `Location` models for business and branch management
- **Authentication & Security:**
  - JWT authentication set up using DRF SimpleJWT
  - Permissions and access control for users and admins
- **Environment Management:**
  - `.env` file for secrets and database credentials
  - `.gitignore` configured to protect sensitive files
  - Documentation on environment variable management added
- **API & CRUD:**
  - Initial endpoints for user registration and login
  - Basic CRUD for core models (in progress)
- **Documentation:**
  - Project roadmap and environment setup guides written

---

## Challenges Encountered
- **Environment Variable Management:**
  - Deciding between `python-dotenv` and `django-environ` for loading environment variables; resolved by standardizing on `python-dotenv` for simplicity.
  - Ensuring `.env` is always excluded from version control for security.
- **Database Connection:**
  - Handling PostgreSQL authentication and password management, especially with local vs. production settings.
- **Custom User Model:**
  - Migrating from Django's default user to a custom user model with roles, which required careful planning to avoid migration issues.
- **Permissions & Security:**
  - Implementing fine-grained permissions for different user roles and ensuring endpoints are secure by default.
- **Project Structure:**
  - Keeping the project modular and maintainable as new features and models are added.

---

## Next Steps
- Complete CRUD endpoints for all core models
- Implement advanced search and booking logic
- Add unit tests for permissions and booking concurrency
- Polish documentation and prepare for deployment

---

**End of README**
