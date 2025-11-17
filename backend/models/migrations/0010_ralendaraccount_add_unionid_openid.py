# Generated migration: Add ralendar_unionid and ralendar_openid fields to RalendarAccount

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0009_ralendaraccount'),
    ]

    operations = [
        migrations.AddField(
            model_name='ralendaraccount',
            name='ralendar_unionid',
            field=models.CharField(blank=True, help_text='Ralendar 用户的 UnionID（QQ/微信）', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='ralendaraccount',
            name='ralendar_openid',
            field=models.CharField(blank=True, help_text='Ralendar 用户的 OpenID（QQ/微信）', max_length=100, null=True),
        ),
    ]

