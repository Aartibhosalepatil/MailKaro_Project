from django.contrib import admin
from .models import Email,Attachment

@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('subject', 'from_email', 'to','timestamp','user','email_type')
    list_per_page = 10
    search_fields = ('subject', 'from_email', 'to')
    list_filter = ('email_type', 'timestamp')


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('email','filename','file')
    list_filter = ('email__user', 'email__timestamp')

