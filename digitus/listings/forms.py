from django import forms
from django.forms import inlineformset_factory
from .models import Listing, ListingImage, Message, Comment
import re

class ListingForm(forms.ModelForm):
    """Formulaire pour créer ou modifier une annonce."""
    class Meta:
        model = Listing
        fields = ['title', 'description', 'price', 'category', 'listing_type']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring focus:ring-blue-200 focus:border-blue-600',
                'placeholder': 'Titre de l’annonce',
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring focus:ring-blue-200 focus:border-blue-600',
                'placeholder': 'Décrivez votre produit...',
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring focus:ring-blue-200 focus:border-blue-600',
                'placeholder': 'Prix',
                'step': '0.01',
            }),
            'category': forms.Select(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring focus:ring-blue-200 focus:border-blue-600',
            }),
            'listing_type': forms.Select(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring focus:ring-blue-200 focus:border-blue-600',
            }),
        }

class ListingImageForm(forms.ModelForm):
    """Formulaire pour ajouter ou modifier une image d'annonce."""
    class Meta:
        model = ListingImage
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring focus:ring-blue-200 focus:border-blue-600',
                'accept': 'image/*',
            }),
        }
    
    def clean_image(self):
        """Valide que l'image ne dépasse pas 5 Mo."""
        image = self.cleaned_data.get('image')
        if image and image.size > 800 * 1024 * 1024:  # 5 Mo
            raise forms.ValidationError("L'image ne doit pas dépasser 5 Mo.")
        return image

# Formset pour gérer plusieurs images d'une annonce
ListingImageFormSet = inlineformset_factory(
    Listing, ListingImage, form=ListingImageForm, extra=3, can_delete=True
)

class CheckoutForm(forms.Form):
    """Formulaire pour passer une commande depuis le panier."""
    first_name = forms.CharField(
        max_length=100,
        label='Prénom',
        widget=forms.TextInput(attrs={
            'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring focus:ring-blue-200 focus:border-blue-600',
            'placeholder': 'Entrez votre prénom',
        })
    )
    last_name = forms.CharField(
        max_length=100,
        label='Nom',
        widget=forms.TextInput(attrs={
            'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring focus:ring-blue-200 focus:border-blue-600',
            'placeholder': 'Entrez votre nom',
        })
    )
    phone = forms.CharField(
        max_length=20,
        label='Numéro de téléphone',
        widget=forms.TextInput(attrs={
            'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring focus:ring-blue-200 focus:border-blue-600',
            'placeholder': 'Ex: +2251234567890',
        })
    )
    neighborhood = forms.CharField(
        max_length=100,
        label='Quartier',
        widget=forms.TextInput(attrs={
            'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring focus:ring-blue-200 focus:border-blue-600',
            'placeholder': 'Entrez votre quartier',
        })
    )
    city = forms.CharField(
        max_length=100,
        label='Ville',
        widget=forms.TextInput(attrs={
            'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring focus:ring-blue-200 focus:border-blue-600',
            'placeholder': 'Entrez votre ville',
        })
    )

    def clean_first_name(self):
        """Valide que le prénom contient uniquement des lettres et des espaces."""
        first_name = self.cleaned_data['first_name']
        if not re.match(r'^[A-Za-z\s\-]+$', first_name):
            raise forms.ValidationError("Le prénom ne doit contenir que des lettres, des espaces ou des tirets.")
        return first_name.strip()

    def clean_last_name(self):
        """Valide que le nom contient uniquement des lettres et des espaces."""
        last_name = self.cleaned_data['last_name']
        if not re.match(r'^[A-Za-z\s\-]+$', last_name):
            raise forms.ValidationError("Le nom ne doit contenir que des lettres, des espaces ou des tirets.")
        return last_name.strip()

    def clean_phone(self):
        """Valide que le numéro de téléphone a un format correct."""
        phone = self.cleaned_data['phone']
        if not re.match(r'^\+?\d{8,10}$', phone):
            raise forms.ValidationError("Veuillez entrer un numéro de téléphone valide (ex: +2251234567890 ou 12345678).")
        return phone.strip()

class MessageForm(forms.ModelForm):
    """Formulaire pour envoyer un message à un vendeur."""
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring focus:ring-blue-200 focus:border-blue-600',
                'placeholder': 'Écrivez votre message...',
                'rows': 4,
            }),
        }

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content.strip()) < 5:
            raise forms.ValidationError("Le message doit contenir au moins 5 caractères.")
        return content.strip()

class CommentForm(forms.ModelForm):
    """Formulaire pour ajouter un commentaire/avis sur une annonce."""
    class Meta:
        model = Comment
        fields = ['content', 'rating']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring focus:ring-blue-200 focus:border-blue-600',
                'placeholder': 'Laissez votre commentaire...',
                'rows': 4,
            }),
            'rating': forms.Select(
                choices=[(i, f"{i} étoile{'s' if i > 1 else ''}") for i in range(1, 6)],
                attrs={
                    'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring focus:ring-blue-200 focus:border-blue-600',
                }
            ),
        }

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content.strip()) < 5:
            raise forms.ValidationError("Le commentaire doit contenir au moins 5 caractères.")
        return content.strip()