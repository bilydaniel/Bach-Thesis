#scrapes data from fdb
# xbilyd01

from bs4 import BeautifulSoup as soup  
from urllib.request import urlopen as url_req
from config import *
import json
import csv
from database_manager import *
from datetime import date as datelib

class Web_scraper_fdb():
	def __init__(self):
		self.db = Database_manager()
		self.base_url = "https://www.fdb.cz/clenove.html?jmeno=&radit=&online=0"
		
		self.current_page = None

	def download(self):
		try:
			self.db.connect("fdb")
			
			self.download_all()
		finally:
			self.db.db_close()
				
	def download_all(self):
		self.current_page = self.base_url
		while(1):
			url_client = url_req(self.current_page)
			url_html = url_client.read()
			url_soup = soup(url_html, "html.parser")
			url_client.close()
			
			users = self.get_users(url_soup)

			for user in users:
				self.current_page = user
				self.iterate_comms()

			if(not self.get_next_users(url_soup)):
				break

	def get_users(self,url_soup):
			tables = url_soup.findAll("div",{"class": "clenDetailTabulka"})	
			users_urls = []

			for table in tables:
				comm_wrapper = table.findAll("li")[2]
				comm_url = comm_wrapper.find("a").get("href")
				comm_url = comm_url.replace(".","https://www.fdb.cz",1)
				users_urls.append(comm_url)

			
			return users_urls

	def get_next_users(self,url_soup):
		next_button = url_soup.find("a",{"class":"next page-numbers"})
		
		if(next_button):
			partial_url = next_button.get("href")
			self.current_page = partial_url.replace(".",self.base_url,1)
			return True
		else:
			return False

	def iterate_comms(self):
		while(1):
			#print(self.current_page)
			url_client = url_req(self.current_page)
			url_html = url_client.read()
			url_soup = soup(url_html, "html.parser")
			url_client.close()
			
			comments = self.get_comments(url_soup)

			if(not self.get_next_comments(url_soup)):
				break

	def get_comments(self, url_soup):
		user = url_soup.find("div",{"class":"clenDetailPopis"}).find("a").text

		titles = []
		film_wrappers = url_soup.findAll("div",{"class":"film"})
		for film_wrapper in film_wrappers:
			title = film_wrapper.find("a").get("title")
			titles.append(title)
		
		texts = []
		text_wrappers = url_soup.findAll("div",{"class":"komentar"})
		for text_wrapper in text_wrappers:
			text = text_wrapper.text.replace(" \xa0 "," ")
			text = text.replace("\r\n","")
			
			texts.append(text)

		ratings = []
		rating_wrappers = url_soup.findAll("div",{"class":"cols"})
		for rating_wrapper in rating_wrappers:
			rating = rating_wrapper.text.replace("Hodnocení: ","")
			if(rating == "\xa0"):
				ratings.append("-")
			else:
				number = int(rating.split("/")[0])
				rating = float(number)/10.
				ratings.append(rating)
		dates = []
		date_wrappers = url_soup.findAll("div",{"class":"pridano"})
		for date_wrapper in date_wrappers:
			date = date_wrapper.text.replace("Přidáno: ","")
			dates.append(date)

		for i in range(len(titles)):
			if(self.db.find_critic(titles[i],user) != None):
				continue
			texts[i] = texts[i].replace("\n","")
			
			
			if("dnes" in dates[i]):
				today_date = datelib.today()
				dates[i] = str(today_date.day)+"."+str(today_date.month)+"."+str(today_date.year)
				

			self.db.save_review(titles[i],texts[i],ratings[i],user,dates[i],"","fdb")
			self.db.save_critic(titles[i],user)
			
		#print(user)	
		'''
				
			data_dict = {"title":titles[i], 
						"text":texts[i],
						"rating":ratings[i],
						"user_name":user, 
						"date":dates[i]
						}

			

			with open(dir_athena + 'json_fdb.txt', 'a') as file:
				json.dump(data_dict,file,ensure_ascii=False)#, indent = 4, sort_keys = True,ensure_ascii=False)
				file.write('\n')
			print(titles[i]+": "+user)
			'''
	def get_next_comments(self,url_soup):
		next_button = url_soup.find("a",{"class":"next page-numbers"})
		
		if(next_button):
			partial_url = next_button.get("href")
			#print(partial_url)
			self.current_page = partial_url.replace("./..","https://www.fdb.cz",1)
			return True
		else:
			return False
