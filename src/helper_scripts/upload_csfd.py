#data from csfd could not be downloaded directly from athena, had to download them using my computer
#this script uploads data into database
# xbilyd01

import json
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

	def save_review(self,title,text,rating,critic,date,freshness,source):
		self.cursor.execute("""INSERT INTO reviews (title,text,rating,critic,date,freshness,source) VALUES(%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING""", (title,text,rating,critic,date,freshness,source))	
		self.connection.commit()

file_name = "/mnt/minerva1/nlp/projects/sentiment8/json_csfd_filtered.txt"
db = Database_manager()
db.connect()
with open(file_name) as f:
	for i, l in enumerate(f):
		json_data = json.loads(l)
		db.save_review(json_data["title"],json_data["text"],json_data["rating"],json_data["user_id"],json_data["date"],"","csfd")