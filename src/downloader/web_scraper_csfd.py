#scrapes data from csfd
# xbilyd01

from bs4 import BeautifulSoup as soup  
from urllib.request import urlopen as url_req
from config import *
import json
import csv
from database_manager_csfd import *
import http.client

class Web_scraper_csfd():
	def __init__(self):
		self.current_user = 1
		self.db = Database_manager_csfd()
		self.comments_to_download = 0

	def download(self):
		try:
			self.db.connect("csfd")
			#self.db.create_table()
			if(print_out_db):
				#self.db.select_all()
				#self.db.insert_user(1,1)
				self.db.select_all()
			else:	
				if(self.movie_name == ""):
					self.download_all()
				else:
					pass
		finally:
			self.db.close()

	def download_all(self):
		errors_returned = 0 #is the user deleted or am I too far with id?
		self.current_user = 61411
		base_url = "https://www.csfd.cz/uzivatel/"

		#cycle through the users, users are identified by number id
		#some users have their profile deleted, so the site returns an error
		#if there is more than set amount of errors, that means it downloaded all the users
		while(errors_returned < max_errors ): #max_errors  is in config.py
			user_url = base_url + str(self.current_user)
			try:
				url_client = url_req(user_url)
			except:
				errors_returned +=1
				self.current_user +=1
				#url_client.close()#TODO ???
				continue

			#resets number of errors if a user is found
			errors_returned = 0	
			url_html = url_client.read()
			url_soup = soup(url_html, "html.parser")
			url_client.close()
			
			side_bar = url_soup.find("div",{"class": "ui-sidebar-menu"})
			comments_url = user_url + "/komentare/"
				
				
			self.download_user_comments(comments_url)
			self.current_user += 1

	def download_user_comments(self,comments_url):
		while(1):
			try:
				url_client = url_req(comments_url)
				url_html = url_client.read() 
				break
			except (http.client.IncompleteRead) as e:
				continue
		
		url_soup = soup(url_html, "html.parser")
		url_client.close()


		paginator = url_soup.find("div",{"class": "paginator text"})
		if(paginator == None):
			last_page = 1
		else:
			pages = paginator.findAll("a")
			last_page = pages[-2].text
			last_page = int(last_page)

		current_page = 1
		while(current_page <= last_page):
			self.download_page(comments_url + "strana-" + str(current_page))
			current_page += 1
			
	def download_page(self,page_url):
		while(1):
			try:
				url_client = url_req(page_url)
				url_html = url_client.read()
				break
			except (http.client.IncompleteRead) as e:
				continue
		url_soup = soup(url_html, "html.parser")
		url_client.close()

		comments = url_soup.findAll("div",{"class": "post"})
		dates = url_soup.findAll("li",{"class": "date"})
		i = 0
		for comment in comments:
			title = comment.find("div",{"class": "title"})
			stars = title.find("img")
			if(stars != None):
				rating = len(stars["alt"])
			else:
				rating = 0	

			text = title.find_next_sibling().text
				
			if(rating == 0):
				title_text = title.text.replace("odpad!","").strip()
			else:
				title_text = title.text.strip()	
			
			rating = rating/5

			date = dates[i].text.replace(u'\xa0\xa0', u' ')
			date = date.split(" ")[0]
			text = text.replace("\n","")
			text = text.replace("_","")
			
			if(self.db.find_critic(title_text,self.current_user) != None):
				i += 1
				continue

			data_dict = {"title":title_text, 
						"text":text,
						"rating":rating,
						"user_id":self.current_user, 
						"date":date
						}

		#print(json.dumps(data_dict, indent = 4, sort_keys = True,ensure_ascii=False))
			self.db.save_critic(title_text,self.current_user)

			with open(dir_athena + 'json_csfd.txt', 'a') as file:
				json.dump(data_dict,file,ensure_ascii=False)#, indent = 4, sort_keys = True,ensure_ascii=False)
				file.write('\n')
			print(str(self.current_user)+": "+title_text)	
			i += 1
			#self.comments_to_download -= 1
			#if(self.comments_to_download == 0):
			#	break	

	def find_comments(self,side_bar):
		total_comments = 0
		comments = side_bar.find("a",text = "Komentáře") 
		if(comments != None):
				num_comments = comments.find_next_sibling("span").text
				num_comments = num_comments.replace("(", "")
				num_comments = num_comments.replace(")", "")
				total_comments = num_comments
		
		return total_comments
		
	
	
		

		
