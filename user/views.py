import re
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import User


# Create your views here.
def login_view(request):
    if request.method == "POST":
        username_or_email = request.POST["username_or_email"]
        password = request.POST["password"]

        is_email = re.fullmatch(r"[^@]+@[^@]+\.[^@]+", username_or_email)

        if is_email:
            email = username_or_email
            user = authenticate(request, email=email, password=password)
        else:
            username = username_or_email
            user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("lock:locks")
        else:
            return render(request, "user/login.html")

    return render(request, "user/login.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect("user:login")


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if len(password) < 4 or password != confirm_password:
            return render(request, "user/register.html", {
                "error": "Password must be at least 4 characters long with 1 uppercase letter \
                                     and match the confirm password field."
            }, status=200)

        valid_email = re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email)
        valid_username = re.fullmatch(r"^[a-zA-Z\d]+$", username)

        valid_name = re.fullmatch(r"^[a-zA-Z\d]+$", first_name) and re.fullmatch(r"^[a-zA-Z\d]+$", last_name)
        if valid_email and valid_username and valid_name:

            try:
                user = User.objects.create_user(
                    username=username, password=password, email=email,
                    first_name=first_name, last_name=last_name
                )
                user.save()

            except IntegrityError:
                return render(request, "user/register.html", {
                    "error": "Username or email already exists."
                }, status=200)

            login(request, user)
            return redirect("user:login")

        else:
            return render(request, "user/register.html", {
                "error": "Your name, username and email must be valid."
            }, status=200)

    return render(request, "user/register.html")
