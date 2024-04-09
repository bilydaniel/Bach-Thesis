#filters czech reviews, csfd contains alot of slovak reviews
# xbilyd01

import json
import cld3
def json_readr(file):
	for line in open(file, mode="r"):
		try:
			yield json.loads(line)
		except Exception as e:
			print("EXCEPTION")
			print(e)
			continue
		

generator = json_readr("json_csfd.txt")


with open("json_csfd_filtered.txt","a") as f:
	
	while (True):
		try:
			json_data = next(generator)
		except Exception as e:
			print(e)
			print(json_data)
		


		if(json_data == None):
			break
		'''	
		if(json_data["id"]==2333463):
			print("Konec")
			exit()
		'''
		language_analysis = cld3.get_language(json_data["text"])
		if(language_analysis == None):
			print(json_data)
		else:
			if(language_analysis.language =="cs"):
				json.dump(json_data,f,ensure_ascii=False)
				f.write("\n")
