from django.urls import path
from . import views

app_name = 'artists'

urlpatterns = [
    path('', views.artist_list, name='artist_list'),
    path('<int:pk>/', views.artist_detail, name='artist_detail'),
    path('dashboard/', views.artist_dashboard, name='artist_dashboard'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('products/delete/<int:pk>/', views.delete_product, name='delete_product'),
    path('products/toggle-availability/<int:pk>/', views.toggle_product_availability, name='toggle_product_availability'),
]
