from django.contrib import admin
from .models import Email,Attachment

@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('subject', 'from_email', 'timestamp','user')
    list_per_page = 10

@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('email','filename','file')

