from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile, OneTimePassword

# Define a custom admin class for the User model
class CustomUserAdmin(UserAdmin):
    list_display = ('id','email', 'first_name', 'last_name', 'is_staff', 'profile_picture','is_active', 'is_superuser', 'is_verified', 'get_groups_display', 'auth_provider')
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'is_verified')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups')}),
        ('Important dates', {'fields': ('last_login', 'created_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)

    def get_groups_display(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])

    get_groups_display.short_description = 'Groups'

# Register the models and custom admin classes
admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile)
admin.site.register(OneTimePassword)












