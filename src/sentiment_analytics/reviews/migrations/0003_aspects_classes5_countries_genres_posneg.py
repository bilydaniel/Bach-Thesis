# Generated by Django 3.0.3 on 2020-06-24 12:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0002_movies'),
    ]

    operations = [
        migrations.CreateModel(
            name='Aspects',
            fields=[
                ('review_id', models.IntegerField(primary_key=True, serialize=False)),
                ('actor_pos', models.IntegerField(blank=True, null=True)),
                ('actor_neg', models.IntegerField(blank=True, null=True)),
                ('audio_video_pos', models.IntegerField(blank=True, null=True)),
                ('audio_video_neg', models.IntegerField(blank=True, null=True)),
                ('character_pos', models.IntegerField(blank=True, null=True)),
                ('character_neg', models.IntegerField(blank=True, null=True)),
                ('experience_pos', models.IntegerField(blank=True, null=True)),
                ('experience_neg', models.IntegerField(blank=True, null=True)),
                ('story_pos', models.IntegerField(blank=True, null=True)),
                ('story_neg', models.IntegerField(blank=True, null=True)),
                ('stat_used', models.BooleanField(blank=True, null=True)),
            ],
            options={
                'db_table': 'aspects',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Classes5',
            fields=[
                ('review_id', models.IntegerField(primary_key=True, serialize=False)),
                ('one_star', models.FloatField(blank=True, null=True)),
                ('two_star', models.FloatField(blank=True, null=True)),
                ('three_star', models.FloatField(blank=True, null=True)),
                ('four_star', models.FloatField(blank=True, null=True)),
                ('five_star', models.FloatField(blank=True, null=True)),
                ('final_rating', models.TextField(blank=True, null=True)),
                ('stat_used', models.BooleanField(blank=True, null=True)),
            ],
            options={
                'db_table': 'classes_5',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Countries',
            fields=[
                ('title', models.TextField(primary_key=True, serialize=False)),
                ('country', models.TextField()),
            ],
            options={
                'db_table': 'countries',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Genres',
            fields=[
                ('title', models.TextField(primary_key=True, serialize=False)),
                ('genre', models.TextField()),
            ],
            options={
                'db_table': 'genres',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='PosNeg',
            fields=[
                ('predicted_value', models.FloatField(blank=True, null=True)),
                ('predicted_class', models.TextField(blank=True, null=True)),
                ('review', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='reviews.Reviews')),
                ('stat_used', models.BooleanField(blank=True, null=True)),
            ],
            options={
                'db_table': 'pos_neg',
                'managed': False,
            },
        ),
    ]
