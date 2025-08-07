# This file contains all the urls related to the mail app --->> for accessing any url use 127.0.0.8000/mail/inbox/ like this

from django.urls import path
from .views import (
    inbox_view, compose_view, message_detail_view,
    sent_mail_view, eml_upload_view, download_attachment,delete_email_view
)

urlpatterns = [
    path('inbox/', inbox_view, name='inbox'),
    path('compose/', compose_view, name='compose'), 
    path('message/<str:type>/<int:email_id>/', message_detail_view, name='message_detail'),
    path('sent/', sent_mail_view, name='sent'),
    path('eml_upload/',eml_upload_view, name='eml_upload'),
    path('download_attachment/<int:attachment_id>/',download_attachment,name='download_attachment'),
    path('delete_email/<int:email_id>/',delete_email_view,name='delete_email'),
]
