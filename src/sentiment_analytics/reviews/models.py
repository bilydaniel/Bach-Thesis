from django.db import models

# Create your models here.
class Reviews(models.Model):
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

class Genres(models.Model):
    title = models.TextField(primary_key=True)
    genre = models.TextField()

    class Meta:
        managed = False
        db_table = 'genres'
        unique_together = (('title', 'genre'),)
class Countries(models.Model):
    title = models.TextField(primary_key=True)
    country = models.TextField()

    class Meta:
        managed = False
        db_table = 'countries'
        unique_together = (('title', 'country'),)



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



    


   
    class Meta:
        managed = False
        db_table = 'movies'



class UsersCsfd(models.Model):
    movie = models.TextField(blank=True, null=True)
    critic = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users_csfd'


class UsersFdb(models.Model):
    movie = models.TextField(blank=True, null=True)
    critic = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users_fdb'


class UsersImdb(models.Model):
    movie = models.TextField(blank=True, null=True)
    critic = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users_imdb'



class UsersRottentomatoes(models.Model):
    movie = models.TextField(blank=True, null=True)
    critic = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users_rottentomatoes'

class PosNeg(models.Model):
    predicted_value = models.FloatField(blank=True, null=True)
    predicted_class = models.TextField(blank=True, null=True)
    review = models.OneToOneField('Reviews', models.DO_NOTHING, primary_key=True)
    stat_used = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pos_neg'


class Classes5(models.Model):
    review_id = models.IntegerField(primary_key=True)
    one_star = models.FloatField(blank=True, null=True)
    two_star = models.FloatField(blank=True, null=True)
    three_star = models.FloatField(blank=True, null=True)
    four_star = models.FloatField(blank=True, null=True)
    five_star = models.FloatField(blank=True, null=True)
    final_rating = models.TextField(blank=True, null=True)
    stat_used = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'classes_5'

class Aspects(models.Model):
    review_id = models.IntegerField(primary_key=True)
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
