
#listings/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from .models import Listing, Order, SiteTraffic
from .forms import ListingForm, ListingImageFormSet, CheckoutForm
from comptes.models import UserProfile
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

def check_seller(user):  
    try:
        profile = user.userprofile
        return profile.user_type == 'seller'
    except UserProfile.DoesNotExist:
        logger.error(f"Utilisateur {user.username} n'a pas de profil UserProfile")
        return False

def check_buyer(user):
    try:
        profile = user.userprofile
        return profile.user_type == 'buyer'
    except UserProfile.DoesNotExist:
        logger.error(f"Utilisateur {user.username} n'a pas de profil UserProfile")
        return False

@login_required
def create_listing(request):
    if not check_seller(request.user):
        messages.error(request, "Seuls les vendeurs peuvent créer des annonces.")
        logger.warning(f"Utilisateur {request.user.username} non autorisé à créer une annonce")
        return redirect('listing_list')
    
    if request.method == 'POST':
        form = ListingForm(request.POST)
        formset = ListingImageFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            listing = form.save(commit=False)
            listing.user = request.user
            listing.save()
            formset.instance = listing
            formset.save()
            messages.success(request, 'Annonce créée avec succès !')
            logger.info(f"Annonce {listing.title} créée par {request.user.username}")
            return redirect('listing_list')
        else:
            logger.error(f"Erreur lors de la création de l'annonce : {form.errors}, {formset.errors}")
    else:
        form = ListingForm()
        formset = ListingImageFormSet()
    return render(request, 'listings/create.html', {'form': form, 'formset': formset})

