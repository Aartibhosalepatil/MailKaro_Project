from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm
from django.contrib import messages


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # return redirect('mail:inbox')  # you can change this as needed
    else:
        form = SignUpForm()
    return render(request, 'users/signup.html', {'form': form})



def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if user.is_superuser:
                return redirect('/admin/mail/email')  # redirect admin to admin site
            else:
                return redirect('inbox')  # normal user
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})


def custom_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user:     # redirect based on user type
            login(request, user)
            if user.is_superuser or user.is_staff:
                return redirect('/admin/mail/email/')  # Redirect to Emails page
            else:
                return redirect('user_dashboard')  # non-staff user
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'login.html')


@login_required
def user_dashboard(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect('/admin/mail/email/')
    return render(request, 'user_dashboard.html')
