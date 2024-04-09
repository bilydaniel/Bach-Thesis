from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import Movies
from .models import Reviews
from .models import PosNeg
from .models import Aspects
from .models import Genres
from .models import Countries
import datetime
from dateutil.relativedelta import *
from django.db.models import Q
from django.db.models import Avg,F
from django.http import HttpResponseRedirect
from django.db.models import FloatField
from django.db.models.functions import Cast


# Create your views here.
def make_dictionary(request):
	text = {}
	if(request.session['language']=="CZ"):
		text["from"] = "Od"
		text["to"] = "Do"
		text["step"] = "Krok"
		text["day"] = "Den"
		text["month"] = "Měsíc"
		text["year"] =  "Rok"
		text["source"] = "Zdroj"
		text["original"] = "Originílní hodnocení"
		text["analyser"] = "Hondocení analyzátoru"
		text["button_text"] = "Vykreslit Graf"
		text["graph_title"] = "Počet pozitivních a negativních recenzí v čase"
		text["graph_pos"] = "Pozitivní Recenze"
		text["graph_neg"] = "Negativní Recenze"
		text["avg_values"] = "Průměrná hodnocení"
		text["avg_rating"] = "Hodnocení uživatelů"
		text["avg_polarity"] = "Polarita analyzátoru"
		text["avg_stars"] = "Průměrný počet hvězd analyzátoru[1-5]"
		text["actors_score"] = "Aspekt herců" 
		text["story_score"] = "Aspekt příběhu"
		text["characters_score"] = "Aspekt postav" 
		text["audio_video_score"] = "Audio-vizuální aspekt"
		text["experience_score"] = "Aspekt zkušenosti s filmem"
		text["rating"] = "Hodnocení"
		text["author"] = "Autor"
		text["date"] = "Datum"
		text["filter_reviews"] = "Filtrovat příspěvky"
		text["asc"] = "Vzestupně"
		text["dsc"] = "Sestupně"
		text["all"] = "Všechny"
		text["number"] = "Počet recenzí"
		text["details"] = "Detailní informace"
		text["type"] = "Film / Seriál"
		text["original_rating"] = "Originální Hodnocení"
		text["popularity"] = "Popularita"
		text["movie"] = "Film"
		text["series"] = "Seriál"
		text["genres"] = "Žánry"
		text["countries"] = "Země"
	else:
		text["from"] = "From"
		text["to"] = "To"
		text["step"] = "Step"
		text["day"] = "Day"
		text["month"] = "Month"
		text["year"] =  "Year"
		text["source"] = "Source"
		text["original"] = "Original rating"
		text["analyser"] = "Analyser rating"
		text["button_text"] = "Draw Graph"
		text["graph_title"] = "Number of positive and negative reviews in time"
		text["graph_pos"] = "Positive Reviews"
		text["graph_neg"] = "Negative Reviews"
		text["avg_values"] = "Average ratings"
		text["avg_rating"] = "User rating"
		text["avg_polarity"] = "Analyser polarity"
		text["avg_stars"] = "Analyser stars[1-5]"
		text["actors_score"] = "Actor aspect"
		text["story_score"] = "Story aspect"
		text["characters_score"] = "Character aspect"
		text["audio_video_score"] = "audio-video aspect"
		text["experience_score"] = "experience aspect"
		text["rating"] = "Rating"
		text["author"] = "Author"
		text["date"] = "Date"
		text["filter_reviews"] = "Filter reviews"
		text["asc"] = "Ascending"
		text["dsc"] = "Descending"
		text["all"] = "All"
		text["number"] = "Number of reviews"

		text["details"] = "Details"
		text["type"] = "Movie / Series"
		text["original_rating"] = "Original Rating"
		text["popularity"] = "Popularity"
		text["movie"] = "Movie"
		text["series"] = "Series"
		text["genres"] = "Genres"
		text["countries"] = "Countries"
	return text

