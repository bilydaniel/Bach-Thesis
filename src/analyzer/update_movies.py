#combines all analyses data for each movie
# xbilyd01
import psycopg2
import statistics

class Database_manager():
	def __init__(self):
		self.connection = None
		self.cursor = None
		self.title_cursor = None

	def connect(self):
		try:
			self.connection = psycopg2.connect(user = "xbilyd01", password = "dz16SwQdvu", host = "127.0.0.1", port = "5432", database = "xbilyd01")
			self.cursor = self.connection.cursor()
			self.title_cursor = self.connection.cursor()
		except (Exception, psycopg2.Error) as error :
			print ("Error while connecting to PostgreSQL", error)
	
	def db_close(self):
		self.connection.commit() 
		self.connection.close()

		if(self.connection):
			self.cursor.close()
			self.title_cursor.close()
			self.connection.close()
			print("PostgreSQL connection is closed")

	def save_titles(self):
		self.cursor.execute("""INSERT INTO movies(title,language)  
								SELECT DISTINCT(reviews.title), language_mapping.language FROM reviews JOIN language_mapping on reviews.source=language_mapping.source
								ON CONFLICT DO NOTHING""")
		self.connection.commit()

	def get_titles(self):
		return self.title_cursor.fetchone()
	
	def create_get_titles(self):
		self.title_cursor.execute("""SELECT DISTINCT(movies.title),movies.language FROM movies JOIN reviews ON movies.title = reviews.title WHERE reviews.analyzed='true'""")#TODO REMOVE WHERE popularity IS NULL
	


	def get_ids(self,title,language):
		self.cursor.execute("""SELECT reviews.id FROM reviews JOIN language_mapping ON reviews.source = language_mapping.source WHERE reviews.title = %s AND language_mapping.language=%s AND reviews.analyzed='true'""",(title,language))
		return self.cursor.fetchall()

	def get_popularity(self,title,language):
		self.cursor.execute("""SELECT COUNT(reviews.id) FROM reviews JOIN language_mapping ON reviews.source = language_mapping.source WHERE reviews.title = %s AND language_mapping.language=%s""",(title,language))
		return self.cursor.fetchone()	

	def get_avg_polarity(self,review_ids):
		self.cursor.execute("""SELECT AVG(polarity_mapping.value) FROM pos_neg JOIN polarity_mapping ON pos_neg.predicted_class=polarity_mapping.polarity WHERE pos_neg.review_id = ANY(%s) """,(review_ids,))
		return self.cursor.fetchone()[0]	

	def get_avg_stars(self,review_ids):
		self.cursor.execute("""SELECT AVG(star_mapping.value) FROM classes_5 JOIN star_mapping ON classes_5.final_rating=star_mapping.rating WHERE classes_5.review_id = ANY(%s) """,(review_ids,))
		return self.cursor.fetchone()[0]

	def tag_stats(self,review_ids,table_name):
		if(table_name == "pos_neg"):
			self.cursor.execute("""UPDATE pos_neg SET stat_used = 'true' WHERE review_id = ANY(%s)""",(review_ids,))
		elif(table_name == "classes"):
			self.cursor.execute("""UPDATE classes_5 SET stat_used = 'true' WHERE review_id = ANY(%s)""",(review_ids,))
		elif(table_name == "aspects"):
			self.cursor.execute("""UPDATE aspects SET stat_used = 'true' WHERE review_id = ANY(%s)""",(review_ids,))
		self.connection.commit()
		
	def get_analysis_ids(self,review_ids):
		self.cursor.execute("""SELECT review_id FROM pos_neg WHERE review_id = ANY(%s) """,(review_ids,))
		return self.cursor.fetchall()

	def special_division(self,x,y,aspect):
		if(y == 0):
			self.zeros[aspect]+=1
			return 0
		else:
			return x/y


	#avereges out all aspect score from all reviews for a certain movie
	def get_avg_aspects(self,review_ids):
		self.cursor.execute("""SELECT * FROM aspects WHERE review_id = ANY(%s) """,(review_ids,))
		review_stats = self.cursor.fetchall()

		self.zeros = {"actor":0,"audio_video":0,"character":0,"experience":0,"story":0,}	
		aspects_in_reviews = []

		for review_stat in review_stats:
			actor_avg = self.special_division(review_stat[1],review_stat[1]+review_stat[2],"actor")
			audio_video_avg = self.special_division(review_stat[3],review_stat[3]+review_stat[4],"audio_video")
			character_avg = self.special_division(review_stat[5],review_stat[5]+review_stat[6],"character")
			experience_avg = self.special_division(review_stat[7],review_stat[7]+review_stat[8],"experience")
			story_avg = self.special_division(review_stat[9],review_stat[9]+review_stat[10],"story")

			aspects_in_reviews.append([actor_avg,audio_video_avg,character_avg,experience_avg,story_avg])
			

			actor_avg = audio_video_avg = character_avg = experience_avg = story_avg = 0

		for aspect_in_review in aspects_in_reviews:
			actor_avg += aspect_in_review[0] 
			audio_video_avg += aspect_in_review[1]
			character_avg += aspect_in_review[2]
			experience_avg += aspect_in_review[3]
			story_avg += aspect_in_review[4]

		actor_avg /= len(aspects_in_reviews)-self.zeros["actor"]
		audio_video_avg /= len(aspects_in_reviews)-self.zeros["audio_video"]
		character_avg /= len(aspects_in_reviews)-self.zeros["character"]
		experience_avg /= len(aspects_in_reviews)-self.zeros["experience"]
		story_avg /= len(aspects_in_reviews)-self.zeros["story"]

		return([actor_avg,story_avg,character_avg,audio_video_avg,experience_avg])

	def update_polarity(self,avg_polarity,title,language):
		self.cursor.execute("""UPDATE movies SET avg_polarity = %s WHERE title=%s AND language=%s""",(avg_polarity,title,language))
		self.connection.commit()

	def update_popularity(self,popularity,title,language):
		self.cursor.execute("""UPDATE movies SET popularity = %s WHERE title=%s AND language=%s""",(popularity,title,language))
		self.connection.commit()

	def update_classes(self,avg_stars,title,language):
		self.cursor.execute("""UPDATE movies SET avg_stars = %s WHERE title=%s AND language=%s""",(avg_stars,title,language))
		self.connection.commit()

	def update_aspects(self,avg_aspects,title,language):
		self.cursor.execute("""UPDATE movies SET actors_score = %s,story_score = %s,characters_score = %s,audio_video_score = %s,experience_score = %s WHERE title=%s AND language=%s
								""",(avg_aspects[0],avg_aspects[1],avg_aspects[2],avg_aspects[3],avg_aspects[4],title,language))
		self.connection.commit()


	def check_stats_used(self,table_name,review_ids_arr):
		if(table_name == "pos_neg"):
			self.cursor.execute("""SELECT review_id FROM pos_neg WHERE review_id = ANY(%s) AND stat_used = 'false'""",(review_ids_arr,))
		elif(table_name == "classes"):
			self.cursor.execute("""SELECT review_id FROM classes_5 WHERE review_id = ANY(%s) AND stat_used = 'false'""",(review_ids_arr,))
		elif(table_name == "aspects"):
			self.cursor.execute("""SELECT review_id FROM aspects WHERE review_id = ANY(%s) AND stat_used = 'false'""",(review_ids_arr,))
		return self.cursor.fetchone()

	def reset_stats_used(self):
		self.cursor.execute("""UPDATE pos_neg SET stat_used = 'false'""")
		self.connection.commit()		
		self.cursor.execute("""UPDATE classes_5 SET stat_used = 'false'""")
		self.connection.commit()		
		self.cursor.execute("""UPDATE aspects SET stat_used = 'false'""")
		self.connection.commit()		

