from django.contrib import admin, messages
from .models import Agency, AgencyMember

@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ('agency_name', 'user', 'city', 'phone_number', 'is_verified', 'submitted_on')
    list_filter = ('is_verified', 'city')
    search_fields = ('agency_name', 'user__username', 'contact_email')
    actions = ['verify_agencies']

    @admin.action(description="Verify selected agencies and upgrade owners to Agency Admin")
    def verify_agencies(self, request, queryset):
        for agency in queryset:
            if not agency.is_verified:
                # 1. Verify the agency
                agency.is_verified = True
                agency.save()
                
                # 2. Upgrade the user's role
                user = agency.user
                user.role = 'AGENCY_ADMIN'
                user.save()
                
        self.message_user(
            request, 
            "Selected agencies have been verified and owners upgraded to Agency Admin.",
            messages.SUCCESS
        )

@admin.register(AgencyMember)
class AgencyMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'agency', 'joined_at', 'is_active')
    list_filter = ('agency', 'is_active')
