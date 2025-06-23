from django.contrib import admin
from users.models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'masked_email', 'role', 'is_active', 'is_staff')
    search_fields = ('username',)
    list_filter = ('role', 'is_active', 'is_staff')
    ordering = ('username',)

    def masked_email(self, obj):
        try:
            return f"{obj.email[:2]}***@***"
        except:
            return "N/A"
    masked_email.short_description = 'Email'

    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Permissions', {
            'fields': ('role', 'is_active', 'is_staff')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'role')}
        ),
    )
