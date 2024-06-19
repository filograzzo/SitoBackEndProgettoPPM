# Generated by Django 4.2.11 on 2024-06-19 20:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0005_customuser_friends'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='category',
            field=models.CharField(choices=[('ANTIPASTI', 'Antipasti'), ('PRIMI', 'Primi'), ('SECONDI', 'Secondi'), ('DOLCI', 'Dolci')], default='PRIMI', max_length=10),
        ),
    ]