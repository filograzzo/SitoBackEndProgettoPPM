from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CreateUserForm, LoginForm, UpdateProfileForm, RecipeCreateForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Recipe
from django.views.generic import ListView

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


class Recipes(ListView):
    """View all recipes"""
    template_name = 'pages/index.html'
    model = Recipe
    context_object_name = 'recipes'

    def get_queryset(self):
        return Recipe.objects.all()


class LikedRecipes(ListView):
    """View all liked recipes"""
    template_name = 'pages/my-likes.html'
    model = Recipe
    context_object_name = 'liked_recipes'

    def get_queryset(self):
        return Recipe.objects.filter(likes=self.request.user)


@login_required(login_url="my-login")
def dashboard(request):
    return render(request, 'pages/dashboard.html')


@login_required
def my_profile(request):
    if request.method == 'POST':
        form = UpdateProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("my-profile")
    else:
        form = UpdateProfileForm(instance=request.user)
    return render(request, 'pages/my-profile.html', {'form': form})


@login_required
def recipe_creation(request):
    if request.method == 'POST':
        form = RecipeCreateForm(request.POST,
                                request.FILES)  # Passa anche request.FILES per gestire l'upload dell'immagine
        if form.is_valid():
            new_recipe = form.save(commit=False)
            new_recipe.user = request.user
            new_recipe.save()
            return redirect('my-profile')  # Reindirizza a una view dopo il salvataggio della ricetta
    else:
        form = RecipeCreateForm()

    context = {'form': form}
    template = 'pages/recipe-creation.html'
    return render(request, template, context)


@login_required
def delete_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    # Verifica se l'utente che sta cercando di eliminare la ricetta è anche il creatore della ricetta
    if request.user == recipe.user:
        if request.method == 'POST':
            recipe.delete()
            return redirect('my-profile')  # Reindirizza dopo l'eliminazione della ricetta

        # Se non è una richiesta POST, potresti anche gestire un altro comportamento (ad esempio un messaggio di errore)
        # Ma normalmente non dovrebbe accadere se il form è correttamente configurato
        return redirect('my-profile')
    else:
        # Se l'utente non è autorizzato, puoi reindirizzarlo o mostrare un messaggio di errore
        # In questo caso, reindirizziamo alla pagina di profilo
        return redirect('my-profile')


@login_required
def edit_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    # Verifica se l'utente che sta cercando di modificare la ricetta è anche il creatore della ricetta
    if request.user == recipe.user:
        if request.method == 'POST':
            form = RecipeCreateForm(request.POST, request.FILES, instance=recipe)
            if form.is_valid():
                form.save()
                return redirect('my-profile')  # Reindirizza dopo la modifica della ricetta
        else:
            form = RecipeCreateForm(instance=recipe)

        # Passa il form al template per visualizzare il form di modifica
        context = {
            'form': form,
            'recipe': recipe,
        }
        return render(request, 'pages/edit-recipe.html', context)
    else:
        # Se l'utente non è autorizzato, puoi reindirizzarlo o mostrare un messaggio di errore
        # In questo caso, reindirizziamo alla pagina di profilo
        return redirect('my-profile')


def recipe_search(request):
    query = request.GET.get('q')
    if query:
        recipes = Recipe.objects.filter(title__icontains=query)
    else:
        recipes = Recipe.objects.all()
    return render(request, 'pages/index.html', {'recipes': recipes})


@login_required
def like_recipe(request, recipe_id):
    if request.method == 'POST':
        recipe = Recipe.objects.get(id=recipe_id)
        if request.user in recipe.likes.all():
            recipe.likes.remove(request.user)
            liked = False
        else:
            recipe.likes.add(request.user)
            liked = True
        return JsonResponse({'success': True, 'liked': liked})
    return JsonResponse({'success': False})
