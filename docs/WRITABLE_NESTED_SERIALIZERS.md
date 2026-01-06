# Writable Nested Serializers in Django Rest Framework (DRF) 🛠️

In this project, we updated the `VehicleDetailSerializer` to allow creating and updating a **Vehicle** along with its **Specifications** in a single API request. This guide explains the "What, Why, and How" of this implementation.

---

## 1. The Challenge: Nested Relationships
By default, DRF serializers treat nested relationships as **Read-Only**.

If you have a `Vehicle` that HAS ONE `VehicleSpecs`, and you provide a JSON like this:
```json
{
  "make": "Tesla",
  "specs": {
    "transmission": "AUTOMATIC",
    "fuel_type": "ELECTRIC"
  }
}
```
DRF's default `create()` method will fail because it doesn't know how to handle the `specs` dictionary. It expects only simple fields that exist directly on the `Vehicle` model.

---

## 2. Our Solution: A 3-Step Process

### Step A: Make the Nested Field Writable
In `vehicles/serializers.py`, we removed `read_only=True` from the `specs` field:

```python
class VehicleDetailSerializer(serializers.ModelSerializer):
    # Before: specs = VehicleSpecsSerializer(read_only=True)
    # After:
    specs = VehicleSpecsSerializer(required=True)
```

### Step B: Overriding `create()`
We manually handle the data separation. We "pop" the nested data out before saving the main model.

```python
def create(self, validated_data):
    # 1. Extract (pop) the nested specs data
    specs_data = validated_data.pop('specs')
    
    # 2. Assign the agency (Business Logic)
    validated_data['owner_agency'] = self.context['request'].user.agency
    
    # 3. Create the parent Vehicle
    vehicle = Vehicle.objects.create(**validated_data)
    
    # 4. Create the child Specs linked to the new vehicle
    VehicleSpecs.objects.create(vehicle=vehicle, **specs_data)
    
    return vehicle
```

### Step C: Overriding `update()`
For updates, we update existing objects instead of creating new ones.

```python
def update(self, instance, validated_data):
    # 1. Pop the specs data
    specs_data = validated_data.pop('specs', None)
    
    if specs_data:
        # 2. Get the existing specs object for this vehicle
        specs_instance, created = VehicleSpecs.objects.get_or_create(vehicle=instance)
        
        # 3. Update fields on the specs object
        for attr, value in specs_data.items():
            setattr(specs_instance, attr, value)
        specs_instance.save()
        
    # 4. Use super() to handle standard vehicle field updates
    return super().update(instance, validated_data)
```

---

## 3. Best Practices to Remember
1. **Atoms/Transactions**: In production, wrap the `create()` logic in `transaction.atomic` to ensure that if the Specs creation fails, the Vehicle creation is also rolled back.
2. **Safety Checks**: Always verify that the user has the permissions to create/link these objects (e.g., checking `hasattr(user, 'agency')`).
3. **get_or_create**: When updating, use `get_or_create` for the child object. This handles cases where a main object might have been created without its specifications previously.

---

## 📄 Summary
By overriding these methods, you gain full control over how complex data structures are preserved in your database, providing a much smoother experience for frontend developers.
