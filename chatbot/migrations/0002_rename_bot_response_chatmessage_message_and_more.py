# Generated by Django 5.1.3 on 2024-12-11 10:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chatmessage',
            old_name='bot_response',
            new_name='message',
        ),
        migrations.RemoveField(
            model_name='chatmessage',
            name='user_message',
        ),
        migrations.AddField(
            model_name='chatmessage',
            name='sender',
            field=models.CharField(default=1, max_length=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='chatmessage',
            name='session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chatbot.chatsession'),
        ),
    ]
