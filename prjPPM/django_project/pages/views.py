from django.shortcuts import render, redirect
from .forms import CreateUserForm, LoginForm, UpdateProfileForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# - Authentcation models and functions

from django.contrib.auth.models import auth
from django.contrib.auth import authenticate, login, logout




def homePageView(request):
    return render(request, 'pages/index.html')


def register(request):
    if request.user.is_authenticated:  # reindirizza l'utente se è già autenticato
        return redirect("")

    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()  # pushes data to database
            return redirect("my-login")

    context = {'registerform': form}
    return render(request, 'pages/register.html', context=context)


def my_login(request):
    if request.user.is_authenticated:  # reindirizza l'utente se è già autenticato
        return redirect("")  # o la tua vista di default

    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect("")  # o la tua vista di default
            else:
                messages.error(request, "Credenziali non valide. Per favore, riprova.")
        else:
            messages.error(request, "Errore nel modulo di login. Controlla i dati inseriti.")

    context = {'loginform': form}
    return render(request, 'pages/my-login.html', context=context)


def user_logout(request):
    auth.logout(request)
    return redirect("")


@login_required(login_url="my-login")
def dashboard(request):
    return render(request, 'pages/dashboard.html')


@login_required
def my_profile(request):
    if request.method == 'POST':
        form = UpdateProfileForm(request.POST, request.FILES,  instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("my-profile")
    else:
        form = UpdateProfileForm(instance=request.user)
    return render(request, 'pages/my-profile.html', {'form': form})

