# Generated by Django 5.0.2 on 2024-04-22 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homepage', '0012_komentarai_likes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='komentarai',
            name='likes',
        ),
        migrations.AddField(
            model_name='komentarai',
            name='likes',
            field=models.ManyToManyField(blank=True, related_name='liked_comments', to='homepage.naudotojai'),
        ),
    ]
