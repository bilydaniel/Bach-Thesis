#extracts data from brat annotations, saves as json
#https://brat.nlplab.org/
# xbilyd01
import re
import json


previous_text = ""
with open("czech_annotated.txt","r") as f:
	for line in f:
		data = re.findall('\s+(.*)\s\d+\s\d+;?\d*\s?\d*\s+(.*)', line)
		#data = re.findall('\s+(.*)\s\d+\s\d+\s+(.*)', line)

		print(data)
		if(data == None):
			exit()
		annotation = data[0][0]
		
		aspect = annotation.split("_")[0]
		polarity = annotation.split("_")[1]
		text = data[0][1]

		#TODO preprocess the text a bit
		
		if(aspect == "audio" or aspect == "video"):
			aspect = "audio_video"

		data_dict = {	"text":text,
						"aspect":aspect,
						"polarity":polarity
					}

		
			

		with open('annotated_czech_json.txt', 'a') as file:
			json.dump(data_dict,file,ensure_ascii=False)
			file.write('\n')



		print(annotation)
		print(text)