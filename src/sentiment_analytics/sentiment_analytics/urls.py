"""sentiment_analytics URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from reviews.views import home_view
from reviews.views import switch_language
from movies.views import movie_detail
from reviews.views import search_results
from movies.views import leaderboard
from movies.views import inc_review_limit
from reviews.views import review_detail
from movies.views import trends
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view),
    path('switch_language', switch_language),
    path('movie/<str:title>', movie_detail,name='movie'),
    path('search',search_results,name='search_results'),
    path('leaderboard',leaderboard,name='leaderboard'),
    path('inc_review_limit', inc_review_limit, name='inc_review_limit'),
    path('review_detail/<int:id>', review_detail, name='review_detail'),
    path('review_detail', review_detail, name='review_detail'),
    path('trends',trends,name='trends'),

]
