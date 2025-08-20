# This file contains all the urls related to the mail app --->> for accessing any url use 127.0.0.8000/mail/inbox/ like this

from django.urls import path
from mail import views
# from .views import (
#     inbox_view, compose_view, message_detail_view,
#     sent_mail_view, eml_upload_view, download_attachment,delete_email_view
# )

urlpatterns = [
    path('inbox/', views.inbox_view, name='inbox'),
    path('message/<str:type>/<int:email_id>/', views.message_detail_view, name='message_detail'),
    path('compose/', views.compose_view, name='compose'),
     path("sent/", views.sent_mail_view, name="sent"),   
    path('eml_upload/',views.eml_upload_view, name='eml_upload'),
    path('download_attachment/<int:attachment_id>/',views.download_attachment,name='download_attachment'),
    path('delete_email/<int:email_id>/',views.delete_email_view,name='delete_email'),
    
]

