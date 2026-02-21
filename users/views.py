from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import CustomUserCreationForm
from django.contrib.auth.models import User


def register_view(request):
    # users/views.py
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # ✅ go to login page
    else:
        form = CustomUserCreationForm()

    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    """
    Custom login using EMAIL 
    """
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            return render(request, 'users/login.html', {
                "error": "Invalid email or password"
            })

        user = authenticate(request, 
                            username=username, 
                            password=password
                        )   

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'users/login.html', {
                "error": "Invalid email or password"
            })

    return render(request, 'users/login.html')



def logout_view(request):
    logout(request)
    return redirect('login')