def get_ratings(title,language,dates,step_size,rating_source):
	if(language == "cz"):
		review_source = ["csfd","fdb"]
		separator = "."
	else:
		review_source = ["imdb","rottentomatoes"]
		separator = " "
	if(step_size=="day"):
			pass
	elif(step_size=="month"):
		for i,date in enumerate(dates):
			split_date = date.split(separator)
			dates[i] = separator.join([split_date[1],split_date[2]])

	elif(step_size=="year"):
		for i,date in enumerate(dates):
			dates[i] = date.split(separator)[2]

	pos_dict = {}
	neg_dict= {}
	date_query = Q()

	for query_date in dates:
		if(rating_source == "original"):
			date_query = date_query | Q(date__contains=query_date)
		else:
			date_query = date_query | Q(review__date__contains=query_date)
		pos_dict[query_date] = 0
		neg_dict[query_date] = 0

	if(rating_source == "original"):
		pos_results = Reviews.objects.filter(title__exact=title).filter(source__in=review_source).filter(rating__gt=0.5).filter(date_query).values_list('date', flat=True)
		neg_results = Reviews.objects.filter(title__exact=title).filter(source__in=review_source).filter(rating__lte=0.5).filter(date_query).values_list('date', flat=True)


	else:
		pos_results = PosNeg.objects.filter(predicted_class__exact="pos").filter(review__title=title).filter(review__source__in=review_source).filter(date_query).values_list('review__date', flat=True)		
		neg_results = PosNeg.objects.filter(predicted_class__exact="neg").filter(review__title=title).filter(review__source__in=review_source).filter(date_query).values_list('review__date', flat=True)		
	positive_results = []
	negative_results = []
	for i,pos_result in enumerate(pos_results):
		split_pos = pos_result.split(separator)

		if(step_size == "day"):
			split_pos_res = split_pos
		elif(step_size == "month"):
			split_pos_res = [split_pos[1],split_pos[2]]
		elif(step_size == "year"):
			split_pos_res = [split_pos[2]]
		positive_results.append(separator.join(split_pos_res)) 

	for i,neg_result in enumerate(neg_results):
		split_neg = neg_result.split(separator)

		if(step_size == "day"):
			split_neg_res = split_neg
		elif(step_size == "month"):
			split_neg_res = [split_neg[1],split_neg[2]]
		elif(step_size == "year"):
			split_neg_res = [split_neg[2]]

		negative_results.append(separator.join(split_neg_res))

	
	for key,value in pos_dict.items():
		for pos_result in positive_results:
			if(key == pos_result):
				#print(key,pos_result)
				pos_dict[key] += 1

	for key,value in neg_dict.items():
		for neg_result in negative_results:
			if(key == neg_result):
				neg_dict[key] += 1

	pos_arr=[]
	neg_arr=[]
	for key,value in pos_dict.items():
		pos_arr.append(value)
	for key,value in neg_dict.items():
		neg_arr.append(value)
	return pos_arr,neg_arr

def get_graph_data(title,request_data,language):
	pos_result = []
	neg_result = []
	
	start_date = datetime.datetime.strptime(request_data["from"], '%Y-%m-%d')
	end_date = datetime.datetime.strptime(request_data["to"], '%Y-%m-%d')
	if(request_data["step_size"] == "day"):
		delta = datetime.timedelta(days=1)
	elif(request_data["step_size"] == "month"):
		delta = relativedelta(months=+1)

	elif(request_data["step_size"] == "year"):
		delta = relativedelta(years=+1)

	dates = []
	while start_date <= end_date:
		if(language == "cz"):
			format_date = start_date.strftime('%-d.%-m.%Y')
			dates.append(format_date)		
		else:
			format_date = start_date.strftime('%-d %B %Y')
			dates.append(format_date)
		start_date += delta
	
	pos_results, neg_results = get_ratings(title,language, dates,request_data["step_size"],request_data["source"])
	return pos_results,neg_results,dates

	
def inc_review_limit(request):
	if("review_limit" not in request.session):
		request.session["review_limit"] = 10
	else:
		request.session["review_limit"] = request.GET["num_reviews"]
		 

	return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
		
