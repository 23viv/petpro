from django.urls import path
from . import views
 
urlpatterns=[
    path('', views.welcome, name='welcome'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('home/',views.home, name="home"),
    path('pet-profile/', views.pet_profile, name='pet_profile'),
    path('chatbot/',views.chatbot,name='chatbot'),
    path('diet_plan/',views.diet_view,name='diet_plan'),
    
    
]