# Generated by Django 3.2.16 on 2024-02-02 13:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_post_comment_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='comment_count',
        ),
    ]