def movie_detail(request,title):
	form_values = {}
	if(request.method == "GET"):
		request.session["values_pos"] = 0
		request.session["values_neg"] = 0
		request.session["values_dates"] = 0
		request.session["review_limit"] = 10

		form_values["all_selected"] = "selected"
		form_values["asc_checked"] = "checked"
		pick_aspect ="all"
	
	if(request.method =="POST"):
		request.session["review_limit"] =  request.POST.get('num_reviews', 10)
		date_from = request.POST.get('from', None)
		date_to = request.POST.get('to', None)

		step_size = request.POST.get('step_size', None)
		source = request.POST.get('source', None)
		
		form_values["date_from"] = date_from
		form_values["date_to"] = date_to
		form_values["day_checked"] = "checked" if (step_size =="day") else ""
		form_values["month_checked"] = "checked" if (step_size =="month") else ""
		form_values["year_checked"] = "checked" if (step_size =="year") else ""
		
		form_values["original_checked"] = "checked" if (source =="original") else ""
		form_values["analyser_checked"] = "checked" if (source =="analyser") else ""
		if(date_from != None):
			values_pos,values_neg,values_dates = get_graph_data(title,request.POST,request.session['language'].lower())
			request.session["values_pos"] = values_pos
			request.session["values_neg"] = values_neg
			request.session["values_dates"] = values_dates

		pick_aspect = request.POST.get("pick_aspect","all")
		form_values[pick_aspect+"_selected"] = "selected"
	
	if(request.session['language'].lower() == "cz"):
		review_source = ["csfd","fdb"]
	else:
		review_source = ["imdb","rottentomatoes"]
	
	avg_rating = Reviews.objects.filter(title__exact=title).exclude(Q(rating__contains='-')).annotate(rating_float=Cast('rating',FloatField())).aggregate(Avg('rating_float'))
	print(avg_rating)
	movie = get_object_or_404(Movies,title=title,language=request.session['language'].lower())
	text = make_dictionary(request)

	if(pick_aspect == "all"):
		reviews = Reviews.objects.filter(title__exact=title).filter(source__in=review_source)[:int(request.session["review_limit"])]
	else:
		pos_field = pick_aspect+"_pos__exact"
		neg_field = pick_aspect+"_neg__exact"
		pos_contains = {pos_field: 0}
		neg_contains = {neg_field: 0}
		aspect_query = Q(**pos_contains)& Q(**neg_contains)
		reviews = Aspects.objects.filter(review__title=title).filter(review__source__in=review_source).exclude(aspect_query)[:int(request.session["review_limit"])]	
		reviews_result = []
		for x,review in enumerate(reviews):
			reviews_result.append(review.review)
		reviews = reviews_result 
	
	if(movie.movie_series):
		if(request.session['language'].lower() == "cz"):
			movie_type = ""
		else:
			movie_type = "Series"
	else:
		if(request.session['language'].lower() == "cz"):
			movie_type = ""
		else:
			movie_type = "Movie"
		

	genres = Genres.objects.raw('SELECT * FROM genres WHERE title=%s',[movie.title])
	movie_genres = ""
	for genre in genres:
		movie_genres += genre.genre +" "

	countries = Countries.objects.raw('SELECT * FROM countries WHERE title=%s',[movie.title])
	movie_countries = ""
	for country in countries:
		movie_countries += country.country +" "

	context = {
		"form_values":form_values,
		"movie":movie,
		"text":text,
		"values_pos": request.session["values_pos"],
		"values_neg": request.session["values_neg"],
		"dates": request.session["values_dates"],
		"reviews":reviews,
		"avg_rating":avg_rating['rating_float__avg'],
		"review_limit":request.session["review_limit"],
		"movie_type":movie_type,
		"genres":movie_genres,
		"countries":movie_countries
	}

	return render(request,"movies/detail.html",context)

