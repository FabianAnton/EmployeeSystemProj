# Generated by Django 5.1.6 on 2025-03-25 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0002_alter_employee_employee_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='archived',
            field=models.BooleanField(default=False),
        ),
    ]
