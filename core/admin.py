from django.contrib import admin
from .models import Agency, AgencyMember

@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ('agency_name', 'user', 'city', 'phone_number', 'is_verified')

@admin.register(AgencyMember)
class AgencyMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'agency', 'joined_at', 'is_active')
