#manages database connection
# xbilyd01
import psycopg2

class Database_manager():
	def __init__(self):
		self.connection = None
		self.cursor = None

	def connect(self):
		try:
			self.connection = psycopg2.connect(user = "xbilyd01", password = "dz16SwQdvu", host = "127.0.0.1", port = "5432", database = "xbilyd01")
			self.cursor = self.connection.cursor()
		except (Exception, psycopg2.Error) as error :
			print ("Error while connecting to PostgreSQL", error)
	
	def db_close(self):
		self.connection.commit() 
		self.connection.close()

		if(self.connection):
			self.cursor.close()
			self.connection.close()
			print("PostgreSQL connection is closed")

	def download_reviews(self,limit,source):
		self.cursor.execute("""SELECT id,text FROM reviews WHERE source = ANY(%s) AND analyzed = 'False' ORDER BY id ASC LIMIT %s """, (source,limit))  
		reviews = self.cursor.fetchall()
		return reviews

	def tag_analyzed(self,review_ids):
		self.cursor.execute("""UPDATE reviews SET analyzed = 'true' WHERE id = ANY(%s) """,(review_ids,))

	def reset_tag_analyzed(self):
		self.cursor.execute("""UPDATE reviews SET analyzed = 'false' WHERE analyzed = 'true'""")		

	def save_polarity(self,review_id,polarity_result, polarity_class):
		self.cursor.execute("""INSERT INTO pos_neg (review_id, predicted_value, predicted_class) VALUES(%s,%s,%s) ON CONFLICT DO NOTHING""", (review_id,polarity_result, polarity_class))	
		self.connection.commit()

	def save_class(self,review_id,predict_results,class_result):
		self.cursor.execute("""INSERT INTO classes_5 (review_id, one_star, two_star, three_star, four_star, five_star,final_rating) VALUES(%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING""", 
			(review_id,predict_results[0],predict_results[1],predict_results[2],predict_results[3],predict_results[4], class_result))	
		self.connection.commit()
		
	def save_aspects(self,review_id,aspect_results):
		self.cursor.execute("""INSERT INTO aspects VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING""", 
			(review_id,aspect_results["actor_pos"],aspect_results["actor_neg"],aspect_results["audio_video_pos"],aspect_results["audio_video_neg"],aspect_results["character_pos"],aspect_results["character_neg"],aspect_results["experience_pos"],aspect_results["experience_neg"],aspect_results["story_pos"],aspect_results["story_neg"]))	
		self.connection.commit()

	def create_table(self):
		if(self.name == "csfd"):
			self.cursor.execute("""CREATE TABLE IF NOT EXISTS csfd(
										movie text,
										critic integer
									)""")
		elif(self.name == "rottentomatoes"):
			self.cursor.execute("""CREATE TABLE IF NOT EXISTS rottentomatoes(
										movie text ,
										critic text
									)""")
		elif(self.name == "imdb"):
			self.cursor.execute("""CREATE TABLE IF NOT EXISTS imdb(
										movie text ,
										critic text
									)""")

		elif(self.name == "fdb"):
			self.cursor.execute("""CREATE TABLE IF NOT EXISTS fdb(
										movie text ,
										critic text
									)""")
		self.connection.commit()										
	
	def select_all(self):
		if(self.name == "csfd"):
			result = self.cursor.execute("""SELECT * FROM users_csfd""")

		elif(self.name == "rottentomatoes"):
			result = self.cursor.execute("""SELECT * FROM users_rottentomatoes""")
			
		elif(self.name == "imdb"):
			result = self.cursor.execute("""SELECT * FROM users_imdb""")

		print("select all")	
		print(self.cursor.fetchall())
	

	def get_comments(self, id):
		self.cursor.execute("""SELECT total_comments FROM csfd WHERE id = ?""", (id,))   
		
		result = self.cursor.fetchone()
		if(result == None):
			return 0
		return result[0]

	def insert_user(self, id, comments):
		self.cursor.execute("""INSERT OR REPLACE INTO users_csfd VALUES(?,?)""", (id,comments))	
		self.connection.commit()


	def find_critic(self,movie,critic):
		if(self.name == "rottentomatoes"):
			self.cursor.execute("""SELECT * FROM users_rottentomatoes WHERE movie = %s AND critic = %s""", (movie,critic))  
		elif(self.name == "imdb"):
			self.cursor.execute("""SELECT * FROM users_imdb WHERE movie = %s AND critic = %s""", (movie,critic))  
		elif(self.name == "fdb"):
			self.cursor.execute("""SELECT * FROM users_fdb WHERE movie = %s AND critic = %s""", (movie,critic))  
		elif(self.name == "csfd"):
			self.cursor.execute("""SELECT * FROM users_csfd WHERE movie = %s AND critic = %s""", (movie,critic))  
		result = self.cursor.fetchone()
		return result 

	def save_critic(self,movie,critic):
		if(self.name == "rottentomatoes"):
			self.cursor.execute("""INSERT INTO users_rottentomatoes VALUES(%s,%s) ON CONFLICT DO NOTHING""", (movie,critic))	
		elif(self.name == "imdb"):
			self.cursor.execute("""INSERT INTO users_imdb VALUES(%s,%s) ON CONFLICT DO NOTHING""", (movie,critic))		
		elif(self.name == "fdb"):
			self.cursor.execute("""INSERT INTO users_fdb VALUES(%s,%s) ON CONFLICT DO NOTHING""", (movie,critic))		
		elif(self.name == "csfd"):
			self.cursor.execute("""INSERT OR REPLACE INTO users_csfd VALUES(?,?)""", (movie,critic))		
		self.connection.commit()


	def save_review(self,title,text,rating,critic,date,freshness,source):
		self.cursor.execute("""INSERT INTO reviews (title,text,rating,critic,date,freshness,source) VALUES(%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING""", (title,text,rating,critic,date,freshness,source))	
		self.connection.commit()