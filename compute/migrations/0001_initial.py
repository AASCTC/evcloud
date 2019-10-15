# Generated by Django 2.2.6 on 2019-10-15 08:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('network', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Center',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='数据中心名称')),
                ('location', models.CharField(max_length=100, verbose_name='位置')),
                ('desc', models.CharField(blank=True, default='', max_length=200, verbose_name='简介')),
            ],
            options={
                'verbose_name': '分中心',
                'verbose_name_plural': '01_分中心',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, verbose_name='组名称')),
                ('desc', models.CharField(blank=True, default='', max_length=200, verbose_name='描述')),
                ('center', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='compute.Center', verbose_name='组所属的分中心')),
                ('users', models.ManyToManyField(blank=True, related_name='user_set', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '宿主机组',
                'verbose_name_plural': '02_宿主机组',
                'ordering': ('id',),
                'unique_together': {('center', 'name')},
            },
        ),
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('ipv4', models.GenericIPAddressField(unique=True, verbose_name='宿主机ip')),
                ('vcpu_total', models.IntegerField(default=24, verbose_name='宿主机CPU总数')),
                ('vcpu_allocated', models.IntegerField(default=0, verbose_name='已分配CPU总数')),
                ('mem_total', models.IntegerField(default=32768, verbose_name='宿主机总内存大小')),
                ('mem_allocated', models.IntegerField(default=0, verbose_name='宿主机已分配内存大小')),
                ('mem_reserved', models.IntegerField(default=2038, verbose_name='宿主机要保留的内存空间大小')),
                ('vm_limit', models.IntegerField(default=10, verbose_name='本机可创建虚拟机数量上限')),
                ('vm_created', models.IntegerField(default=0, verbose_name='本机已创建虚拟机数量')),
                ('enable', models.BooleanField(default=True, verbose_name='宿主机状态')),
                ('desc', models.CharField(blank=True, default='', max_length=200, verbose_name='描述')),
                ('ipmi_host', models.CharField(blank=True, default='', max_length=100)),
                ('ipmi_user', models.CharField(blank=True, default='', max_length=100)),
                ('ipmi_password', models.CharField(blank=True, default='', max_length=100)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='compute.Group', verbose_name='宿主机所属的组')),
                ('vlans', models.ManyToManyField(related_name='vlan_hosts', to='network.Vlan', verbose_name='VLAN子网')),
            ],
            options={
                'verbose_name': '宿主机',
                'verbose_name_plural': '06_宿主机',
            },
        ),
    ]
