# Generated migration for RalendarAccount model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('models', '0008_alter_trip_is_published'),  # 修改为实际的上一个迁移文件
    ]

    operations = [
        migrations.CreateModel(
            name='RalendarAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ralendar_user_id', models.IntegerField(help_text='Ralendar 用户 ID')),
                ('ralendar_username', models.CharField(help_text='Ralendar 用户名', max_length=100)),
                ('ralendar_email', models.EmailField(blank=True, help_text='Ralendar 邮箱', max_length=254, null=True)),
                ('ralendar_avatar', models.URLField(blank=True, help_text='Ralendar 头像 URL', null=True)),
                ('ralendar_provider', models.CharField(blank=True, help_text='Ralendar 登录方式：qq/acwing/email', max_length=20, null=True)),
                ('access_token', models.TextField(help_text='Ralendar Access Token（JWT）')),
                ('refresh_token', models.TextField(blank=True, help_text='Ralendar Refresh Token（可选）', null=True)),
                ('token_type', models.CharField(default='Bearer', help_text='Token 类型', max_length=20)),
                ('token_expires_at', models.DateTimeField(blank=True, help_text='Token 过期时间', null=True)),
                ('scope', models.CharField(default='calendar:read calendar:write', help_text='授权的权限范围', max_length=200)),
                ('is_active', models.BooleanField(default=True, help_text='是否激活')),
                ('is_default', models.BooleanField(default=False, help_text='是否为默认账号（同步时默认使用此账号）')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='绑定时间')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='更新时间')),
                ('last_synced_at', models.DateTimeField(blank=True, help_text='最后同步时间', null=True)),
                ('user', models.ForeignKey(help_text='Roamio 用户', on_delete=django.db.models.deletion.CASCADE, related_name='ralendar_accounts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Ralendar 账号',
                'verbose_name_plural': 'Ralendar 账号',
                'db_table': 'ralendar_accounts',
                'ordering': ['-is_default', '-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='ralendaraccount',
            index=models.Index(fields=['user', 'is_active'], name='ralendar_ac_user_id_8c01c6_idx'),
        ),
        migrations.AddIndex(
            model_name='ralendaraccount',
            index=models.Index(fields=['user', 'is_default'], name='ralendar_ac_user_id_a44982_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='ralendaraccount',
            unique_together={('user', 'ralendar_user_id')},
        ),
    ]

