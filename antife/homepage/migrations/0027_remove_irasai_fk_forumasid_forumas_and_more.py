# Generated by Django 5.0.2 on 2024-05-02 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homepage', '0026_alter_irasai_category_alter_irasai_tekstas'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='irasai',
            name='fk_Forumasid_Forumas',
        ),
        migrations.AddField(
            model_name='irasai',
            name='pavadinimas',
            field=models.CharField(default='Pavadinimas', max_length=255),
        ),
        migrations.DeleteModel(
            name='Forumai',
        ),
    ]