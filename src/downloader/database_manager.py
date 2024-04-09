# xbilyd01
from config import *
import psycopg2

class Database_manager():
	def __init__(self):
		self.connection = None
		self.cursor = None

	def connect(self,name):
		self.name = name  

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
			

	def create_table(self):
		# if(self.name == "csfd"):
		# 	self.cursor.execute("""CREATE TABLE IF NOT EXISTS csfd(
		# 								id integer PRIMARY KEY,
		# 								total_comments integer
		# 							)""")
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
		#print("result")
		#print(result)
		#print(id)
		#print(self.cursor)

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