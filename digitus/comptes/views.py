from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from .forms import RegistrationForm, LoginForm
from comptes.models import UserProfile
import logging

logger = logging.getLogger(__name__)

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid(): 
            user = form.save()
            messages.success(request, 'Inscription réussie ! Vous pouvez maintenant vous connecter.')
            logger.info(f"Inscription réussie pour {form.cleaned_data['username']}")
            return redirect('login')
        else:
            logger.error(f"Erreur d'inscription : {form.errors.as_data()}")
            messages.error(request, 'Erreur lors de l’inscription. Veuillez corriger les champs.')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                logger.info(f"Utilisateur {username} connecté avec succès")
                if user.is_superuser:
                    messages.success(request, "Connexion réussie en tant qu'administrateur !")
                    return redirect('admin_dashboard')
                try:
                    profile = user.userprofile
                    messages.success(request, f"Connexion réussie en tant que {profile.user_type} !")
                    if profile.user_type == 'buyer':
                        return redirect('buyer_dashboard')
                    elif profile.user_type == 'seller':
                        return redirect('seller_dashboard')
                except UserProfile.DoesNotExist:
                    logger.error(f"Utilisateur {username} n'a pas de profil UserProfile")
                    messages.error(request, "Profil utilisateur manquant. Contactez l’administrateur.")
                    return redirect('home')
            else:
                messages.error(request, 'Nom d’utilisateur ou mot de passe incorrect.')
                logger.warning(f"Échec de l'authentification pour {username}")
        else:
            logger.error(f"Formulaire de connexion invalide : {form.errors}")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    messages.success(request, 'Déconnexion réussie !')
    logger.info("Déconnexion réussie")
    return redirect('login')

def home(request):
    try:
        profile = request.user.userprofile
        user_type = profile.user_type
    except (UserProfile.DoesNotExist, AttributeError):
        user_type = None
    return render(request, 'home.html', {
        'message': 'Bienvenue sur Digitus Market',
        'user_type': user_type,
    })
    


