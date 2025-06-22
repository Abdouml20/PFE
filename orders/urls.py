from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    path('detail/<int:pk>/', views.order_detail, name='order_detail'),
    path('history/', views.order_history, name='order_history'),
    
    # Artist order management
    path('artist/', views.artist_orders, name='artist_orders'),
    path('artist/detail/<int:pk>/', views.artist_order_detail, name='artist_order_detail'),
    path('artist/update-status/<int:pk>/', views.update_order_status, name='update_order_status'),
]