def make_leaderboard_dictionary(request):
	text = {}
	if(request.session['language']=="CZ"):
		text["order_by"] = "Seřadit podle"	
		text["order"] = "Řadit"
		text["limit"] = "Limit"	
		text["polarity"] = "Polarita"
		text["stars"] = "Počet hvězd"
		text["actor"] = "Aspekt herci"
		text["story"] = "Aspekt příběh"
		text["character"] = "Aspekt postavy"
		text["audio_video"] = "Aspekt audio-video"
		text["experience"] = "Aspekt zkušenost"
		text["asc"] = "Vzestupně"
		text["dsc"] = "Sestupně"
		text["button_text"] = "Filtrovat"
		text["popularity"] = "Popularita"
	else:
		text["order_by"] = "Order by"		
		text["order"] = "Order"
		text["limit"] = "Limit"
		text["polarity"] = "Polarity"
		text["stars"] = "Number of stars"
		text["actor"] = "Actor aspect"
		text["story"] = "Story aspect"
		text["character"] = "Character aspect"
		text["audio_video"] = "Audio- video aspect"
		text["experience"] = "Experience aspect"
		text["asc"] = "Ascending"
		text["dsc"] = "Descending"
		text["button_text"] = "Filter"
		text["popularity"] = "Popularity"

	return text

def leaderboard(request):
	form_values = {}
	language = request.session['language'].lower()
	if(request.method == "GET"):
		form_values["popularity_selected"] = "selected" 
		form_values["dsc_checked"] = "checked" 
		form_values["limit_value"] = 100
		order_by = "popularity"
		order ="DSC"
		limit = 100
		query = "-popularity"
	elif(request.method == "POST"):
		query = ""
		limit = request.POST.get('limit', 100)
		order = request.POST.get('order', "asc")
		order_by = request.POST.get("orderby","polarity")
		
		form_values[order_by+"_selected"] = "selected"
		form_values["limit_value"] = limit
		form_values[order+"_checked"] = "checked"

		if(order == "dsc"):
			query += "-"
		query += order_by

	field_name_isnull = order_by+"__isnull"
	text = make_leaderboard_dictionary(request)
	form_values["as"] = "s"
	results = Movies.objects.filter(language__exact=language).exclude(**{field_name_isnull: True}).order_by(query)[:int(limit)]
	context = {
		"results":results,
		"text":text,
		"form_values":form_values
	}
	return render(request,"movies/leaderboard.html",context)

def get_data_by_type(date_from,date_to):
	sources = ["imdb","rottentomatoes"]
	dates =[]
	dates_clean =[]
	movie_dates = {}
	series_dates = {}
	types = ["movie","series"]
	classes = {}
	

	for x in range(int(date_from),int(date_to)+1):
		dates.append("%"+str(x)+"%")
		movie_dates[x] = 0
		series_dates[x] = 0 
		dates_clean.append(str(x))

	for x_type in types:
		classes[x_type]=[]
		for date in dates:
			classes[x_type].append(0)

	res = Movies.objects.raw('SELECT * FROM movies join reviews on (movies.title=reviews.title)WHERE source = ANY(%s) AND date LIKE ANY(%s) AND  movie_series IS NOT NULL',[sources,dates])
	
	for x,x_date in enumerate(dates_clean):
		for r in res:
			if(x_date in r.date):
				if(r.movie_series):
					classes["series"][x] += 1
				else:
					classes["movie"][x] += 1

	return dates_clean,classes


def get_data_by_genre(date_from,date_to):
	sources = ["imdb","rottentomatoes"]
	dates =[]
	dates_clean = []
	classes = {}
	for x in range(int(date_from),int(date_to)+1):
		dates.append("%"+str(x)+"%")
		dates_clean.append(str(x))

	genres =["Short",
	 "Horror",
	 "Drama",
	 "Biography",
	 "Action",
	 "News",
	 "Talk-Show",
	 "Thriller",
	 "Western",
	 "Sci-Fi",
	 "Comedy",
	 "Adventure",
	 "War",
	 "Family",
	 "Animation",
	 "Crime",
	 "Game-Show",
	 "Documentary",
	 "Romance",
	 "Sport",
	 "Reality-TV",
	 "History",
	 "Mystery",
	 "Musical",
	 "Music",
	 "Film-Noir",
	 "Fantasy"]

	for genre in genres:
		classes[genre]=[]
		for date in dates:
			classes[genre].append(0)

	res = Movies.objects.raw('SELECT * FROM movies join reviews on(movies.title=reviews.title)join genres on(movies.title=genres.title) WHERE source = ANY(%s) AND date LIKE ANY(%s) AND genre=ANY(%s)',[sources,dates,genres])
	for x,x_date in enumerate(dates_clean):
		for r in res:
			if(x_date in r.date):
				classes[r.genre][x] += 1

	return dates_clean,classes

