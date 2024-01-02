# Generated by Django 3.2.13 on 2022-09-19 08:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0006_auto_20201225_1006'),
    ]

    operations = [
        migrations.AddField(
            model_name='vlan',
            name='image_specialized',
            field=models.BooleanField(default=False, verbose_name='镜像虚拟机专用'),
        ),
        migrations.AlterField(
            model_name='vlan',
            name='enable',
            field=models.BooleanField(default=True, verbose_name='启用网络'),
        ),
    ]
