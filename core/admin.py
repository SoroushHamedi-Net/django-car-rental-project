from django.contrib import admin
from .models import NotificationLog


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'channel', 'subject', 'is_sent', 'created_at')
    list_filter = ('channel', 'is_sent', 'created_at')
    search_fields = ('recipient__username', 'recipient__phone_number', 'subject', 'message')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
