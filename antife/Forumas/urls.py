from django.urls import path, include
from . import views

app_name = 'Forumas'

urlpatterns = [
    path('', views.forumasview, name='forumasview'),
    path('create_topic/', views.create_topic, name='create_topic'),
    path('add_comment/<int:irasas_id>/', views.add_comment, name='add_comment'),
    path('delete_comment/', views.delete_comment, name='delete_comment'),
    path('like_comment/<int:pk>/', views.like_comment, name='like_comment'),
    path('ckeditor/', include('ckeditor_uploader.urls')),
]