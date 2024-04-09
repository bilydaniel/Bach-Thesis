#extracts random reviews for future manual annotation
# xbilyd01

import json
import random
import re

alphabets= "([A-Za-z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov)"

def split_into_sentences(text):
    text = " " + text + "  "
    text = text.replace("\n"," ")
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(websites,"<prd>\\1",text)
    if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
    text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
    text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
    text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
    if "”" in text: text = text.replace(".”","”.")
    if "\"" in text: text = text.replace(".\"","\".")
    if "!" in text: text = text.replace("!\"","\"!")
    if "?" in text: text = text.replace("?\"","\"?")
    #ADDED
    text = re.sub("\.+",".",text)
    text = re.sub("\!+","!",text)
    text = re.sub("\?+","?",text)
    #ADDED
    text = text.replace(".",".<stop>")
    text = text.replace("?","?<stop>")
    text = text.replace("!","!<stop>")
    text = text.replace("<prd>",".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    return sentences

def json_readr(file):
	file_lines = list(open(file, mode="r"))
	while(True):
		rand = random.randrange(0, len(file_lines))
		yield json.loads(file_lines[rand])

generator = json_readr("validate_fixed.txt")
to_json = 0

with open("random_data.txt","a") as f:
	i = 0
	while i < 40:
		json_data = next(generator)
		text_data = json_data["text"] 
		sentences = split_into_sentences(text_data)
		for sentence in sentences:
			if(to_json):
				data_dict = {	"text":sentence,
								"aspect":"none",
								"polarity":"none"
							}

		
			

				with open('random_data.txt', 'a') as file:
					json.dump(data_dict,file,ensure_ascii=False)
					file.write('\n')
			else:
				with open('to_annotate_random_data.txt', 'a') as file:
					file.write(sentence)
					file.write('\n')
		i+=1
		
		
		
