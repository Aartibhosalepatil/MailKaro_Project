"""
URL configuration for my_email_client project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# from .views import home_view
from .views import home_redirect

from users.views import custom_login_view  # import your view

urlpatterns = [
    # path('',home_view,name='home'),
    path('', home_redirect),   
    path('admin/login/', custom_login_view),  
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),  
    path('mail/', include('mail.urls')),
    # path('notifications/', include('notifications.urls')),
]





# This is useful to create and store all the files that end user uploaded kept in this media folder

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