db = Database_manager()
db.connect()

args = {"save_titles":1, "save_stats":1}

#make a row in a table for each movie
if(args["save_titles"]):
	db.save_titles()

if(args["save_stats"]):
	db.create_get_titles()
	title,language = db.get_titles()

	
	
	i = 0
	while(title):
		print(title,language)
		review_ids_arr = []
		review_ids_arr = db.get_ids(title,language)
		#print(review_ids_arr)

		
		popularity = db.get_popularity(title, language)
		db.update_popularity(popularity,title,language)


		#pos_neg
		if(db.check_stats_used("pos_neg",review_ids_arr)):#TODO otestovat jestli funguje
			avg_polarity = db.get_avg_polarity(review_ids_arr)
			db.update_polarity(avg_polarity,title,language)
			db.tag_stats(review_ids_arr,"pos_neg")
		#classes
		if(db.check_stats_used("classes",review_ids_arr)):
			avg_stars = db.get_avg_stars(review_ids_arr)
			db.update_classes(avg_stars,title,language)
			db.tag_stats(review_ids_arr,"classes")

		#aspects
		if(db.check_stats_used("aspects",review_ids_arr)):
			avg_aspects = db.get_avg_aspects(review_ids_arr)
			db.update_aspects(avg_aspects,title,language)
			db.tag_stats(review_ids_arr,"aspects")
		
		get_titles_result = db.get_titles()
		if(get_titles_result):
			title,language = get_titles_result
		else:
			title = None
		
		


	