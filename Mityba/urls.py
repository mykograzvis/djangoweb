from django.urls import path
from . import views
from .views import product

app_name = 'Mityba'

urlpatterns = [
    # Define your URL patterns here
    path('product/', views.product, name='product'),
    path('receptai_list/', views.receptai_list, name='receptai_list'),
    path('create_recipe/', views.create_recipe_view, name='create_recipe'),
    path('valgiarastis/', views.valgiarastis, name='valgiarastis'),
    path('create_valgiarastis/', views.create_valgiarastis, name='create_valgiarastis'),
    path('receptai_list/<int:recipe_id>/', views.remove_recipe_view, name='remove_recipe'),
    path('valgymai/', views.valgymai_open, name='valgymai_open'),
    path('manoreceptai_list/', views.manoreceptai_list, name='manoreceptai_list'),
    path('add_to_favorites/<int:recipe_id>/', views.add_to_favorites, name='add_to_favorites'),
    path('delete_valgomasReceptas/<int:valgymo_receptas_id>/', views.delete_valgomasReceptas, name='delete_valgomasReceptas'),
    path('delete_valgomasProduktas/<int:valgomas_produktas_id>/', views.delete_valgomasProduktas, name='delete_valgomasProduktas'),
    path('add_valgymas/', views.add_new_valgymas, name='add_valgymas'),
    path('saveCopy/', views.saveCopy, name='saveCopy'),
    path('copyValgiarastis/', views.copyValgiarastis, name='copyValgiarastis'),
    path('receptukurimas/', views.create_recipe_view, name='create_recipe'),
    path('panaudotireceptai/', views.panaudotireceptai, name='panaudoti_receptai'),
]