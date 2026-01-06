# Model Critique and Recommendations

> **Last Updated:** December 16, 2025  
> **Project:** Car Rental API - Django Backend

---

## Table of Contents
1. [Issues Successfully Fixed](#issues-successfully-fixed)
2. [Remaining Critical Issues](#remaining-critical-issues)
3. [Missing Features](#missing-features)
4. [Priority Action Items](#priority-action-items)

---

## Issues Successfully Fixed ✅

Great work on addressing these critical issues:

1. ✅ **Added `is_staff` field** (line 45) - Required for Django Admin access
2. ✅ **Added `objects = CustomUserManager()`** (line 49) - Enables custom user creation
3. ✅ **Fixed `related_name` in Agency** - Changed from `'users'` to `'agency_profile'`
4. ✅ **Fixed `__str__` in Location** - Now correctly uses `agency.agency_name`
5. ✅ **Fixed VehicleSpecs choices** - Changed from `'NULL'` to `'NA'`
6. ✅ **Added overlap validation** - Implemented `clean()` method in Booking model
7. ✅ **Changed `is_active` default** - Now `True` for immediate user access

---

## Remaining Critical Issues 🚨

### Issue #1: Vehicle `__str__` Method Still Broken

**Location:** `models.py` Line 111

**Current Code:**
```python
def __str__(self):
    return f"{self.make} ({self.licence_plate}) - {self.agency.name}"  # ❌ Wrong
```

**Problem:** 
- The foreign key is named `owner_agency`, not `agency`
- `Agency` model has `agency_name`, not `name`
- This will crash in Django admin when viewing vehicles

**Fix:**
```python
def __str__(self):
    return f"{self.make} ({self.licence_plate}) - {self.owner_agency.agency_name}"
```

---

### Issue #2: Role Field Design Problem

**Location:** `models.py` Lines 41-44

**Current Code:**
```python
is_agency_admin = models.BooleanField(default=False)
is_customer = models.BooleanField(default=True)
is_agency_staff = models.BooleanField(default=False)
is_staff = models.BooleanField(default=False)
```

**Problem:** 
This design allows **invalid states**. A user could be:
- Both a customer AND agency admin
- Both agency staff AND agency admin
- Unclear distinction between `is_agency_admin` and `is_staff`

**Why This Matters:**
Your permission logic will become complex and error-prone:
```python
# Every permission check needs multiple conditions
if user.is_agency_admin or user.is_agency_staff:
    # allow access
```

#### **Solution Option 1: Single Choice Field (Recommended)**

```python
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('CUSTOMER', 'Customer'),
        ('AGENCY_STAFF', 'Agency Staff'),
        ('AGENCY_ADMIN', 'Agency Admin'),
        ('PLATFORM_ADMIN', 'Platform Admin'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='CUSTOMER',
        help_text='User role in the system'
    )
    
    # Keep these for Django admin functionality
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Convenience methods for clean permission checks
    def is_customer(self):
        return self.role == 'CUSTOMER'
    
    def is_agency_user(self):
        return self.role in ['AGENCY_STAFF', 'AGENCY_ADMIN']
    
    def can_manage_agency(self):
        return self.role == 'AGENCY_ADMIN'
```

**Benefits:**
- ✅ Only one role per user (enforced at database level)
- ✅ Cleaner permission checks: `if user.is_agency_user()`
- ✅ Easy to add new roles without adding fields
- ✅ Prevents invalid states

#### **Solution Option 2: Keep Booleans with Validation**

If you prefer the boolean approach, add validation:

```python
def clean(self):
    # Ensure only one primary role is selected
    role_count = sum([
        self.is_agency_admin,
        self.is_customer,
        self.is_agency_staff
    ])
    if role_count > 1:
        raise ValidationError("A user can only have one primary role")
    if role_count == 0:
        raise ValidationError("A user must have at least one role")
```

---

### Issue #3: No Automatic Cost Calculation

**Location:** `models.py` Line 175

**Current Code:**
```python
# Comment says "calculated at booking time" but no code does this
total_rental_cost = models.DecimalField(max_digits=10, decimal_places=2)
```

**Problem:** 
Someone could manually enter the wrong amount, leading to pricing errors or revenue loss.

#### **Solution: Calculate in `save()` Method**

```python
class Booking(models.Model):
    # ... existing fields ...
    
    def calculate_rental_cost(self):
        """Calculate total cost based on rental duration and daily rate"""
        if self.start_date and self.end_date:
            days = (self.end_date - self.start_date).days
            if days <= 0:
                days = 1  # Minimum 1 day rental
            return self.vehicle.daily_rental_rate * days
        return 0
    
    def save(self, *args, **kwargs):
        # Auto-calculate cost if not set
        if not self.total_rental_cost:
            self.total_rental_cost = self.calculate_rental_cost()
        
        # Always run validation before saving
        self.full_clean()
        super().save(*args, **kwargs)
```

**Why Lock the Price:**
- ✅ If vehicle rates change later, old bookings keep their original price
- ✅ Historical accuracy for financial records
- ✅ No surprises for customers

---

### Issue #4: `clean()` Method Isn't Automatically Called

**Location:** `models.py` Lines 181-189

**Current Code:**
```python
def clean(self):
    overlapping_bookings = Booking.objects.filter(
        vehicle=self.vehicle,
        start_date__lt=self.end_date,
        end_date__gt=self.start_date
    ).exclude(pk=self.pk)

    if overlapping_bookings.exists():
        raise ValidationError("This vehicle is already booked for the selected dates.")
```

**Problem:** 
Django's `clean()` method is **NOT automatically called** when you use:
- ❌ `Booking.objects.create(...)`
- ❌ `booking.save()`
- ❌ DRF serializers (unless you explicitly call it)

**When IS it called?**
- ✅ Django admin forms
- ✅ Django forms  
- ✅ When you manually call `instance.full_clean()`

#### **Fix: Override `save()` to Always Call `clean()`**

```python
def clean(self):
    # Validate dates first
    if self.start_date and self.end_date:
        if self.end_date <= self.start_date:
            raise ValidationError("End date must be after start date.")
    
    # Your existing overlap validation
    overlapping_bookings = Booking.objects.filter(
        vehicle=self.vehicle,
        start_date__lt=self.end_date,
        end_date__gt=self.start_date
    ).exclude(pk=self.pk)

    if overlapping_bookings.exists():
        raise ValidationError("This vehicle is already booked for the selected dates.")

def save(self, *args, **kwargs):
    # Always run validation before saving
    self.full_clean()
    super().save(*args, **kwargs)
```

---

### Issue #5: Missing Date Validation

**Location:** `models.py` Lines 171-172

**Problem:** 
There's no check that `end_date` is after `start_date`. Someone could book from 2025-12-20 to 2025-12-15, which is invalid.

#### **Fix: Add Comprehensive Date Validation**

```python
def clean(self):
    from django.utils import timezone
    from datetime import timedelta
    
    # Validate dates exist
    if not self.start_date or not self.end_date:
        raise ValidationError("Both start and end dates are required.")
    
    # Validate end date is after start date
    if self.end_date <= self.start_date:
        raise ValidationError("End date must be after start date.")
    
    # Prevent bookings in the past
    if self.start_date < timezone.now():
        raise ValidationError("Cannot book dates in the past.")
    
    # Optional: Prevent bookings too far in the future
    max_advance_days = 365  # 1 year
    if self.start_date > timezone.now() + timedelta(days=max_advance_days):
        raise ValidationError(f"Bookings cannot be made more than {max_advance_days} days in advance.")
    
    # Check for overlapping bookings
    overlapping_bookings = Booking.objects.filter(
        vehicle=self.vehicle,
        start_date__lt=self.end_date,
        end_date__gt=self.start_date
    ).exclude(pk=self.pk)

    if overlapping_bookings.exists():
        raise ValidationError("This vehicle is already booked for the selected dates.")
```

---

### Issue #6: No Database-Level Protection Against Race Conditions

**Problem:** 
Your `clean()` validation happens in Python, but two simultaneous requests could both check availability, see no conflicts, then both create overlapping bookings.

**Example Timeline:**
```
Time    Request A                          Request B
----    ---------                          ---------
T0      Check overlaps → None found ✓
T1                                         Check overlaps → None found ✓
T2      Save booking ✓
T3                                         Save booking ✓  ← Both succeeded! ❌
```

#### **Solution: Add Database Constraints + Atomic Transactions**

**Step 1: Add Database Index and Constraints**

```python
class Booking(models.Model):
    # ... existing fields ...
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            # Optimize overlap queries
            models.Index(fields=['vehicle', 'start_date', 'end_date']),
            models.Index(fields=['user', 'booking_status']),
        ]
        constraints = [
            # Ensure end date is after start date (PostgreSQL/MySQL)
            models.CheckConstraint(
                check=models.Q(end_date__gt=models.F('start_date')),
                name='booking_end_after_start'
            ),
        ]
```

**Step 2: Use Atomic Transactions in Your API View**

```python
# In your views.py or serializers.py
from django.db import transaction
from django.db.models import Q

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    
    @transaction.atomic
    def perform_create(self, serializer):
        # Lock the vehicle row to prevent concurrent bookings
        vehicle = Vehicle.objects.select_for_update().get(
            pk=serializer.validated_data['vehicle'].pk
        )
        
        # Now save - the clean() method will run via save()
        instance = serializer.save()
        
        # Update vehicle status
        vehicle.status = 'RENTED'
        vehicle.save()
```

**What `select_for_update()` Does:**
- 🔒 Locks the vehicle database row
- ⏸️ Other requests trying to book the same vehicle must WAIT
- ✅ Prevents the race condition completely
- 🔓 Lock is automatically released after the transaction commits

---

## Missing Features 💡

Based on your `Revisited_Plan.md` and `PROJECT_IDEA.md`, these features are planned but not yet modeled:

### 1. Vehicle Images (Critical for UVP)

Your plan emphasizes **"Visual-First Filtering"** and **"large, high-quality images"**.

```python
class VehicleImage(models.Model):
    vehicle = models.ForeignKey(
        Vehicle, 
        on_delete=models.CASCADE, 
        related_name='images'
    )
    image = models.ImageField(
        upload_to='vehicles/%Y/%m/',
        help_text='Vehicle photo'
    )
    is_primary = models.BooleanField(
        default=False,
        help_text='Primary image shown in vehicle cards'
    )
    caption = models.CharField(
        max_length=200, 
        blank=True,
        help_text='Optional image description'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_primary', 'uploaded_at']
        verbose_name = 'Vehicle Image'
        verbose_name_plural = 'Vehicle Images'
    
    def __str__(self):
        primary = "Primary" if self.is_primary else "Secondary"
        return f"{primary} image for {self.vehicle.make}"
    
    def save(self, *args, **kwargs):
        # If this is set as primary, unset other primary images for this vehicle
        if self.is_primary:
            VehicleImage.objects.filter(
                vehicle=self.vehicle,
                is_primary=True
            ).update(is_primary=False)
        super().save(*args, **kwargs)
```

**Don't Forget:** 
```bash
pip install Pillow
```

---

### 2. Add-ons (Child Seat, GPS, Beach Gear)

Your plan mentions **"bookable add-ons"** and **"Car & Experience Bundling"**.

```python
class Addon(models.Model):
    """Additional items/services that can be added to a booking"""
    
    ADDON_TYPE_CHOICES = [
        ('CHILD_SEAT', 'Child Seat'),
        ('GPS', 'GPS Navigation'),
        ('PHONE_HOLDER', 'Phone Holder'),
        ('BEACH_GEAR', 'Beach Gear Kit'),
        ('SIM_CARD', 'Tourist SIM Card'),
        ('HELMETS', 'Extra Helmets'),
        ('INSURANCE', 'Additional Insurance'),
    ]
    
    agency = models.ForeignKey(
        Agency, 
        on_delete=models.CASCADE, 
        related_name='addons',
        help_text='Agency that offers this add-on'
    )
    name = models.CharField(max_length=100)
    addon_type = models.CharField(max_length=20, choices=ADDON_TYPE_CHOICES)
    description = models.TextField(blank=True)
    price_per_day = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        help_text='Daily rate for this add-on'
    )
    is_available = models.BooleanField(default=True)
    stock_quantity = models.PositiveIntegerField(
        default=1,
        help_text='Number available for simultaneous bookings'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['addon_type', 'name']
        verbose_name = 'Add-on'
        verbose_name_plural = 'Add-ons'
    
    def __str__(self):
        return f"{self.name} - {self.agency.agency_name}"


class BookingAddon(models.Model):
    """Many-to-many relationship between Booking and Addon with quantity"""
    
    booking = models.ForeignKey(
        Booking, 
        on_delete=models.CASCADE, 
        related_name='selected_addons'
    )
    addon = models.ForeignKey(
        Addon, 
        on_delete=models.CASCADE,
        related_name='booking_selections'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        help_text='Number of this add-on for this booking'
    )
    total_price = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        help_text='Total cost for this add-on (calculated automatically)'
    )
    
    class Meta:
        unique_together = ['booking', 'addon']
        verbose_name = 'Booking Add-on'
        verbose_name_plural = 'Booking Add-ons'
    
    def __str__(self):
        return f"{self.addon.name} x{self.quantity} for Booking #{self.booking.id}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate total price
        if not self.total_price:
            booking_days = (self.booking.end_date - self.booking.start_date).days
            if booking_days <= 0:
                booking_days = 1
            self.total_price = self.addon.price_per_day * self.quantity * booking_days
        super().save(*args, **kwargs)
```

**Usage Example:**
```python
# When creating a booking with add-ons
booking = Booking.objects.create(...)
child_seat = Addon.objects.get(addon_type='CHILD_SEAT', agency=booking.agency)
BookingAddon.objects.create(booking=booking, addon=child_seat, quantity=2)

# Calculate total booking cost including add-ons
total = booking.total_rental_cost + sum(
    addon.total_price for addon in booking.selected_addons.all()
)
```

---

### 3. Security Deposit Tracking

Your plan emphasizes **"Deposit Clarity"** with visual deposit information.

**Add to Booking Model:**

```python
class Booking(models.Model):
    # ... existing fields ...
    
    # Security deposit fields
    security_deposit = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=0,
        help_text='Refundable security deposit amount'
    )
    deposit_status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending Collection'),
            ('HELD', 'Held by Agency'),
            ('REFUNDED', 'Refunded to Customer'),
            ('PARTIALLY_REFUNDED', 'Partially Refunded'),
            ('FORFEITED', 'Forfeited (Damages)'),
        ],
        default='PENDING',
        help_text='Current status of the security deposit'
    )
    deposit_collected_date = models.DateTimeField(
        null=True, 
        blank=True,
        help_text='When the deposit was collected'
    )
    deposit_refunded_date = models.DateTimeField(
        null=True, 
        blank=True,
        help_text='When the deposit was refunded'
    )
    refund_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Actual amount refunded (may differ if damages)'
    )
    deposit_notes = models.TextField(
        blank=True,
        help_text='Notes about deposit (e.g., damage deductions)'
    )
```

---

### 4. Reviews and Ratings (Trust Building)

Your plan mentions showing **"Agency Rating (4.8/5)"** for trust building.

```python
class Review(models.Model):
    """Customer review after completing a booking"""
    
    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name='review',
        help_text='Review must be linked to a completed booking'
    )
    
    # Overall ratings (1-5 scale)
    overall_rating = models.PositiveSmallIntegerField(
        choices=[(i, f"{i} Star{'s' if i > 1 else ''}") for i in range(1, 6)],
        help_text='Overall experience rating (1-5)'
    )
    vehicle_condition_rating = models.PositiveSmallIntegerField(
        choices=[(i, i) for i in range(1, 6)],
        help_text='Vehicle cleanliness and condition'
    )
    service_rating = models.PositiveSmallIntegerField(
        choices=[(i, i) for i in range(1, 6)],
        help_text='Customer service quality'
    )
    value_rating = models.PositiveSmallIntegerField(
        choices=[(i, i) for i in range(1, 6)],
        help_text='Value for money'
    )
    
    # Written review
    title = models.CharField(
        max_length=200,
        blank=True,
        help_text='Review headline/title'
    )
    comment = models.TextField(
        blank=True,
        help_text='Detailed review text'
    )
    pros = models.TextField(
        blank=True,
        help_text='What the customer liked'
    )
    cons = models.TextField(
        blank=True,
        help_text='What could be improved'
    )
    
    # Metadata
    would_recommend = models.BooleanField(
        default=True,
        help_text='Would recommend to others'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Agency response
    agency_response = models.TextField(
        blank=True,
        help_text='Agency response to the review'
    )
    responded_at = models.DateTimeField(null=True, blank=True)
    responded_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='review_responses'
    )
    
    # Moderation
    is_verified = models.BooleanField(
        default=True,
        help_text='Review is from verified booking'
    )
    is_flagged = models.BooleanField(
        default=False,
        help_text='Flagged for inappropriate content'
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
    
    def __str__(self):
        return f"Review for Booking #{self.booking.id} - {self.overall_rating}/5"
    
    def clean(self):
        # Only allow reviews for completed bookings
        if self.booking.booking_status != 'COMPLETED':
            raise ValidationError("Reviews can only be created for completed bookings.")
```

**Add Helper Method to Agency Model:**

```python
class Agency(models.Model):
    # ... existing fields ...
    
    @property
    def average_rating(self):
        """Calculate average rating from all reviews"""
        from django.db.models import Avg
        reviews = Review.objects.filter(booking__agency=self)
        avg = reviews.aggregate(Avg('overall_rating'))['overall_rating__avg']
        return round(avg, 1) if avg else 0
    
    @property
    def review_count(self):
        """Total number of reviews"""
        return Review.objects.filter(booking__agency=self).count()
```

---

### 5. Seasonal Pricing Support

Your plan mentions **"Allow agencies to set Seasonal Rates (High, Peak, Green season)"**.

```python
class SeasonalPricing(models.Model):
    """Override vehicle pricing for specific date ranges"""
    
    SEASON_TYPE_CHOICES = [
        ('LOW', 'Green/Low Season'),
        ('NORMAL', 'Normal Season'),
        ('HIGH', 'High Season'),
        ('PEAK', 'Peak Season'),
    ]
    
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='seasonal_prices'
    )
    season_type = models.CharField(max_length=10, choices=SEASON_TYPE_CHOICES)
    start_date = models.DateField(help_text='Season start date')
    end_date = models.DateField(help_text='Season end date')
    daily_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Override daily rental rate for this period'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['start_date']
        verbose_name = 'Seasonal Pricing'
        verbose_name_plural = 'Seasonal Pricing'
    
    def __str__(self):
        return f"{self.vehicle.make} - {self.season_type} ({self.start_date} to {self.end_date})"
    
    def clean(self):
        if self.end_date <= self.start_date:
            raise ValidationError("End date must be after start date.")
        
        # Check for overlapping seasonal pricing for same vehicle
        overlapping = SeasonalPricing.objects.filter(
            vehicle=self.vehicle,
            start_date__lt=self.end_date,
            end_date__gt=self.start_date
        ).exclude(pk=self.pk)
        
        if overlapping.exists():
            raise ValidationError("Seasonal pricing overlaps with existing pricing period.")
```

**Update Booking to Use Seasonal Pricing:**

```python
class Booking(models.Model):
    # ... existing fields ...
    
    def calculate_rental_cost(self):
        """Calculate cost considering seasonal pricing"""
        if not self.start_date or not self.end_date:
            return 0
        
        from datetime import timedelta
        
        total_cost = 0
        current_date = self.start_date.date()
        end_date = self.end_date.date()
        
        while current_date < end_date:
            # Check if there's seasonal pricing for this date
            seasonal = self.vehicle.seasonal_prices.filter(
                start_date__lte=current_date,
                end_date__gt=current_date
            ).first()
            
            daily_rate = seasonal.daily_rate if seasonal else self.vehicle.daily_rental_rate
            total_cost += daily_rate
            current_date += timedelta(days=1)
        
        return total_cost
```

---

### 6. Timestamps for All Models

**Why Important:**
- 🐛 **Debugging:** When was this record created?
- 📊 **Analytics:** How many bookings per month?
- 📝 **Auditing:** When was this vehicle last updated?

**Add to ALL models:**

```python
# Base mixin you can inherit from
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


# Then use it like:
class Vehicle(TimeStampedModel):
    # ... your fields ...
    pass

class Booking(TimeStampedModel):
    # ... your fields ...
    
    class Meta:
        ordering = ['-created_at']
```

**Or add manually to each model:**

```python
class Agency(models.Model):
    # ... existing fields ...
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

---

## Priority Action Items 📋

### 🔴 **Must Fix Immediately (Blocks Core Functionality)**

| # | Issue | Impact | Location |
|---|-------|--------|----------|
| 1 | Fix Vehicle `__str__` method | Crashes Django admin | Line 111 |
| 2 | Override `save()` to call `full_clean()` | Validation doesn't work | Booking model |
| 3 | Add date validation to `clean()` | Invalid bookings possible | Booking model |
| 4 | Auto-calculate `total_rental_cost` | Pricing errors | Booking model |

**Implementation Priority:** Fix in order listed above.

---

### 🟡 **Should Fix Soon (Quality & Reliability)**

| # | Issue | Impact | Effort |
|---|-------|--------|--------|
| 5 | Refactor role fields | Permission bugs | Medium |
| 6 | Add database indexes | Poor performance at scale | Low |
| 7 | Add atomic transactions | Race conditions | Medium |
| 8 | Add `VehicleImage` model | Core to UVP | Medium |

---

### 🟢 **Nice to Have (Enhanced Features)**

| # | Feature | Business Value | Effort |
|---|---------|----------------|--------|
| 9 | Add `Addon` model | Revenue opportunity | Medium |
| 10 | Add `Review` model | Trust & conversion | High |
| 11 | Add timestamps to all models | Debugging & analytics | Low |
| 12 | Add `SeasonalPricing` model | Competitive advantage | High |
| 13 | Add security deposit tracking | Trust & compliance | Low |

---

## Quick Fixes Code

### Complete `save()` Method for Booking

```python
class Booking(models.Model):
    # ... all your existing fields ...
    
    def calculate_rental_cost(self):
        """Calculate total cost based on rental duration and daily rate"""
        if self.start_date and self.end_date:
            days = (self.end_date - self.start_date).days
            if days <= 0:
                days = 1  # Minimum 1 day rental
            return self.vehicle.daily_rental_rate * days
        return 0
    
    def clean(self):
        from django.utils import timezone
        from datetime import timedelta
        
        # Validate dates exist
        if not self.start_date or not self.end_date:
            raise ValidationError("Both start and end dates are required.")
        
        # Validate end date is after start date
        if self.end_date <= self.start_date:
            raise ValidationError("End date must be after start date.")
        
        # Prevent bookings in the past
        if self.start_date < timezone.now():
            raise ValidationError("Cannot book dates in the past.")
        
        # Optional: Prevent bookings too far in advance
        max_advance_days = 365
        if self.start_date > timezone.now() + timedelta(days=max_advance_days):
            raise ValidationError(f"Bookings cannot be made more than {max_advance_days} days in advance.")
        
        # Check for overlapping bookings
        overlapping_bookings = Booking.objects.filter(
            vehicle=self.vehicle,
            start_date__lt=self.end_date,
            end_date__gt=self.start_date,
            booking_status__in=['PENDING', 'CONFIRMED']  # Only check active bookings
        ).exclude(pk=self.pk)

        if overlapping_bookings.exists():
            raise ValidationError("This vehicle is already booked for the selected dates.")
    
    def save(self, *args, **kwargs):
        # Auto-calculate cost if not set
        if not self.total_rental_cost:
            self.total_rental_cost = self.calculate_rental_cost()
        
        # Always run validation before saving
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Booking {self.id} by {self.user.username} for {self.vehicle.make}"
```

---

## Next Steps

1. **Fix critical issues** (Items 1-4 above)
2. **Run migrations** after model changes:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
3. **Test in Django Admin** - Verify `__str__` methods work
4. **Test booking overlap** - Try creating overlapping bookings
5. **Add VehicleImage model** - Critical for your visual-first UVP
6. **Plan for add-ons and reviews** - High business value features

---

## Resources

- [Django Model Validation](https://docs.djangoproject.com/en/stable/ref/models/instances/#validating-objects)
- [Database Transactions](https://docs.djangoproject.com/en/stable/topics/db/transactions/)
- [select_for_update](https://docs.djangoproject.com/en/stable/ref/models/querysets/#select-for-update)
- [Database Constraints](https://docs.djangoproject.com/en/stable/ref/models/constraints/)

---

**Questions or need help implementing?** Review this document and tackle the "Must Fix Immediately" items first!
