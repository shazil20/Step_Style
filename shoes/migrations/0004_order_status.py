# Generated by Django 5.0.4 on 2024-06-03 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shoes', '0003_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('DELIVERED', 'Delivered')], default='PENDING', max_length=10),
        ),
    ]