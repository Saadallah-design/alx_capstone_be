import os
import django
from datetime import time

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carRentalConfig.settings')
django.setup()

from users.models import User
from core.models import Agency
from branches.models import Branch
from vehicles.models import Vehicle, VehicleSpecs

def seed_mock_data():
    print("🚀 Starting full data seeding...")
    
    # 1. Define Mock Agencies and Their Admins
    agency_configs = [
        {
            "username": "rabat_admin",
            "email": "admin@rabat-rentals.com",
            "agency_name": "Rabat Car Services",
            "city": "PHUKET_TOWN",
            "address": "45 Rabat Street, Phuket",
            "license": "LIC-RABAT-001"
        },
        {
            "username": "patong_admin",
            "email": "admin@patong-rentals.com",
            "agency_name": "Patong Premium Rentals",
            "city": "PATONG",
            "address": "12 Banana Walk, Patong",
            "license": "LIC-PATONG-999"
        },
        {
            "username": "eco_admin",
            "email": "admin@eco-drive.com",
            "agency_name": "Eco Drive Phuket",
            "city": "BANG_TAO",
            "address": "Eco Plaza, Bang Tao",
            "license": "LIC-ECO-555"
        }
    ]

    for config in agency_configs:
        print(f"\n🏢 Processing Agency: {config['agency_name']}")
        
        # Create/Get User
        user, u_created = User.objects.get_or_create(
            username=config["username"],
            defaults={
                "email": config["email"],
                "role": "AGENCY_ADMIN",
                "first_name": config["agency_name"].split()[0],
                "last_name": "Admin",
                "is_staff": True # Allow admin access for testing
            }
        )
        if u_created:
            user.set_password("password123")
            user.save()
            print(f"   ✅ Created User: {user.username}")
        else:
            print(f"   ℹ️ User already exists: {user.username}")

        # Create/Get Agency Profile
        agency, a_created = Agency.objects.get_or_create(
            user=user,
            defaults={
                "agency_name": config["agency_name"],
                "address": config["address"],
                "contact_email": config["email"],
                "phone_number": "081-000-1111",
                "license_number": config["license"],
                "city": config["city"],
                "is_verified": True
            }
        )
        if a_created:
            print(f"   ✅ Created Agency: {agency.agency_name}")
        else:
            print(f"   ℹ️ Agency already exists: {agency.agency_name}")

        # 2. Create Branches for this Agency
        branch_data = [
            {
                "name": f"{agency.agency_name} - Main Branch",
                "phone_number": "081-123-4567",
                "email": f"main@{config['username']}.com",
                "city": agency.city,
                "address": agency.address,
                "country": "Thailand",
                "latitude": 7.884,
                "longitude": 98.391,
                "opening_time": time(8, 0),
                "closing_time": time(22, 0),
                "is_pickup_point": True,
                "is_dropoff_point": True
            },
            {
                "name": f"{agency.agency_name} - Waterfront",
                "phone_number": "081-987-6543",
                "email": f"waterfront@{config['username']}.com",
                "city": agency.city,
                "address": "Pier 9, Phuket Coast",
                "country": "Thailand",
                "latitude": 7.850,
                "longitude": 98.400,
                "opening_time": time(9, 0),
                "closing_time": time(20, 0),
                "is_pickup_point": True,
                "is_dropoff_point": True
            }
        ]

        for b_info in branch_data:
            branch, b_created = Branch.objects.get_or_create(
                name=b_info["name"],
                agency=agency,
                defaults=b_info
            )
            if b_created:
                print(f"   ✅ Created Branch: {branch.name}")
            else:
                print(f"   ℹ️ Branch already exists: {branch.name}")

            # 3. Create Vehicles for this Branch
            vehicles = [
                {"make": "Toyota", "model": "Yaris", "type": "CAR", "rate": 1000.0, "plate": f"{branch.id}-ABC"},
                {"make": "Honda", "model": "PCX", "type": "SCOOTER", "rate": 400.0, "plate": f"{branch.id}-XYZ"}
            ]

            for v_info in vehicles:
                vehicle, v_created = Vehicle.objects.get_or_create(
                    licence_plate=v_info["plate"],
                    defaults={
                        "owner_agency": agency,
                        "current_location": branch,
                        "make": v_info["make"],
                        "model": v_info["model"],
                        "year": 2023,
                        "vehicle_type": v_info["type"],
                        "daily_rental_rate": v_info["rate"],
                        "status": "AVAILABLE"
                    }
                )
                if v_created:
                    print(f"      🚗 Created {v_info['make']} {v_info['model']}")
                    VehicleSpecs.objects.create(
                        vehicle=vehicle,
                        transmission="AUTOMATIC",
                        fuel_type="PETROL",
                        seats=5 if v_info["type"] == "CAR" else 2,
                        is_air_conditioned=True if v_info["type"] == "CAR" else False
                    )

    print("\n🎉 Full Seeding Complete!")

if __name__ == "__main__":
    seed_mock_data()
