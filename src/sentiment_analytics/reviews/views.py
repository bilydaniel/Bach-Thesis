import math
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.db.models import Max, Min, Sum,F
from django.db.models.functions import Abs
from .models import Reviews
from .models import Movies
from .models import PosNeg
from .models import Classes5
from .models import Aspects
# Create your views here.
def home_view(request,*args,**kwargs):
	if('language' not in request.session):
		request.session['language'] = 'CZ'
	
	top_movies = get_top_movies(request.session['language'])
	#print(top_movies)

	if(request.session['language']=="CZ"):
		placeholder = "Hledat"
		leaderboard = "Žebříček"
	else:
		placeholder = "Search"
		leaderboard = "Leaderboard"

	context = {
	'language':request.session['language'],
	'top_movies':top_movies,
	'placeholder':placeholder,
	'leaderboard':leaderboard

	}
	return render(request,"home.html",context)

def get_top_movies(language):
	top_movies = []
	max_value = list(Movies.objects.filter(language=language.lower()).aggregate(Max('avg_polarity')).values())[0]
	best_movie = Movies.objects.filter(language=language.lower()).filter(avg_polarity=max_value)[0]

	min_value = list(Movies.objects.filter(language=language.lower()).aggregate(Min('avg_polarity')).values())[0]
	min_value = math.ceil(min_value * 100) / 100.0
	worst_movie = Movies.objects.filter(language=language.lower()).filter(avg_polarity__lte=min_value)[0]

	mid_value = list(Movies.objects.filter(language=language.lower()).aggregate(controversial=Min(Abs(F('avg_polarity')-0.5))).values())[0]
	controversial_movie = Movies.objects.filter(language=language.lower()).filter(avg_polarity__lte=mid_value+0.5)[0]
	#controversial_movie = Movies.objects.all().aggregate(controversial=Min(Abs(F('num_pos')-F('num_neg'))))

	if(language == "CZ"):
		best_movie.description = "Nejlepší Film"
		worst_movie.description = "Nejhorší Film"
		controversial_movie.description = "Nejvíce Kontroverzní Film"
	if(language == "EN"):
		best_movie.description = "The Best Movie"
		worst_movie.description = "The Worst Movie"
		controversial_movie.description = "The Most Controversial Movie"

	top_movies.append(best_movie)
	top_movies.append(worst_movie)
	top_movies.append(controversial_movie)
	return top_movies


def switch_language(request,*args,**kwargs):
	if(request.method == 'GET'):
		if("CZ" in request.GET):
			request.session['language'] = 'CZ'
		if("EN" in request.GET):
			request.session['language'] = 'EN'
		
	return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def search_results(request,*args,**kwargs):
	query = request.GET.get('q')
	dic = make_dictionary(request.session["language"])
	results = Movies.objects.filter(language=request.session["language"].lower()).filter(title__icontains=query)
	context = {
		"results":results,
		"text":dic
	}
	return render(request,"search_results.html",context)

def make_dictionary(language):
	text = {}
	if(language == "cz"):
		text["rating"] = "Hodnocení"
		text["author"] = "Autor"
		text["date"] = "Datum"
		text["source"] = "Zdroj"
		text["not_analysed"] = "Tato recenze ještě nebyla analyzována, data nenalezena."
		text["used"] = "Tato recenze byla započítána do celkového hodnocení filmu."
		text["not_used"] = "Tato recenze zatím nebyla započítána do celkového hodnocení filmu." 
		text["pol_analyser"] = "Analýza polarity"
		text["stars_analyser"] = "Analýza podle počtu hvězd"
		text["aspect_analyser"] = "Analýza aspektů[počty zmínek o jednotlivých aspektech]"
		text["predicted_value"] = "Předpověděná hodnota" 
		text["predicted_class"] = "Finální polarita předpovědi"
		text["onestar_value"] = "Předpověď jedné hvězdy"
		text["twostar_value"] = "Předpověď dvou hvězd"
		text["threestar_value"] = "Předpověď třech hvězd"
		text["fourstar_value"] = "Předpověď čtyř hvězd"
		text["fivestar_value"] = "Předpověď pěti hvězd"
		text["final_value"] =  "Finální výsledek"
		text["actor_pos"] = "herci pozitivní"
		text["actor_neg"] = "herci negativní"
		text["audio_video_pos"] = "audio-video pozitivní"
		text["audio_video_neg"] = "audio-video negativní"
		text["character_pos"] = "postavy pozitivní"
		text["character_neg"] = "postavy negativní"
		text["experience_pos"] = "zkušenost pozitivní"
		text["experience_neg"] = "zkušenost negativní"
		text["story_pos"] = "příběh pozitivní"
		text["story_neg"] = "příběh negativní"
		text["popularity"] = "Popularita"

		
	else:
		text["rating"] = "Rating"
		text["author"] = "Author"
		text["date"] = "Date"
		text["source"] = "Source"
		text["not_analysed"] = "This review has not been analysed yet, data missing."
		text["used"] = "This review was used to calculate the overall score of the movie."
		text["not_used"] = "This review was not yet used to calculate the overall score of the movie."
		text["pol_analyser"] = "Polarity analysis"
		text["stars_analyser"] = "Stars analysis"
		text["aspect_analyser"] = "Aspect analysis[numbers of positive/negative mentions of aspects]"
		text["predicted_value"] = "Predicted Value" 
		text["predicted_class"] = "Final Polarity"
		text["onestar_value"] = "One star prediction"
		text["twostar_value"] = "Two star prediction"
		text["threestar_value"] = "Three star prediction"
		text["fourstar_value"] = "Four star prediction"
		text["fivestar_value"] = "Five star prediction"
		text["final_value"] =  "Final result"
		text["actor_pos"] = "Actor positive"
		text["actor_neg"] = "Actor negative"
		text["audio_video_pos"] = "Audio-video positive"
		text["audio_video_neg"] = "Audio-video negative"
		text["character_pos"] = "Character positive"
		text["character_neg"] = "Character negative"
		text["experience_pos"] = "Experience positive"
		text["experience_neg"] = "Experience negative"
		text["story_pos"] = "Story positive"
		text["story_neg"] = "Story negative"
		text["popularity"] = "Popularity"


	return text

def review_detail(request,id, *args, **kwargs):
	language = request.session['language'].lower()
	text = make_dictionary(language)
	review = Reviews.objects.filter(id=id)[0]
	pos_neg = PosNeg.objects.filter(review_id=id).first()
	classes_5 = Classes5.objects.filter(review_id=id).first()
	aspects = Aspects.objects.filter(review_id=id).first()
	
	context={
	"id":id,
	"r":review,
	"text":text,
	"pos_neg":pos_neg,
	"classes_5":classes_5,
	"aspects":aspects
	}
	return render(request,"review_detail.html",context)
