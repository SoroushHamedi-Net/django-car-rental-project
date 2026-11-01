from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, VerificationToken


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 'get_full_name', 'phone_number', 'role',
        'is_email_verified', 'is_phone_verified', 'is_staff'
    )
    list_filter = ('role', 'is_email_verified', 'is_phone_verified', 'is_staff', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'phone_number', 'national_code', 'email')
    ordering = ('-date_joined',)

    fieldsets = UserAdmin.fieldsets + (
        ('اطلاعات تکمیلی و نقش در سامانه', {
            'fields': ('role', 'phone_number', 'national_code', 'is_email_verified', 'is_phone_verified')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('اطلاعات اولیه نقش و تماس', {
            'fields': ('role', 'phone_number', 'national_code')
        }),
    )


@admin.register(VerificationToken)
class VerificationTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'token_type', 'is_used', 'created_at', 'expires_at')
    list_filter = ('token_type', 'is_used', 'created_at')
    search_fields = ('user__username', 'user__phone_number', 'token')
    readonly_fields = ('created_at',)
