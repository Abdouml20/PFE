from django.urls import path
from . import views

app_name = 'categories'

urlpatterns = [
    path('', views.category_list, name='category_list'),
    path('crafts/', views.craft_category_list, name='craft_category_list'),
    path('crafts/<str:craft_id>/', views.craft_category_detail, name='craft_category_detail'),
    path('add/', views.add_category, name='add_category'),
    path('edit/<int:pk>/', views.edit_category, name='edit_category'),
    path('delete/<int:pk>/', views.delete_category, name='delete_category'),
    path('<slug:slug>/', views.category_detail, name='category_detail'),
]
