# Generated by Django 3.1.1 on 2020-09-05 10:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Session',
            fields=[
                ('session_id', models.IntegerField(primary_key=True, serialize=False, unique=True)),
                ('create_time', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('question_id', models.IntegerField(primary_key=True, serialize=False, unique=True)),
                ('question', models.CharField(max_length=255)),
                ('session_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='session_link', to='main_app.session')),
            ],
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('option_id', models.IntegerField(primary_key=True, serialize=False, unique=True)),
                ('question_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='question_link', to='main_app.question')),
            ],
        ),
    ]
