# Next Steps: Vehicles App Implementation

The next logical step in building the Modular Monolith is to implement the **Vehicles App** (`vehicles`). This app is central to the platform, connecting `users` (agencies) to `rentals` (bookings).

## 1. Goal
Create a robust Vehicle Management system that allows:
- **Agencies** to add, update, and manage their fleet.
- **Customers** to browse and filter available vehicles.
- **System** to track vehicle status and specifications.

## 2. Models Refinement (`vehicles/models.py`)
The current `Vehicle` model is a good start but needs enhancement:

-   **Images**: Add support for vehicle images.
    -   *Recommendation*: Create a `VehicleImage` model to allow multiple images per vehicle (Main image + angles/interior).
-   **Slug**: Add a slug field for SEO-friendly URLs (`/vehicles/toyota-camry-2024-xc90`).
-   **Timestamps**: Add `created_at` and `updated_at`.

### Proposed Structure
```python
class Vehicle(models.Model):
    # Existing fields...
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # ...

class VehicleImage(models.Model):
    vehicle = models.ForeignKey(Vehicle, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='vehicles/')
    is_main = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```

## 3. Serializers (`vehicles/serializers.py`)
We need robust serializers to handle nested data:

1.  **VehicleImageSerializer**: For handling image uploads/display.
2.  **VehicleSpecsSerializer**: For detailed specs (transmission, fuel, etc.).
3.  **VehicleListSerializer**: Lightweight, for search results (Main image, Price, Make, Model).
4.  **VehicleDetailSerializer**: Full details, including all images and full specs.

## 4. Views & API Endpoints (`vehicles/views.py`)

| Endpoint | Method | Permission | Purpose |
| :--- | :--- | :--- | :--- |
| `/api/vehicles/` | GET | AllowAny | List all available vehicles (with filters). |
| `/api/vehicles/` | POST | IsAgencyAdmin | Create a new vehicle. |
| `/api/vehicles/{slug}/` | GET | AllowAny | Retrieve vehicle details. |
| `/api/vehicles/{slug}/` | PUT/PATCH | IsOwnerAgency | Update vehicle details. |
| `/api/vehicles/{slug}/` | DELETE | IsOwnerAgency | Remove a vehicle. |

## 5. Next Actions Checklist
- [ ] Install `Pillow` (if not installed) for image handling.
- [ ] Update `vehicles/models.py`.
- [ ] Create `vehicles/serializers.py`.
- [ ] Create `vehicles/views.py`.
- [ ] Configure `vehicles/urls.py` and include in main `urls.py`.
- [ ] Run Migrations.
- [ ] Verify with a test script (Agency adding a car, Customer viewing it).
