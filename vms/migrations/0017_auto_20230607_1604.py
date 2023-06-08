# Generated by Django 3.2.13 on 2023-06-07 08:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0008_vlan_vlan_id'),
        ('compute', '0009_group_enable'),
        ('vms', '0016_alter_vm_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='vm',
            name='center_id',
            field=models.ForeignKey(blank=True, db_constraint=False, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='compute.center', verbose_name='数据中心'),
        ),
        migrations.AddField(
            model_name='vm',
            name='last_ip',
            field=models.ForeignKey(blank=True, db_constraint=False, default=None, help_text='该字段在使用搁置服务时使用', null=True, on_delete=django.db.models.deletion.SET_NULL, to='network.macip', verbose_name='虚拟机最后使用ip'),
        ),
        migrations.AddField(
            model_name='vm',
            name='vm_status',
            field=models.CharField(choices=[('shelve', '搁置'), ('normal', '正常')], default='normal', max_length=16, verbose_name='实际运行状态'),
        ),
        migrations.AlterField(
            model_name='vm',
            name='host',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='compute.host', verbose_name='宿主机'),
        ),
        migrations.AlterField(
            model_name='vm',
            name='mac_ip',
            field=models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ip_vm', to='network.macip', verbose_name='MAC IP'),
        ),
    ]
