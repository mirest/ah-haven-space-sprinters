# Generated by Django 2.1.7 on 2019-04-25 14:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0008_auto_20190425_1325'),
    ]

    operations = [
        migrations.RenameField(
            model_name='report',
            old_name='body',
            new_name='reason',
        ),
        migrations.AlterField(
            model_name='report',
            name='article',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='articles.Article'),
        ),
    ]
