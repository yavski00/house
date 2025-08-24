#listings/models.py
from django.db import models
from django.contrib.auth.models import User
from comptes.models import UserProfile

class Listing(models.Model):
    TYPE_CHOICES = (
        ('sale', 'Vente'),
        ('rent', 'Location'),
    )
    CATEGORY_CHOICES = (
        ('land', 'Terrain'),
        ('house_sale', 'Maison (Vente)'),
        ('house_rent', 'Maison (Location)'),
    ) 

    title = models.CharField(max_length=200) 
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    listing_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True) 

    def __str__(self):
        return self.title    

    class Meta:
        ordering = ['-created_at']

class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='annonce/', null=True, blank=True)

    def __str__(self):
        return f"Image pour {self.listing.title}"

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('cancelled', 'Annulée'),
    )
    buyer = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    neighborhood = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commande {self.id} - {self.listing.title}" 

class SiteTraffic(models.Model):
    date = models.DateField(auto_now_add=True)
    visitors = models.PositiveIntegerField(default=0)  
    page_views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Trafic du {self.date}"



class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message de {self.sender} à {self.recipient} pour {self.listing.title}"

    class Meta:
        ordering = ['timestamp']

class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    rating = models.IntegerField(choices=[(i, f"{i} étoile{'s' if i > 1 else ''}") for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commentaire de {self.user.username} sur {self.listing.title}"

    class Meta:
        ordering = ['-created_at']
        
        
