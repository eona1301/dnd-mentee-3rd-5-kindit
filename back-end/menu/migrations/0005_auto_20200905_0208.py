# Generated by Django 3.0.2 on 2020-09-04 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0004_auto_20200904_0530'),
    ]

    operations = [
        migrations.CreateModel(
            name='MenuIngredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('brand', models.CharField(max_length=64, verbose_name='브랜드')),
                ('name', models.CharField(max_length=64, verbose_name='재료이름')),
                ('ingredient_type', models.PositiveIntegerField(default='0', verbose_name='재료타입')),
                ('ingredient_image', models.ImageField(blank=True, null=True, upload_to='ingredient/', verbose_name='재료이미지')),
            ],
            options={
                'verbose_name': '커스텀메뉴 재료',
                'verbose_name_plural': '커스텀메뉴 재료',
                'db_table': '커스텀메뉴 재료',
            },
        ),
        migrations.RemoveField(
            model_name='menu',
            name='ingredient',
        ),
        migrations.AddField(
            model_name='menu',
            name='ingredient',
            field=models.ManyToManyField(blank=True, related_name='ingredient', to='menu.MenuIngredient', verbose_name='재료'),
        ),
    ]