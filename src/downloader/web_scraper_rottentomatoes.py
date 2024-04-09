#scrapes data from rotten tomatoes
# xbilyd01

from config import *
from database_manager import *
from bs4 import BeautifulSoup as soup  
from urllib.request import urlopen as url_req
import json
import time

class Web_scraper_rottentomatoes():
	def __init__(self):
		self.movie_name = None
		self.db = Database_manager()
		self.base_url = "https://www.rottentomatoes.com"
		self.num_pages = 0
		self.current_page = 1

	def download(self):
		try:
			self.db.connect("rottentomatoes")
			if(print_out_db):
				pass
				self.db.select_all()
			else:	
				if(self.movie_name == ""):
					self.download_all()
				else:
					pass
		
		finally:
			self.db.db_close()	

	def download_all(self):
		top_url = self.base_url + "/top/"
		while(True):
			try:
				url_client = url_req(top_url)
				url_html = url_client.read()
				break
			except Exception as e:
				print(e)
				time.sleep(10)
		
		url_soup = soup(url_html, "html.parser")
		url_client.close()

		genre_list = url_soup.find("ul",{"class": "genrelist"})

		genres = genre_list.findAll("a")

		for genre in genres:
			self.download_genre(genre["href"])
		
	def download_genre(self, genre):
		genre_url = self.base_url + genre 
		while(True):
			try:
				url_client = url_req(genre_url)
				url_html = url_client.read()
				break
			except Exception as e:
				print(e)
				time.sleep(10)
		
		url_soup = soup(url_html, "html.parser")
		url_client.close()	
		 
		movie_wrapers = url_soup.findAll("td")
		for movie_wraper in movie_wrapers:
			movie_url= movie_wraper.find("a",{"class": "unstyled articleLink"})
			if(movie_url != None):
				movie_url = movie_url["href"]
				self.get_pages(movie_url)

				#iterates over pages of reviews of a ceratin movie
				while self.current_page <= int(self.num_pages):
					page_url = self.base_url + movie_url + "/reviews?page=" + str(self.current_page)
					self.download_page(page_url)

					self.current_page += 1

				self.current_page = 1	

	def download_page(self,page_url):
		while(True):
			try:
				url_client = url_req(page_url)
				url_html = url_client.read()	
				break
			except Exception as e:
				print(e)
				time.sleep(10)
			
		url_soup = soup(url_html, "html.parser")
		url_client.close()		

		review_wrappers = url_soup.findAll("div",{"class":"row review_table_row"})
		title = url_soup.find("a",{"class":"unstyled articleLink","target":"_top"}).text.strip()
		for review_wrapper in review_wrappers:
			
			user_name = review_wrapper.find("div",{"class":"col-sm-13 col-xs-24 col-sm-pull-4 critic_name"}).find("a").text
			review_area = review_wrapper.find("div",{"class":"the_review"})
			review_text = review_area.text.strip()
			
			fresh = review_wrapper.find("div",{"class":"review_icon icon small fresh"})
			rotten = review_wrapper.find("div",{"class":"review_icon icon small rotten"})

			date = review_wrapper.select("div.review-date.subtle.small")[0]
			date = (' '.join(date.text.split())) #remove excesive spaces
			date = date.replace(", "," ") #remove colon
			date_split = date.split(" ")
			date_split[0], date_split[1] = date_split[1], date_split[0] #switch the order of day and month
			date = (' '.join(date_split))
			

			if(self.db.find_critic(title,user_name) != None):
				continue

			if(fresh == None):
				state = "rotten"
			elif(rotten == None):
				state = "fresh"
			else:
				state = "-"	


			normalized_rating = "-"
			rating_area = review_wrapper.find("div",{"class":"small subtle review-link"})
			if(rating_area != None):
				rating_text = rating_area.text
				if(rating_text != None):
					rating_split = rating_text.split("|")
					if(len(rating_split) > 1):
						rating = rating_split[1].split(":")[1].strip()
						normalized_rating = self.normalize_rating(rating)
						
			self.db.save_review(title,review_text,normalized_rating,user_name,date,state,"rottentomatoes")
			self.db.save_critic(title,user_name)
			#print(title+": "+user_name)
			'''
			data_dict = {"title":title,
						"text": review_text,
						"user_name": user_name,
						"rating":normalized_rating,
						"freshness":state,
						"date":date	
						}
			
			with open(dir_athena + 'json_rottentomatoes.txt', 'a') as file:
				json.dump(data_dict,file,ensure_ascii=False)#, indent = 4, sort_keys = True,
				file.write('\n')
			'''

	#returns number of pages of reviews that a movie has
	def get_pages(self,movie_url):
		reviews_url = self.base_url + movie_url + "/reviews" 
		while(True):
			try:
				url_client = url_req(reviews_url)
				url_html = url_client.read()
				break
			except Exception as e:
				print(e)
				time.sleep(10)

		
		url_soup = soup(url_html, "html.parser")
		url_client.close()

		page_info = url_soup.find("span",{"class":"pageInfo"})
		page_info_txt = page_info.text

		self.num_pages = page_info_txt.split(" ")[3]

	#people can write their own rating on rotten tomatoes, this function tries to normalize
	#the most common occurances of ratings
	def normalize_rating(self,rating):
		normalized_rating = "-"
		if(len(rating) < 3 and rating[0].isalpha()):
			score = self.rating_convert(rating[0].lower())
			if(score == "-"):
				return normalized_rating
			else:
				if(len(rating)>1):
					if(rating[1] == "+"):
						score += 1
					elif(rating[1] == "-"):
						score -= 1
					else:
						return "-"

					return score/15

				else:
					return score/15	
		elif(rating[0].isdigit() and ("/" in rating)):
			numbers = rating.split("/")
			
			try:
				x = float(numbers[0])
				y = float(numbers[1])
				return x/y
			except:
				return "-"
		return normalized_rating

	def rating_convert(self,x):
		return {
			'a': 14,
			'b': 11,
			'c': 8,
			'd': 5,
			'e': 2,
			'f': 0,
				}.get(x, "-")
			