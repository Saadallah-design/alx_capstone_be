from django.core.management.base import BaseCommand
from datetime import time
from django.utils.text import slugify
from users.models import User
from core.models import Agency
from branches.models import Branch
from vehicles.models import Vehicle, VehicleSpecs

class Command(BaseCommand):
    help = 'Seeds mock data for Agencies, Branches, and Vehicles'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("🚀 Starting full data seeding..."))
        
        # 1. Define Mock Agencies and Their Admins
        agency_configs = [
            {
                "username": "rawai_admin",
                "email": "admin@rawai-rentals.com",
                "agency_name": "Rawai Car Services",
                "city": "PHUKET_TOWN",
                "address": "45 Rawai Street, Phuket",
                "license": "LIC-RAWAI-001"
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
            self.stdout.write(f"\n🏢 Processing Agency: {config['agency_name']}")
            
            # Create/Get User
            user, u_created = User.objects.get_or_create(
                username=config["username"],
                defaults={
                    "email": config["email"],
                    "role": "AGENCY_ADMIN",
                    "first_name": config["agency_name"].split()[0],
                    "last_name": "Admin",
                    "is_staff": True
                }
            )
            if u_created:
                user.set_password("password123")
                user.save()
                self.stdout.write(self.style.SUCCESS(f"   ✅ Created User: {user.username}"))
            else:
                self.stdout.write(f"   ℹ️ User already exists: {user.username}")

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
                self.stdout.write(self.style.SUCCESS(f"   ✅ Created Agency: {agency.agency_name}"))
            else:
                self.stdout.write(f"   ℹ️ Agency already exists: {agency.agency_name}")

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
                    self.stdout.write(self.style.SUCCESS(f"   ✅ Created Branch: {branch.name}"))
                else:
                    self.stdout.write(f"   ℹ️ Branch already exists: {branch.name}")

                # 3. Create Vehicles for this Branch
                vehicles = [
                    {"make": "Toyota", "model": "Yaris", "type": "CAR", "rate": 1000.0, "plate": f"PLATE-{branch.id}-YARIS"},
                    {"make": "Honda", "model": "PCX", "type": "SCOOTER", "rate": 400.0, "plate": f"PLATE-{branch.id}-PCX"}
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
                        self.stdout.write(self.style.SUCCESS(f"      🚗 Created {v_info['make']} {v_info['model']}"))
                        VehicleSpecs.objects.create(
                            vehicle=vehicle,
                            transmission="AUTOMATIC",
                            fuel_type="PETROL",
                            seats=5 if v_info["type"] == "CAR" else 2,
                            is_air_conditioned=True if v_info["type"] == "CAR" else False
                        )

        self.stdout.write(self.style.SUCCESS("\n🎉 Full Seeding Complete!"))
