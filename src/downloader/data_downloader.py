# xbilyd01

import json
import requests
from web_scraper_csfd import *
from web_scraper_rottentomatoes import *
from web_scraper_imdb import *
from web_scraper_fdb import *
from config import *

class Data_downloader():
	def __init__(self, social_media):
		self.social_media = social_media
		

	def download_data(self):
		print("downloading...")

		if(self.social_media["csfd"]):
			self.download_csfd()

		if(self.social_media["imdb"]):
			self.download_imdb()	
			
		if(self.social_media["rottentomatoes"]):
			self.download_rottentomatoes()	
			
		if(self.social_media["fdb"]):
			self.download_fdb()	

	def download_csfd(self):
		print("downloading from csfd...")	
		csfd_downloader = Web_scraper_csfd()
		csfd_downloader.download()

	def download_rottentomatoes(self):
		print("downloading from rotten tomatoes...")	
		rottentomatoes_downloader = Web_scraper_rottentomatoes()
		rottentomatoes_downloader.download()
		
	def download_imdb(self):
		print("downloading from imdb...")
		imdb_downloader = Web_scraper_imdb()	
		imdb_downloader.download()


	def download_fdb(self):
		print("downloading from fdb...")
		fdb_downloader = Web_scraper_fdb()	
		fdb_downloader.download()
			
	

downloader = Data_downloader(social_media)
downloader.download_data()