def get_data_by_type(date_from,date_to):
	sources = ["imdb","rottentomatoes"]
	dates =[]
	dates_clean =[]
	movie_dates = {}
	series_dates = {}
	types = ["movie","series"]
	classes = {}

	for x in range(int(date_from),int(date_to)+1):
		dates.append("%"+str(x)+"%")
		movie_dates[x] = 0
		series_dates[x] = 0 
		dates_clean.append(str(x))

	for x_type in types:
		classes[x_type]=[]
		for date in dates:
			classes[x_type].append(0)

	res = Movies.objects.raw('SELECT * FROM movies join reviews on (movies.title=reviews.title)WHERE source = ANY(%s) AND date LIKE ANY(%s) AND  movie_series IS NOT NULL',[sources,dates])
	
	for x,x_date in enumerate(dates_clean):
		for r in res:
			if(x_date in r.date):
				if(r.movie_series):
					classes["series"][x] += 1
				else:
					classes["movie"][x] += 1

	return dates_clean,classes


def get_data_by_country(date_from,date_to):
	sources = ["imdb","rottentomatoes"]
	dates =[]
	dates_clean = []
	classes = {}
	for x in range(int(date_from),int(date_to)+1):
		dates.append("%"+str(x)+"%")
		dates_clean.append(str(x))

	countries =["Soviet Union",
"Federal Republic of Yugoslavia",
"Indonesia",
"Italy",
"Luxembourg",
"Czech Republic",
"Czechoslovakia",
"Sweden",
"USA",
"Uganda",
"Dominican Republic",
"Cambodia",
"Ireland",
"Germany",
"Singapore",
"Canada",
"Uzbekistan",
"Finland",
"Portugal",
"South Korea",
"Colombia",
"Malta",
"Argentina",
"Cuba",
"Latvia",
"West Germany",
"Bahamas",
"Puerto Rico",
"India",
"Iran",
"Chile",
"France",
"Estonia",
"Israel",
"South Africa",
"Syria",
"Peru",
"Senegal",
"Malaysia",
"Iceland",
"Yugoslavia",
"Hong Kong",
"Japan",
"Denmark",
"Philippines"]

	for country in countries:
		classes[country]=[]
		for date in dates:
			classes[country].append(0)

	
	res = Movies.objects.raw('SELECT * FROM movies join reviews on(movies.title=reviews.title)join countries on(movies.title=countries.title) WHERE source = ANY(%s) AND date LIKE ANY(%s) AND country=ANY(%s)',[sources,dates,countries])
	for x,x_date in enumerate(dates_clean):
		for r in res:
			if(x_date in r.date):
				classes[r.country][x] += 1


	return dates_clean,classes

def trends(request):
	form_values = {}
	if(request.method == "GET"):
		values = 0
		dates = 0
		classes = 0
	
	if(request.method =="POST"):
		date_from = request.POST.get('from', None)
		date_to = request.POST.get('to', None)
		popularity_by = request.POST.get('popularity_by', None)
		form_values["date_from"] = date_from
		form_values["date_to"] = date_to
		form_values[popularity_by+"_selected"] = "selected"

		if(popularity_by == "movie"):
			dates,classes = get_data_by_type(date_from,date_to)#,classes
		elif(popularity_by == "genre"):
			dates,classes = get_data_by_genre(date_from,date_to)
		elif(popularity_by == "country"):
			dates,classes = get_data_by_country(date_from,date_to)
	context = {
		"form_values":form_values,
		"dates":dates,
		"classes":classes
		

	}
	return render(request,"movies/trends.html",context)

