
#listings/urls.py
from django.urls import path
from . import views


   
    

urlpatterns = [
    path('', views.listing_list, name='listing_list'),
   path('listing/<int:pk>/', views.listing_detail, name='listing_detail'), 
    path('create/', views.create_listing, name='create_listing'),
    path('edit/<int:pk>/', views.edit_listing, name='edit_listing'),
   path('delete/<int:pk>/', views.delete_listing, name='delete_listing'),
   path('add-to-cart/<int:listing_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('seller/', views.seller_dashboard, name='seller_dashboard'),
    path('confirm-order/<int:order_id>/', views.confirm_order, name='confirm_order'),
   path('buyer/', views.buyer_dashboard, name='buyer_dashboard'),
   path('admin/', views.admin_dashboard, name='admin_dashboard'),
]
    

          
          

 #path('', views.listing_list, name='listing_list'),
    #path('create/', views.create_listing, name='create_listing'),
    #path('<int:pk>/', views.listing_detail, name='listing_detail'),
    #path('<int:pk>/edit/', views.edit_listing, name='edit_listing'),
    #path('<int:pk>/delete/', views.delete_listing, name='delete_listing'),
    
   
    #path('checkout/', views.checkout, name='checkout'),
   


