from django.urls import path
from .views import signup_view,user_dashboard,login_view
from django.contrib.auth import views as auth_views
urlpatterns = [

    path('signup/', signup_view, name='signup'),
    path('login/',login_view,name='login'),
    path('logout/',auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    # path('dashboard/',user_dashboard,name='user_dashboard'),
]

