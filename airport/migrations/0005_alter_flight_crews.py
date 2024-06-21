# Generated by Django 4.0.4 on 2024-06-11 16:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('airport', '0004_airplane_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flight',
            name='crews',
            field=models.ManyToManyField(blank=True, related_name='flights', to='airport.crew'),
        ),
    ]