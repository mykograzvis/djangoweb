from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    name = models.CharField(max_length=255)
    calories = models.DecimalField(max_digits=6, decimal_places=2)
    total_fat = models.DecimalField(max_digits=5, decimal_places=2)
    fiber = models.DecimalField(max_digits=5, decimal_places=2)
    protein = models.DecimalField(max_digits=5, decimal_places=2)
    phenylalanine = models.DecimalField(max_digits=6, decimal_places=2)
    measure = models.CharField(max_length=255)
    homePhenylalanine = models.DecimalField(max_digits=6, decimal_places=2)
    homeWeight = models.DecimalField(max_digits=5, decimal_places=2)
    category = models.CharField(max_length=255)
    color = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Naudotojai(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None)
    vardas = models.CharField(max_length=255)
    pavarde = models.CharField(max_length=255)
    telefonas = models.CharField(max_length=255)
    el_pastas = models.CharField(max_length=255)
    gimimo_data = models.DateField()
    level = models.IntegerField()
    last_login = models.DateTimeField(null=True, blank=True)

class Receptai(models.Model):
    kalorijos = models.FloatField(default=0.0)
    pavadinimas = models.CharField(max_length=255)
    fenilalaninas = models.FloatField(default=0.0)
    baltymai = models.FloatField(default=0.0)
    aprasas = models.CharField(max_length=255)

class Irasai(models.Model):
    pavadinimas = models.CharField(max_length=255, default="Pavadinimas")
    tekstas = models.CharField(max_length=2555)
    data = models.DateField()
    category = models.CharField(max_length=50,default="Daktarui") # New field for category
    fk_Naudotojasid_Naudotojas = models.ForeignKey(Naudotojai, on_delete=models.CASCADE)

class Kraujo_tyrimai(models.Model):
    data = models.DateField()
    fenilalaninas = models.IntegerField()
    fk_Naudotojasid_Naudotojas = models.ForeignKey(Naudotojai, on_delete=models.CASCADE)

class Naudotojo_receptai(models.Model):
    fk_Receptasid_Receptas = models.ForeignKey(Receptai, on_delete=models.CASCADE)
    fk_Naudotojasid_Naudotojas = models.ForeignKey(Naudotojai, on_delete=models.CASCADE)

class Megstamiausi_receptai(models.Model):
    fk_Receptasid_Receptas = models.ForeignKey(Receptai, on_delete=models.CASCADE)
    fk_Naudotojasid_Naudotojas = models.ForeignKey(Naudotojai, on_delete=models.CASCADE)

class Valgiarasciai(models.Model):
    diena = models.IntegerField()
    bendras_fenilalaninas = models.DecimalField(max_digits=10, decimal_places=2)
    bendras_baltymas = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    data = models.DateField()
    fk_Naudotojasid_Naudotojas = models.ForeignKey(Naudotojai, on_delete=models.CASCADE)

class Komentarai(models.Model):
    tekstas = models.CharField(max_length=255)
    data = models.DateField()
    fk_Irasasid_Irasas = models.ForeignKey(Irasai, on_delete=models.CASCADE)
    fk_Naudotojasid_Naudotojas = models.ForeignKey(Naudotojai, on_delete=models.CASCADE)
    likes = models.ManyToManyField(Naudotojai, related_name='liked_comments', blank=True)

class Valgymai(models.Model):
    tipas = models.CharField(max_length=255)
    bendras_baltymas = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    bendras_fenilalaninas = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    fk_Valgiarastisid_Valgiarastis = models.ForeignKey(Valgiarasciai, on_delete=models.CASCADE)


class Valgomas_produktas(models.Model):
    fk_Valgymasid_Valgymas = models.ForeignKey(Valgymai, on_delete=models.CASCADE)
    fk_Produktasid_Produktas = models.ForeignKey(Product, on_delete=models.CASCADE)
    kiekis = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

class Valgymo_receptas(models.Model):
    fk_Receptasid_Receptas = models.ForeignKey(Receptai, on_delete=models.CASCADE)
    fk_Valgymasid_Valgymas = models.ForeignKey(Valgymai, on_delete=models.CASCADE)
    kiekis = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

class Recepto_produktai(models.Model):
    fk_Receptasid_Receptas = models.ForeignKey(Receptai, on_delete=models.CASCADE)
    fk_Produktasid_Produktas = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
