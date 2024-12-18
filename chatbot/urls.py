from django.urls import path
from . import views

urlpatterns = [
    path('response/', views.chatbot_response, name='chatbot_response'),
    path('sessions/', views.get_chat_sessions, name='get_chat_sessions'),
    path('sessions/<str:date>/', views.get_session_messages_by_date, name='get_session_messages_by_date'),
    path('', views.chatbot_page, name='chatbot_page'),
]
