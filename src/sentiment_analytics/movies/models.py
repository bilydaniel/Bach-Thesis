from django.db import models

# Create your models here.
class Countries(models.Model):
    title = models.TextField(primary_key=True)
    country = models.TextField()

    class Meta:
        managed = False
        db_table = 'countries'
        unique_together = (('title', 'country'),)

class Genres(models.Model):
    title = models.TextField(primary_key=True)
    genre = models.TextField()

    class Meta:
        managed = False
        db_table = 'genres'
        unique_together = (('title', 'genre'),)

class Movies(models.Model):
    title = models.TextField(primary_key=True)
    avg_polarity = models.FloatField(blank=True, null=True)
    avg_stars = models.FloatField(blank=True, null=True)
    actors_score = models.FloatField(blank=True, null=True)
    story_score = models.FloatField(blank=True, null=True)
    characters_score = models.FloatField(blank=True, null=True)
    audio_video_score = models.FloatField(blank=True, null=True)
    experience_score = models.FloatField(blank=True, null=True)
    language = models.TextField()
    popularity = models.IntegerField(blank=True, null=True)
    movie_series = models.BooleanField(blank=True, null=True)
    original_rating = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'movies'
        unique_together = (('title', 'language'),)


class Reviews(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.TextField(blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    rating = models.TextField(blank=True, null=True)
    critic = models.TextField(blank=True, null=True)
    date = models.TextField(blank=True, null=True)
    freshness = models.TextField(blank=True, null=True)
    source = models.TextField(blank=True, null=True)
    analyzed = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'reviews'

class Aspects(models.Model):
    review = models.OneToOneField('Reviews', models.DO_NOTHING, primary_key=True)
    actor_pos = models.IntegerField(blank=True, null=True)
    actor_neg = models.IntegerField(blank=True, null=True)
    audio_video_pos = models.IntegerField(blank=True, null=True)
    audio_video_neg = models.IntegerField(blank=True, null=True)
    character_pos = models.IntegerField(blank=True, null=True)
    character_neg = models.IntegerField(blank=True, null=True)
    experience_pos = models.IntegerField(blank=True, null=True)
    experience_neg = models.IntegerField(blank=True, null=True)
    story_pos = models.IntegerField(blank=True, null=True)
    story_neg = models.IntegerField(blank=True, null=True)
    stat_used = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'aspects'



class PosNeg(models.Model):
    predicted_value = models.FloatField(blank=True, null=True)
    predicted_class = models.TextField(blank=True, null=True)
    review = models.OneToOneField('Reviews', models.DO_NOTHING, primary_key=True,related_name="reviewjoin")
    stat_used = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pos_neg'