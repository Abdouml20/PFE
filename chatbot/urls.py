from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.ChatbotView.as_view(), name='chatbot'),
    path('api/chat/', views.ChatbotView.as_view(), name='chat_api'),
    path('api/history/<str:session_id>/', views.get_chat_history, name='chat_history'),
    path('api/clear/', views.clear_chat_history, name='clear_chat'),
]
