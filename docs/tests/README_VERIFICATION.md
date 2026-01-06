# 🎓 Learning Guide: API Verification Scripts

This directory contains standalone Python scripts used to verify the backend API logic without needing a frontend or manual Postman testing.

## 📝 Script: `verify_staff_management.py`

This script demonstrates how to test a Django REST Framework (DRF) `ViewSet` directly.

### Key Learning Concepts:

1.  **Django Environment Setup**:
    - Standalone scripts must tell Django where the `settings.py` is (`DJANGO_SETTINGS_MODULE`).
    - `django.setup()` must be called to load models and apps into memory.

2.  **APIRequestFactory**:
    - A tool that creates "fake" HTTP requests.
    - Unlike a real browser request, this doesn't go over the network; it calls the view functions directly in Python.

3.  **Force Authentication**:
    - Testing protected views (those requiring a login) is easy with `force_authenticate(request, user=user)`.
    - This bypasses the actual JWT or Session login logic and tells DRF "act as if this user is already logged in."

4.  **The Test Lifecycle**:
    - **Setup**: Create temporary test data (Admins, Agencies, Users). 
    - **Execution**: Trigger the view (Create Staff, List Staff, Remove Staff).
    - **Assertions**: Check the `response.status_code` and reload data from the database (`staff_user.refresh_from_db()`) to verify the side effects (like role changes).

### Why use these scripts?
- **Speed**: They run in seconds.
- **Repeatability**: Using timestamps in usernames/emails ensures you can run the test 100 times without "Duplicate Key" errors.
- **Documentation**: The script itself acts as a technical specification of how the API should behave.

---
*Keep these scripts in your `docs/tests` folder for maintenance and future debugging!*
