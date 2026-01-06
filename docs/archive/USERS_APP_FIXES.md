# Users App Implementation Fixes & Explanations

This document details the critical fixes and architectural patterns applied to the `users` app implementation.

## 1. Models (`users/models.py`)

### Problem
The initial implementation of `User` lacked helper methods to easily check roles or retrieve the associated agency. This would have forced every view or serializer to write complex `if/else` logic to check `role == 'AGENCY_ADMIN'` etc.

### Fixes Applied

#### A. Role Helper Methods
Added boolean checks for every role. This makes the code readable and less prone to string typos.
```python
def is_agency_admin(self):
    return self.role == 'AGENCY_ADMIN'

def is_platform_admin(self):
    return self.role == 'PLATFORM_ADMIN'
# ... etc
```

#### B. Unified `agency` Property
This is a critical architectural fix.
-   **Agency Owners** are linked via `agency_profile` (OneToOne).
-   **Agency Staff** are linked via `agency_membership` (OneToOne to AgencyMember).

We added a property that abstracts this difference away:
```python
@property
def agency(self):
    if self.is_agency_admin():
        return getattr(self, 'agency_profile', None)
    elif self.is_agency_staff():
        membership = getattr(self, 'agency_membership', None)
        return membership.agency if membership else None
    return None
```
**Benefit**: In serializers/views, you can just call `user.agency` without caring *how* they are connected to it.

## 2. Serializers (`users/serializers.py`)

### Problem
The manual implementation had several logical errors:
1.  **Undefined Returns**: The `validate` method in `CustomTokenObtainPairSerializer` was returning a variable `token` that didn't exist in that scope (it holds `data` from the parent method).
2.  **Incorrect Relationships**: It tried to access `user.rentals`, but the `Booking` model uses `related_name='bookings'`.
3.  **Missing Imports**: The `Agency` model wasn't imported.

### Fixes Applied

#### A. Corrected Token Response
Fixed the return value to send the actual response data.
```python
def validate(self, attrs):
    data = super().validate(attrs)
    # ... add custom data ...
    return data  # <-- Fixed: Was returning 'token'
```

#### B. Fixed Reverse Relationships
Aligned the field access with the `Booking` model definition.
```python
def get_total_rentals(self, obj):
    # Fixed: 'rentals' -> 'bookings'
    return obj.bookings.count()
```

## 3. Views (`users/views.py`)

### Problem
The `UserProfileView` was defined as a Class-Based View (CBV) inheriting from `RetrieveUpdateAPIView`, but it was incorrectly decorated with function-based view decorators (`@api_view`). This causes conflicts in DRF. Additionally, it didn't know *which* user to retrieve (missing `get_object`).

### Fixes Applied

#### A. Removed Decorators & Added Attributes
Converted decorators to proper class attributes.
```python
class UserProfileView(generics.RetrieveUpdateAPIView):
    # Fixed: Moved from @permission_classes decorator
    permission_classes = [IsAuthenticated]
    
    # Fixed: Used the detailed serializer to show stats
    serializer_class = UserProfileDetailSerializer
```

#### B. Implemented `get_object`
By default, a DetailView expects a `pk` in the URL (e.g., `/users/1/`). For a "Me" profile endpoint (`/me/`), we don't send an ID. We fixed this by overriding `get_object` to return the currently logged-in user.
```python
def get_object(self):
    return self.request.user
```
