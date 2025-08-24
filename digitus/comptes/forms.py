from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from comptes.models import UserProfile

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-600 transition duration-200',
            'placeholder': 'Entrez votre adresse email',
        })
    )
    user_type = forms.ChoiceField(
        choices=UserProfile.USER_TYPE_CHOICES,
        required=True,
        label="Type d'utilisateur",
        widget=forms.Select(attrs={
            'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-600 transition duration-200 bg-white',
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'user_type', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-600 transition duration-200',
                'placeholder': 'Entrez votre nom d’utilisateur',
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'w-full p-3 border-2 border-gray-500 rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-600 transition duration-200 outline-none',
                'placeholder': 'Entrez votre mot de passe',
                'style': 'border: 2px solid #6B7280 !important; box-shadow: 0 0 0 1px #6B7280 !important;'
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'w-full p-3 border-2 border-gray-500 rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-600 transition duration-200 outline-none',
                'placeholder': 'Confirmez votre mot de passe',
                'style': 'border: 2px solid #6B7280 !important; box-shadow: 0 0 0 1px #6B7280 !important;'
            }),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            UserProfile.objects.create(user=user, user_type=self.cleaned_data['user_type'])
        return user

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring focus:ring-blue-200 focus:border-blue-600',
        'placeholder': 'Nom d’utilisateur',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring focus:ring-blue-200 focus:border-blue-600',
        'placeholder': 'Mot de passe',
    }))

