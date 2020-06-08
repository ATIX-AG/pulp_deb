# Generated by Django 2.2.13 on 2020-06-10 12:49

from django.db import migrations
import pulp_deb.app.models.content


class Migration(migrations.Migration):

    dependencies = [
        ('deb', '0018_debversion_extension'),
    ]

    operations = [
        migrations.AlterField(
            model_name='installerpackage',
            name='version',
            field=pulp_deb.app.models.content.DebVersionField(max_length=255),
        ),
        migrations.AlterField(
            model_name='package',
            name='version',
            field=pulp_deb.app.models.content.DebVersionField(max_length=255),
        ),
    ]