from django.urls import path, include
from .views import home, login, register, logout_view, loged

urlpatterns = [
   path("", home, name="home"),
   path('login/', login, name='login'),
   path('register/', register, name='register'),
   path('logout/', logout_view, name='logout'),
   path('mityba/', include('Mityba.urls', namespace='mityba')),
   path('forumas/', include('Forumas.urls', namespace='forumas')),
   path('profilis/', include('Profilis.urls', namespace='profilis')), 
   path('kraujo_tyrimai/', include('Kraujo_tyrimai.urls', namespace='kraujo_tyrimai')), 
    path('baseLogged/', loged, name='loged'),
]
