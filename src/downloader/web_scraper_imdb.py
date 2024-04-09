#scrapes data from imdb, uses selenium
# xbilyd01

from config import *
from database_manager import *
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
import json

class Web_scraper_imdb():
	def __init__(self):
		options = Options()
		options.set_headless(headless=True)
		profile = webdriver.FirefoxProfile()
		profile.set_preference('intl.accept_languages', 'en-US, en')
		self.browser = webdriver.Firefox(firefox_profile=profile,firefox_options=options, executable_path="/mnt/minerva1/nlp/projects/sentiment8/geckodriver-v0.26.0-linux64/geckodriver")
		self.html_soup = None
		self.db = Database_manager()

	def download(self):
		try:
			self.db.connect("imdb")
			#self.db.create_table()
		
			self.browser.get("https://www.imdb.com/feature/genre/?ref_=nv_ch_gr")		

			genre_urls = self.get_genres("widget_image")
			for genre_url in genre_urls:
				self.iterate_genre(genre_url)

			self.browser.quit()
		finally:
			self.db.db_close()

	def get_genres(self,name):
		genres = self.browser.find_elements_by_class_name(name)	
		genre_urls = []
		
		i = 0
		for genre in genres:
			if(i < 8):#max 14, for skipping genres
				i += 1
				continue
			genre_a = genre.find_element_by_tag_name("a")
			url = genre_a.get_property("href")
			genre_urls.append(url)
			
		
		return genre_urls

	def iterate_genre(self,genre_url):
		self.browser.get(genre_url)
		next_button_url = None

		while(True):
			
			try:
				next_button = self.browser.find_element_by_partial_link_text("Next")
				next_button_url = next_button.get_property("href")
			except Exception as e:
				next_button_url = None

			movies = self.get_movies_on_page()
			for movie in movies:
				self.find_comments(movie)
			if(next_button_url):
				self.browser.get(next_button_url)
			else:
				break

	def get_movies_on_page(self):
		movies = self.browser.find_elements_by_class_name("lister-item-header")
		movie_urls = []
	
		for movie in movies:
			movie_a = movie.find_element_by_tag_name("a")
			movie_url = movie_a.get_property("href")
			movie_urls.append(movie_url)
			
			
		return movie_urls
			
	def find_comments(self,movie):
		self.browser.get(movie)
		try:
			reviews_button = self.browser.find_element_by_partial_link_text("user reviews")
		except Exception as e:
			
			return

		self.browser.get(reviews_button.get_property("href"))	
		self.load_all_movies()
		self.download_comments()
		

	def load_all_movies(self):
		while(1):
			try:
				load_button = WebDriverWait(self.browser, 15).until(EC.element_to_be_clickable((By.ID,"load-more-trigger")))
				load_button.click()
			except Exception as e:
				break

	def download_comments(self):
		try:
			html = self.browser.page_source
		except Exception as e:
			return
				
		if(html is None):
			return
		self.html_soup = BeautifulSoup(html, "html.parser")

		title = self.get_title()
		if(title is None):
			return
		reviews = self.get_reviews()
		if(reviews is None):
			return

		for review in reviews:
			rating = review.find("span",{"class": "rating-other-user-rating"})
			if(rating):
				rating = float(rating.findChild("span").text)
				rating /= 10.
				
			user_name_wrapper = review.find("span",{"class": "display-name-link"}) 	
			if(user_name_wrapper is None):
				continue
			user_name_a = user_name_wrapper.findChild("a")
			if(user_name_a is None):
				continue
			user_name = user_name_a.text
			
			if(self.db.find_critic(title,user_name) != None):
				continue

			date = review.find("span",{"class": "review-date"}).text
			review_text = review.find("div",{"class": "content"})
			review_text = review.select('div.text.show-more__control')[0].text
			
			review_text = review_text.replace("\n","")
			review_text = review_text.replace("_","")

			self.db.save_critic(title,user_name)
			self.db.save_review(title,review_text,rating,user_name,date,"","imdb")
			'''
			data_dict = {"title":title,
						"text": review_text,
						"user_name": user_name,
						"rating":rating,
						"date":date	
						}
			with open(dir_athena + 'json_imdb.txt', 'a') as file:
				json.dump(data_dict,file,ensure_ascii=False)#, indent = 4, sort_keys = True,ensure_ascii=False
				file.write('\n')
			print(title+": "+user_name)
			'''
			
	def get_title(self):
		title = self.html_soup.find("h3",{"itemprop": "name"})
		if(title is None):
			return None
		title = (' '.join(title.text.split()))
		return title

	def get_reviews(self):
		reviews = self.html_soup.findAll("div",{"class": "lister-item-content"})
		if(reviews is None):
			return None
		
		return reviews
