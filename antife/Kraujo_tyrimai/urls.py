from django.urls import path
from . import views

app_name = 'kraujo_tyrimai'

urlpatterns = [
    path('', views.kraujotyrview, name='kraujotyrview'),
    path('<int:selected_year>/', views.kraujotyrview, name='kraujotyrview'),
    path('create_kraujo_tyrimas/', views.create_kraujo_tyrimas, name='create_kraujo_tyrimas'),
]
