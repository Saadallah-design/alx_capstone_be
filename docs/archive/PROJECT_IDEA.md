# 💡 Project Idea: 
Car Rental API using Django REST Framework (DRF).
Project Features:
1. Foundational CRUD Features (Basic Data Management)
2. Security & Permissions Features (Access Control) : Ensuring that only the right users can perform sensitive actions.
Token-Based Authentication: Users must submit a valid authentication token to perform any non-read operation (e.g., booking a car).
Rental Ownership: Only the User who created a specific Rental agreement can modify, update, or cancel it.
Admin/Staff Access: Only staff users (or a Superuser) should be able to create, update, or delete Car and RentalBranch records.

3. Search & Availability Features (The Capstone Logic)
Availability Search Endpoint: A dedicated endpoint that accepts mandatory search parameters: Pick-up Branch ID, Start Time, and End Time.
Advanced Filtering: The API must return a list of Car objects that meet two criteria:
The car is currently located at the Pick-up Branch.
The car is not booked for the requested time slot (no overlapping Rental records).
Time Zone Conversion: All incoming start_time and end_time values must be handled and validated after being converted to UTC, ensuring accurate concurrency checks.
Basic Car Filters: Allow users to filter the available list by non-temporal features (e.g., make, model, transmission).

4. Transactional & Workflow Features (Business Utility)
Concurrency Validation: Strict database check to prevent a new rental from being saved if it overlaps with an existing rental for the same car. This is done on the server-side before saving.
Pricing Calculation: Automatically calculate the total_price for a Rental based on the duration (e.g., daily rate of the car * number of days) during the creation process.
One-Way Rental Support: The system must allow the pick_up_branch and drop_off_branch fields to be different. The Car.current_branch field must be updated by a separate API call upon virtual drop-off.


Models: Core Models
RentalBranch
Defines the physical locations for car pick-up and drop-off.
Acts as the Location resource in the Geo-Temporal model.
Car
Represents the actual inventory—the specific vehicles available for rent.
Acts as the Resource that is being scheduled.
Rental
Records the temporal reservation of a car by a user.
Acts as the Booking resource, central to concurrency checks.
User
Handled by Django's built-in auth_user table, but is essential for security and ownership.
Acts as the Customer and the Author of the rental record.
Project Plan
Phase 1: Setup & Core Models
My goal here is to establish the basic environment and the fundamental database structure.
1. Project Setup:
Create the Django project and the api app.
Install necessary libraries: django rest_framework.
Configure settings.py (add rest_framework and the api app to INSTALLED_APPS).
2. Define Core Models:
Define the three essential models in api/models.py:
RentalBranch (Location)
Car (Resource)
Rental (Booking)
Ensure all Foreign Key relationships are correctly defined (I need more reading here).
3. Database Initialization:
Run python manage.py makemigrations api.
Run python manage.py migrate to create the tables.
4. Test Data:
Run python manage.py createsuperuser (i need to ensure creating a .venv file to store passwords etc).
Use the Django Admin to manually add at least two RentalBranch entries and five Car entries.
Phase 2: Basic CRUD & Routing 
Focus here is on getting the most standard API functionality running for the main data objects.
1. Define Serializers:
Create api/serializers.py and define the CarSerializer and RentalBranchSerializer extending ModelSerializer.
2. Implement ViewSets:
Create api/views.py and define a simple CarViewSet extending ModelViewSet. Set the queryset and serializer_class.
3. Configure Routing:
Create api/urls.py.
Import and initialize the DefaultRouter.
Register CarViewSet using router.register(r'cars', CarViewSet).
4. Test Basic CRUD:
Start the server and test listing, retrieving, creating, and deleting cars using the Browsable API (/api/cars/).
Phase 3: Authentication & Security
Secure my API and implement ownership control.
1. Configure Token Auth:
Add rest_framework.authtoken to INSTALLED_APPS in settings.py and run migrate.
Update settings.py to set DEFAULT_AUTHENTICATION_CLASSES (TokenAuthentication) and DEFAULT_PERMISSION_CLASSES (IsAuthenticated).
2. Implement Token Endpoint:
In api/urls.py, add the route for the built-in obtain_auth_token view.
3. Define Custom Permissions:
Create api/permissions.py and define IsAuthorOrReadOnly (or a similar ownership permission for the Rental model).
4. Secure ViewSet:
In api/views.py, apply the custom permission to CarViewSet. Test creating a car (requires login) vs. viewing cars (public).
Phase 4: Geo-Temporal Logic
This is the real challenge: I need to implement the concurrency and availability check.
1. Rental Serializer & ViewSet:
Define the RentalSerializer.
Define the RentalViewSet for CRUD operations on rental agreements.
2. Concurrency Validation:
Implement the custom validation logic in RentalSerializer's validate() method or the RentalViewSet's perform_create() method. This logic must prevent time overlaps for the same car.
3. Availability Endpoint (The Filter):
Create a separate ListAPIView or custom action in RentalViewSet that accepts pick_up_branch_id, start_time, and end_time query parameters.
Write the complex queryset logic that excludes cars that are already booked during the requested time slot.
Phase 5: Polish & Documentation 
Finalize the project and make it presentable for a capstone review.
1. Pricing Logic:
Implement simple logic in the RentalViewSet's perform_create to calculate a placeholder total_price based on the rental duration.
2. Documentation:
Write a comprehensive README.md explaining how to set up, run, and interact with the API (include all endpoint URLs and required headers for Token Auth).


3. Testing:
Write a few simple unit tests for my custom permission class and concurrency validation logic. (I need to do reading here as well!)
4. Presentation Prep:
Preparing the final video for the capstone.

