from django.contrib import admin
from import_export.admin import ImportExportActionModelAdmin
from .models import Naudotojai, Product, Receptai, Irasai, Kraujo_tyrimai, Recepto_produktai, Naudotojo_receptai, Megstamiausi_receptai, Valgiarasciai, Komentarai, Valgymai, Valgomas_produktas, Valgymo_receptas

admin.site.register(Product, ImportExportActionModelAdmin)
admin.site.register(Naudotojai)
admin.site.register(Receptai)
admin.site.register(Irasai)
admin.site.register(Kraujo_tyrimai)
admin.site.register(Recepto_produktai)
admin.site.register(Naudotojo_receptai)
admin.site.register(Valgiarasciai)
admin.site.register(Komentarai)
admin.site.register(Valgymai)
admin.site.register(Valgomas_produktas)
admin.site.register(Valgymo_receptas)
admin.site.register(Megstamiausi_receptai)
