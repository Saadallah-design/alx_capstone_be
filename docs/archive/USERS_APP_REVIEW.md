
## 4. Verification Status (Verified on 2026-01-02)

### A. Syntax & Structure
- **Checked**: `users/serializers.py` syntax error (dictionary closure) has been fixed.
- **Checked**: All imports in `users/serializers.py` are valid.
  - `core.models.Agency` exists and is correctly imported.
  - `django.contrib.auth.get_user_model` is used correctly.

### B. Relationships
- **Checked**: `User.bookings` reverse relationship.
  - Confirmed in `rentals/models.py`: `user = models.ForeignKey('users.User', ..., related_name='bookings')`.
  - Serializer usage `obj.bookings.count()` is correct.

### C. Agency Integration
- **Checked**: `user.agency` property in `users/models.py`.
  - Handles both `agency_profile` (Owner) and `agency_membership` (Staff).
- **Checked**: `Agency` model fields.
  - `users/serializers.py` accesses `id`, `agency_name`. These exist in `core/models.py`.
  - Note: `slug` is accessed via `getattr(..., 'slug', None)`, which is safe but the field does not strictly exist in the `Agency` model yet.

### D. Views & URLs
- **Checked**: `users/urls.py` correctly maps endpoints to views.
- **Checked**: `users/views.py` permissions and serializer classes are appropriate.

### E. Dynamic Testing (Verified via Scripts)
- **User Registration**: SUCCESS
  - Script: `test_registration.py`
  - Result: User created successfully with role `CUSTOMER`.
  - Password Hashing: Verified working.
  - Agency Association: Correctly returns `None` for generic customers.

- **Authentication & Profile Flow**: SUCCESS
  - Script: `test_user_flow.py`
  - **Login (JWT)**: Tokens generated with correct custom access claims (`role`, `agency_id`).
  - **Profile (`/me/`)**: Serializer returns correct user details and handles `agency: None` for customers.
  - **Agency Admin Support**: 
    - Verified that promoting a user to `AGENCY_ADMIN` and linking an agency automatically updates their token claims (`agency_id`).
    - Validated that the profile endpoint correctly nests the `Agency` data for admins.
