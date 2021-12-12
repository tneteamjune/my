# Generated by Django 3.1.2 on 2021-12-12 17:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(blank=True, max_length=30, null=True)),
                ('email', models.CharField(max_length=50)),
                ('subject', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('create_date', models.DateTimeField()),
                ('modify_date', models.DateTimeField(blank=True, null=True)),
                ('imgs', models.ImageField(blank=True, null=True, upload_to='images/')),
                ('type', models.CharField(blank=True, choices=[('add', '휴지통 추가 설치가 필요해요'), ('idea', '이런 기능이 있었으면 해요'), ('error', '사이트에 오류가 있어요'), ('etc', '그 외 문의가 있어요')], max_length=100, null=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-create_date',),
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=30, null=True)),
                ('email', models.CharField(max_length=100, null=True)),
                ('greenpoint', models.IntegerField(blank=True, null=True, verbose_name='초록점수')),
                ('coupon', models.IntegerField(default=0, verbose_name='쿠폰')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Point',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('point', models.IntegerField(default=0)),
                ('reason', models.TextField(default='')),
                ('event', models.TextField(default='')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='images/')),
                ('contact', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='common.contact')),
            ],
        ),
    ]