@login_required
def edit_listing(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    if listing.user != request.user or not check_seller(request.user):
        messages.error(request, "Vous n'êtes pas autorisé à modifier cette annonce.")
        logger.warning(f"Utilisateur {request.user.username} non autorisé à modifier l'annonce {listing.title}")
        return redirect('listing_list')
    
    if request.method == 'POST':
        form = ListingForm(request.POST, instance=listing)
        formset = ListingImageFormSet(request.POST, request.FILES, instance=listing)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Annonce modifiée avec succès !')
            logger.info(f"Annonce {listing.title} modifiée par {request.user.username}")
            return redirect('listing_detail', pk=listing.pk)
        else:
            logger.error(f"Erreur lors de la modification de l'annonce : {form.errors}, {formset.errors}")
    else:
        form = ListingForm(instance=listing)
        formset = ListingImageFormSet(instance=listing)
    return render(request, 'listings/edit.html', {'form': form, 'formset': formset, 'listing': listing})

@login_required
def delete_listing(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    if listing.user != request.user or not check_seller(request.user):
        messages.error(request, "Vous n'êtes pas autorisé à supprimer cette annonce.")
        logger.warning(f"Utilisateur {request.user.username} non autorisé à supprimer l'annonce {listing.title}")
        return redirect('listing_list')
    
    if request.method == 'POST':
        listing.delete()
        messages.success(request, 'Annonce supprimée avec succès !')
        logger.info(f"Annonce {listing.title} supprimée par {request.user.username}")
        return redirect('listing_list')
    return render(request, 'listings/delete.html', {'listing': listing})

def listing_list(request):
    listings = Listing.objects.filter(is_active=True)
    category = request.GET.get('category', '')
    listing_type = request.GET.get('listing_type', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    
    if category:
        listings = listings.filter(category=category)
    if listing_type:
        listings = listings.filter(listing_type=listing_type)
    if min_price:
        try:
            listings = listings.filter(price__gte=float(min_price))
        except ValueError:
            messages.error(request, 'Prix minimum invalide.')
    if max_price:
        try:
            listings = listings.filter(price__lte=float(max_price))
        except ValueError:
            messages.error(request, 'Prix maximum invalide.')
    
    context = {
        'listings': listings,
        'categories': Listing.CATEGORY_CHOICES,
        'listing_types': Listing.TYPE_CHOICES,
        'selected_category': category,
        'selected_type': listing_type,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'listings/list.html', context)

def listing_detail(request, pk):
    listing = get_object_or_404(Listing, pk=pk, is_active=True)
    return render(request, 'listings/detail.html', {'listing': listing})

@login_required
def add_to_cart(request, listing_id):
    if request.method == 'POST':
        if not check_buyer(request.user):
            messages.error(request, "Seuls les acheteurs peuvent ajouter au panier.")
            logger.warning(f"Utilisateur {request.user.username} non autorisé à ajouter au panier")
            return redirect(request.POST.get('next', 'listing_list'))
        
        try:
            listing = Listing.objects.get(pk=listing_id, is_active=True)
            if listing.user == request.user:
                messages.error(request, "Vous ne pouvez pas ajouter votre propre produit au panier.")
                logger.warning(f"Utilisateur {request.user.username} a tenté d'ajouter son propre produit {listing.title}")
                return redirect(request.POST.get('next', 'listing_list'))
            
            image_url = listing.images.first().image.url if listing.images.exists() else ''
            request.session['cart'] = {
                str(listing_id): {
                    'title': listing.title,
                    'price': str(listing.price),
                    'image_url': image_url,
                }
            }
            request.session.modified = True
            messages.success(request, f"{listing.title} a été ajouté au panier !")
            logger.info(f"Annonce {listing.title} ajoutée au panier par {request.user.username}")
        except Listing.DoesNotExist:
            messages.error(request, "Annonce introuvable.")
            logger.error(f"Annonce ID {listing_id} introuvable")
        
        return redirect(request.POST.get('next', 'listing_list'))
    return redirect('listing_list')

@login_required
def view_cart(request):
    if not check_buyer(request.user):
        messages.error(request, "Seuls les acheteurs peuvent voir le panier.")
        logger.warning(f"Utilisateur {request.user.username} non autorisé à voir le panier")
        return redirect('listing_list')
    
    cart = request.session.get('cart', {})
    cart_item = None
    
    if cart:
        listing_id = list(cart.keys())[0]
        item = cart[listing_id]
        cart_item = {
            'listing_id': listing_id,
            'title': item['title'],
            'price': Decimal(item['price']),
            'image_url': item['image_url'],
        }
    
    if request.method == 'POST':
        if 'clear_cart' in request.POST and cart_item:
            request.session['cart'] = {}
            request.session.modified = True
            messages.success(request, "Panier vidé avec succès !")
            return redirect('view_cart')
        elif cart_item:
            form = CheckoutForm(request.POST)
            if form.is_valid():
                listing = get_object_or_404(Listing, pk=cart_item['listing_id'])
                order = Order(
                    buyer=request.user,
                    listing=listing,
                    amount=cart_item['price'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    phone=form.cleaned_data['phone'],
                    neighborhood=form.cleaned_data['neighborhood'],
                    city=form.cleaned_data['city'],
                    status='pending',
                )
                order.save()
                
                # Envoyer un e-mail au vendeur
                try:
                    send_mail(
                        subject=f"Nouvelle commande: {listing.title}",
                        message=f"Une nouvelle commande a été passée pour {listing.title}.\n"
                                f"Montant: {order.amount} €\n"
                                f"Acheteur: {order.first_name} {order.last_name}\n"
                                f"Téléphone: {order.phone}\n"
                                f"Quartier: {order.neighborhood}\n"
                                f"Ville: {order.city}\n"
                                f"vous avez une nouvelle commande sur DigitusMarket",
                        from_email=settings.EMAIL_HOST_USER, 
                        recipient_list=[listing.user.email],
                        fail_silently=False,
                    )
                    logger.info(f"E-mail envoyé au vendeur {listing.user.email} pour la commande {order.id}")
                except Exception as e:
                    logger.error(f"Erreur lors de l'envoi de l'e-mail au vendeur: {str(e)}")
                
                # Envoyer un e-mail à l'acheteur
                try:
                    send_mail(
                        subject=f"Confirmation de votre commande: {listing.title}",
                        message=f"Votre commande pour {listing.title} a été passée avec succès.\n"
                                f"Montant: {order.amount} €\n"
                                f"Statut: En attente\n"
                                f"Vous pouvez suivre votre commande dans votre tableau de bord.\n"
                                f"Merci de votre achat !",
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[request.user.email],
                        fail_silently=False,
                    )
                    logger.info(f"E-mail de confirmation envoyé à l'acheteur {request.user.email} pour la commande {order.id}")
                except Exception as e:
                    logger.error(f"Erreur lors de l'envoi de l'e-mail à l'acheteur: {str(e)}")
                
                # Vider le panier
                request.session['cart'] = {}
                request.session.modified = True
                messages.success(request, "Commande passée avec succès !")
                return redirect('buyer_dashboard')
        else:
            messages.error(request, "Votre panier est vide.")
            return redirect('listing_list')
    else:
        form = CheckoutForm(initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'phone': request.user.userprofile.phone_number or '' if hasattr(request.user.userprofile, 'phone_number') else '',
        })
    
    return render(request, 'listings/cart.html', {
        'cart_item': cart_item,
        'form': form,
    })

@login_required
def seller_dashboard(request):
    if not check_seller(request.user):
        messages.error(request, "Seuls les vendeurs peuvent accéder à ce tableau de bord.")
        return redirect('listing_list')
    
    orders = Order.objects.filter(listing__user=request.user)
    return render(request, 'listings/seller_dashboard.html', {'orders': orders})

@login_required
def confirm_order(request, order_id):
    if not check_seller(request.user):
        messages.error(request, "Seuls les vendeurs peuvent confirmer des commandes.")
        return redirect('listing_list')
    
    order = get_object_or_404(Order, id=order_id, listing__user=request.user)
    if order.status == 'pending':
        order.status = 'confirmed'
        order.save()
        messages.success(request, "Commande confirmée avec succès !")
        logger.info(f"Commande {order.id} confirmée par {request.user.username}")
    else:
        messages.error(request, "Impossible de confirmer cette commande.")
    return redirect('seller_dashboard')

@login_required
def buyer_dashboard(request):
    if not check_buyer(request.user):
        messages.error(request, "Seuls les acheteurs peuvent accéder à ce tableau de bord.")
        return redirect('listing_list')
    
    orders = Order.objects.filter(buyer=request.user)
    return render(request, 'listings/buyer_dashboard.html', {'orders': orders})

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        messages.error(request, "Seuls les super-utilisateurs peuvent accéder à ce tableau de bord.")
        return redirect('listing_list')
    
    orders = Order.objects.all()
    try:
        traffic = SiteTraffic.objects.latest('date')
        traffic_data = {
            'visitors': traffic.visitors,
            'page_views': traffic.page_views,
        }
    except SiteTraffic.DoesNotExist:
        traffic_data = {
            'visitors': 0,
            'page_views': 0,
        }
    
    return render(request, 'listings/admin_dashboard.html', {
        'orders': orders,
        'traffic_data': traffic_data,
    })

