# Generated by Django 4.2.5 on 2024-01-03 03:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compute', '0009_group_enable'),
    ]

    operations = [
        migrations.AddField(
            model_name='center',
            name='keyring',
            field=models.TextField(default='', verbose_name='宿主机 ssh key文本'),
        ),
        migrations.AddField(
            model_name='center',
            name='ssh_key',
            field=models.CharField(blank=True, editable=False, help_text='ssh 私钥', max_length=200, verbose_name='ssh key文件保存路径'),
        ),
    ]
