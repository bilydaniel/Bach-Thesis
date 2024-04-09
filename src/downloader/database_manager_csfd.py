# xbilyd01
import sqlite3
from config import *
class Database_manager_csfd():
	def __init__(self):
		self.connection = None
		self.cursor = None

	def connect(self,name):
		self.name = name  
		self.connection = sqlite3.connect(dir_athena + name + ".db", timeout=10)
		self.cursor = self.connection.cursor()
	
	def close(self):
		self.connection.commit() 
		self.connection.close()
			

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
			result = self.cursor.execute("""SELECT * FROM csfd""")

		elif(self.name == "rottentomatoes"):
			result = self.cursor.execute("""SELECT * FROM rottentomatoes""")
			
		elif(self.name == "imdb"):
			result = self.cursor.execute("""SELECT * FROM imdb""")

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
		self.cursor.execute("""INSERT OR REPLACE INTO csfd VALUES(?,?)""", (id,comments))	
		self.connection.commit()


	def find_critic(self,movie,critic):
		if(self.name == "rottentomatoes"):
			self.cursor.execute("""SELECT * FROM rottentomatoes WHERE movie = ? AND critic = ?""", (movie,critic))  
		elif(self.name == "imdb"):
			self.cursor.execute("""SELECT * FROM imdb WHERE movie = ? AND critic = ?""", (movie,critic))  
		elif(self.name == "fdb"):
			self.cursor.execute("""SELECT * FROM fdb WHERE movie = ? AND critic = ?""", (movie,critic))  
		elif(self.name == "csfd"):
			self.cursor.execute("""SELECT * FROM csfd WHERE movie = ? AND critic = ?""", (movie,critic))  
		result = self.cursor.fetchone()
		return result 

	def save_critic(self,movie,critic):
		if(self.name == "rottentomatoes"):
			self.cursor.execute("""INSERT OR REPLACE INTO rottentomatoes VALUES(?,?)""", (movie,critic))	
		elif(self.name == "imdb"):
			self.cursor.execute("""INSERT OR REPLACE INTO imdb VALUES(?,?)""", (movie,critic))		
		elif(self.name == "fdb"):
			self.cursor.execute("""INSERT OR REPLACE INTO fdb VALUES(?,?)""", (movie,critic))		
		elif(self.name == "csfd"):
			self.cursor.execute("""INSERT OR REPLACE INTO csfd VALUES(?,?)""", (movie,critic))		
		self.connection.commit()
