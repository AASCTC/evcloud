# Generated by Django 4.2.9 on 2024-04-10 05:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compute', '0010_center_keyring_center_ssh_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='center',
            name='ssh_public',
            field=models.TextField(default='', verbose_name='宿主机ssh公钥（id_rsa.pub）'),
        ),
    ]
