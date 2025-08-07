
# Register your models here.
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

# Unregister default admin first
admin.site.unregister(User)

# Create custom admin
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        ("Profile Info", {
            "fields": ("username", "password"),
        }),
        ("Contact Info", {
            "fields": ("first_name", "last_name", "email"),
        }),
        # ("Access Permissions", {
        #     "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
        # }),
        ("Access Permissions", {
            "fields": ("is_active",   "is_superuser"),
        }),
        ("Login Details", {
            "fields": ("last_login", "date_joined"),
        }),
    )

