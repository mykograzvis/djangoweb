from django.urls import path
from . import views

app_name = 'profilis'

urlpatterns = [
    path('', views.profilisview, name='profilisview'),
    path('save_profile_changes/', views.save_profile_changes, name='save_profile_changes'),
    path('profilis/', views.profilisview, name='profilis'), 
]
