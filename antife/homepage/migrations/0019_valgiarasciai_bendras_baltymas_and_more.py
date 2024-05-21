# Generated by Django 4.2.7 on 2024-04-18 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homepage', '0018_rename_mėgstamiausi_receptai_megstamiausi_receptai'),
    ]

    operations = [
        migrations.AddField(
            model_name='valgiarasciai',
            name='bendras_baltymas',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5),
        ),
        migrations.AddField(
            model_name='valgymai',
            name='bendras_baltymas',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5),
        ),
        migrations.AddField(
            model_name='valgymai',
            name='bendras_fenilalaninas',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5),
        ),
        migrations.AlterField(
            model_name='valgiarasciai',
            name='bendras_fenilalaninas',
            field=models.DecimalField(decimal_places=2, max_digits=5),
        ),
    ]