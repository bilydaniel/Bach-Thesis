#downloads additional information to movies (genre, country, if its a movie or series)
# xbilyd01
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
import psycopg2
import re

#self.browser.save_screenshot('/mnt/minerva1/nlp/projects/sentiment8/Downloader/picture.png')

class Add_info_database():
	def __init__(self):
		self.connection = None
		self.cursor = None

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
			self.connection.close()
			print("PostgreSQL connection is closed")

	def create_title_get(self):
		self.title_cursor.execute("""SELECT title FROM movies WHERE language='en' AND movie_series IS NULL""")

	def title_get(self):
		data = self.title_cursor.fetchone()

		return data[0] if data else None

	def save_movieseries_originalrating(self,title,movie_series,original_rating):
		self.cursor.execute("""UPDATE movies SET movie_series=%s,original_rating=%s WHERE title=%s AND language='en'""",(movie_series,original_rating,title))
		self.connection.commit()

	def save_genres(self,title,genres):
		self.cursor.execute("""INSERT INTO genres values(%s,unnest(%s))""",(title,genres))
		self.connection.commit()


	def save_countries(self,title,countries):
		self.cursor.execute("""INSERT INTO countries values(%s,unnest(%s))""",(title,countries))
		self.connection.commit()

class Add_info_imdb():
	def __init__(self):
		options = Options()
		options.set_headless(headless=True)
		profile = webdriver.FirefoxProfile()
		profile.set_preference('intl.accept_languages', 'en-US, en')
		self.browser = webdriver.Firefox(firefox_profile=profile,firefox_options=options, executable_path="/mnt/minerva1/nlp/projects/sentiment8/geckodriver-v0.26.0-linux64/geckodriver")
		self.html_soup = None
		self.db = Add_info_database()
		self.regex_search=re.compile(r'[^\(\)0-9.IVX\s]').search
		self.original_title = None

	def download(self):
		try:
			self.db.connect()
			self.db.create_title_get()
			self.browser.get("https://www.imdb.com/")	
			self.iterate_movies()
			
		finally:
			self.db.db_close()

	def iterate_movies(self):
		movie_title = self.db.title_get()
		while (movie_title):
			self.original_title = movie_title
			#split movie title to movies name and year of release(or other information)
			bracket_index = movie_title.find("(")
			movie_title = movie_title.replace("'","\'")
			
			if(bracket_index==-1):
				movie_specs = None
				part_title = movie_title
			else:
				#clean up the title so it can be found, not found on imdb website otherwise
				part_title = movie_title[:bracket_index]
				movie_specs = movie_title[bracket_index:]
				movie_specs = movie_specs.replace(" Video","")
				movie_specs = movie_specs.replace(" TV Movie","")
				movie_specs = movie_specs.replace("(I) ","")
				movie_specs = movie_specs.replace(" TV Short","")

				
				if("–" in movie_specs):
					slash_index = movie_specs.find("–")
					movie_specs = movie_specs[:slash_index] + ")"

			#find searchbar
			self.search_bar = WebDriverWait(self.browser, 30).until(EC.presence_of_element_located((By.ID, "suggestion-search")))

			movie_url = self.search_movie(part_title,movie_specs)
			if(movie_url != None):
				self.download_data(movie_url)
				
				
			#get next tile from database
			movie_title = self.db.title_get()

	def download_data(self,movie_url):
		self.browser.get(movie_url)

		try:
			rating_wrapper = self.browser.find_element_by_class_name("ratingValue").find_element_by_xpath("//span[@itemprop=\"ratingValue\"]")
			
		except Exception as e:
			rating_wrapper = None	
		try:
			subtext_wrapper = self.browser.find_element_by_class_name("subtext")
		except Exception as e:
			print(e)
			return	

		try:
			genres_wrapper = self.browser.find_element_by_xpath("//h4[text()=\"Genres:\"]").find_element_by_xpath("./..")
		except Exception as e:
			print(e)
			return	
		
		genres_a = genres_wrapper.find_elements_by_tag_name("a")

		try:
			country_wrapper = self.browser.find_element_by_xpath("//h4[text()=\"Country:\"]").find_element_by_xpath("./..")
		except Exception as e:
			print(e)
			return
		
		countries_a = country_wrapper.find_elements_by_tag_name("a")

		genres = []
		for genre_a in genres_a:
			genres.append(genre_a.text)

		countries = []
		for country_a in countries_a:
			countries.append(country_a.text)
		if(rating_wrapper):
			original_rating = float(rating_wrapper.text)/10.
		else:
			original_rating = None
		movie_series = "Series" in subtext_wrapper.text
		
		self.db.save_movieseries_originalrating(self.original_title,movie_series,original_rating)
		self.db.save_genres(self.original_title,genres)
		self.db.save_countries(self.original_title,countries)
	
	def special_match(self,strg):
	    return not bool(self.regex_search(strg))

	def search_movie(self,part_title,movie_specs):
		part_title = part_title.strip()
		if(movie_specs != None):
			if(self.special_match(movie_specs)):
				pass
			else:
				movie_specs = None
		time.sleep(1)
		self.search_bar.send_keys(part_title)
		time.sleep(1)
		self.search_bar.send_keys(Keys.RETURN)
		time.sleep(1)
		
		
		try:
			titles = WebDriverWait(self.browser, 30).until(EC.presence_of_element_located((By.XPATH, "//h3[text()[contains(.,\"Titles\")]]"))).find_element_by_xpath("./..")
		except Exception as e:
			print("NO TITLE")
			print(part_title)
			return
		
		
		#find the correct movie (by additional information like year of release in the title)
		#if not found in the results, click on button that shows more results, tries to find it there
		try:
			if(movie_specs != None):
				search_result = titles.find_element_by_xpath("//td[text()[contains(.,\""+movie_specs+"\")]]/a[text()=\""+part_title+"\"]")#
			else:
				search_result = titles.find_element_by_xpath("//td[@class='result_text']/a[text()=\""+part_title+"\"]")
		except Exception as e:
						
			try:
				load_more = titles.find_element_by_class_name("findMoreMatches")
				load_more = load_more.find_element_by_tag_name("a")
				load_more.click()
				
				if(movie_specs != None):
					search_result = self.browser.find_element_by_xpath("//td[text()[contains(.,\""+movie_specs+"\")]]/a[text()=\""+part_title+"\"]")
				else:
					search_result = self.browser.find_element_by_xpath("//td[@class='result_text']/a[text()=\""+part_title+"\"]")
			except Exception as e:
				search_result = None
			
		if(search_result):
			print(search_result.get_property("href"))
			return search_result.get_property("href")

		return None

		
		
			


		
		

		

downloader = Add_info_imdb()
downloader.download()