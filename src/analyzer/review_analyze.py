#analyzes reviews, does polarity analysis, class analysis(1-5 stars) and aspect analysis
#neural network
# xbilyd01

import database_manager
import torch
import re
import nltk
import spacy
import unidecode
from nltk.stem import WordNetLemmatizer 
from corpy.morphodita import Tagger
import json

#libraries for lemmatization and tokenizing
nlp = spacy.load('en')
lemmatizer = WordNetLemmatizer() 
tagger = Tagger("/mnt/minerva1/nlp/projects/sentiment8/analyzer/data/czech-morfflex-pdt-161115/czech-morfflex-pdt-161115.tagger")

#splits document into sentences
def sentence_splitter(review,language):
	if(language == "en"):
		doc = nlp(review)
		sents = doc.sents
		result = []
		for sent in sents:
			result.append(sent.text)
		return result
	else:
		return nltk.sent_tokenize(review,language="czech")


def aspect_preprocess(x):
	return x
    
def polarity_preprocess(x):
    return x.lower()

#splits document into words
def tokenizer(review,language):
	if(language=="cz"):
		return nltk.word_tokenize(review,language="czech")
	else:
		global nlp
		doc = nlp(review)
		result = []
		for token in doc:
			result.append(token.text)
		return result

#returns list of tokens (words), made from czech text
def nltk_tokenizer(text):
	return nltk.word_tokenize(text,language="czech")

#text preprocessor, takes tokens (words) as input
def text_preprocess(incoming_list):
	for i,word in enumerate(incoming_list):
		incoming_list[i] = word.lower()
	 
	return incoming_list

#czech text preprocessor, takes tokens (words) as input
def text_preprocess_cz(incoming_list):
	for i,word in enumerate(incoming_list):
		incoming_list[i] = unidecode.unidecode(word.lower())
		

	return incoming_list

def aspect_text_preprocess_cz(incoming_list):
	global tagger
	for i,word in enumerate(incoming_list):
		incoming_list[i] = unidecode.unidecode(word.lower())
		#TODO finish
		token = list(tagger.tag(incoming_list[i]))
		incoming_list[i] = token[0].lemma

	return incoming_list

def aspect_text_preprocess(incoming_list):
	global lemmatizer
	for i,word in enumerate(incoming_list):
		incoming_list[i] = lemmatizer.lemmatize(word.lower())

	return incoming_list

#splits ratings into positive and negative classes
def polarity_label_preprocess(incoming_list):#
	if(float(incoming_list) <= 0.5):
		return "neg"
	else:
		return "pos"

#label preprocessor, splits ratings into 5 categories 
def class_label_preprocess(incoming_list):#
	if(float(incoming_list)<=0.2):
		return "one_star"
	elif(float(incoming_list)<=0.4):
		return "two_star"
	elif(float(incoming_list)<=0.6):
		return "three_star"
	elif(float(incoming_list)<=0.8):
		return "four_star"
	elif(float(incoming_list)<=1.0):
		return "five_star"

#maps database column to list index
columns = {"id":0,"text":1}
def column(name):
	return columns[name]

class Polarity_analysis():
	def __init__(self,language):
		print("init")
		self.language = language

		#loads model and pytorch fields
		self.FILE_PREFIX = "/mnt/minerva1/nlp/projects/sentiment8/analyzer/"
		self.model = torch.load(self.FILE_PREFIX + "/bin/"+self.language+"/polarity_analyzer/polarity_model.pt",map_location=torch.device('cpu'))
		self.text = torch.load(self.FILE_PREFIX + "/bin/"+self.language+"/polarity_analyzer/text_field.pt",map_location=torch.device('cpu'))
		self.label = torch.load(self.FILE_PREFIX + "/bin/"+self.language+"/polarity_analyzer/label_field.pt",map_location=torch.device('cpu'))
		print("init")

	#predicts sentiment of a document
	def predict_sentiment(self, review):
	    self.model.eval()
	    #tokenize the document into words
	    tokenized = tokenizer(review,self.language)

	    #preprocess the words
	    if(self.language =="cz"):
	    	tokenized = text_preprocess_cz(tokenized)
	    else:
	    	tokenized = text_preprocess(tokenized)

	    #indexes the tokenized words using loaded pytorch field	
	    indexed = [self.text.vocab.stoi[t] for t in tokenized]
	    length = [len(indexed)]
	    tensor = torch.LongTensor(indexed)#.to(device)
	    tensor = tensor.unsqueeze(1)
	    length_tensor = torch.LongTensor(length)

	    #makes a prediction using loaded model
	    prediction = torch.sigmoid(self.model(tensor, length_tensor))
	    return prediction.item()
	
	def analyze(self,review):
		polarity_result = self.predict_sentiment(review)
		rounded_polarity = round(polarity_result)

		#gets the predicted class (pos/neg) using loaded pytorch field
		polarity_class = self.label.vocab.itos[rounded_polarity]
		return polarity_result,polarity_class

	def crossdomain_test(self):
		print("CROSSING")
		test_file = self.FILE_PREFIX + "data/crossdomain/reviews_Automotive_5.json"
		i = 0
		correct = 0
		with open(test_file,"r") as f:
			for line in f:
				if(i % 1000 == 0 and i != 0):
					print(float(correct)/i)
				#print(i)
				json_data = json.loads(line)
				#print(json_data)
				polarity_result = self.predict_sentiment(json_data["reviewText"])#json_data["text"]
				rounded_polarity = round(polarity_result)
				polarity_class = self.label.vocab.itos[rounded_polarity]
				if(polarity_class == "pos" and json_data["overall"] > 2.5):
					correct += 1
				elif(polarity_class == "neg" and json_data["overall"]<= 2.5):
					correct += 1
				'''
				if(json_data["rating"] in polarity_class):    #json data p/n result from analysis pos/neg
					correct += 1
				'''
				i += 1

			print(float(correct)/i)
		

class Class_analysis():
	def __init__(self,language):
		self.language = language
		self.FILE_PREFIX = "/mnt/minerva1/nlp/projects/sentiment8/analyzer/"

		#loads model and pytorch fields
		self.model = torch.load(self.FILE_PREFIX + "/bin/"+self.language+"/class_analyzer/class_model.pt",map_location=torch.device('cpu'))
		self.text = torch.load(self.FILE_PREFIX + "/bin/"+self.language+"/class_analyzer/text_field.pt",map_location=torch.device('cpu'))
		self.label = torch.load(self.FILE_PREFIX + "/bin/"+self.language+"/class_analyzer/label_field.pt",map_location=torch.device('cpu'))
		self.class_list = ["one_star","two_star","three_star","four_star","five_star"]


	def predict_class(self,review):
		self.model.eval()

		#tokenize the document into words
		tokenized = tokenizer(review,self.language)

		#preprocess the words
		if(self.language =="cz"):
			tokenized = text_preprocess_cz(tokenized)
		else:
			tokenized = text_preprocess(tokenized)

		#indexes the tokenized words using loaded pytorch field
		indexed = [self.text.vocab.stoi[t] for t in tokenized]
		length = [len(indexed)]
		tensor = torch.LongTensor(indexed)
		tensor = tensor.unsqueeze(1)
		length_tensor = torch.LongTensor(length)
		#makes a prediction using loaded model
		prediction = self.model(tensor, length_tensor)
		return prediction
		

	def analyze(self,review):
		predict_result = self.predict_class(review)
		class_result = predict_result[0]
		
		result = []
		for c in self.class_list:
			result.append(class_result[self.label.vocab.stoi[c]].item())

		#gets the class with biggest prediction value
		max_prediction = predict_result.argmax(dim=1)
		return result,self.label.vocab.itos[max_prediction.item()]

# saves pytorch models and fields for each aspect
# each aspect has an aspect model (predicts if the aspect is present in a sentence)
# and polarity model (predicts polarity of given aspect)
class Aspect_wrapper():
    def __init__(self, aspect_model, pos_neg_model, aspect_text_field,
        aspect_aspect_field, polarity_text_field, polarity_polarity_field):

        self.aspect_model = aspect_model
        self.pos_neg_model = pos_neg_model
        self.aspect_text_field = aspect_text_field
        self.aspect_aspect_field = aspect_aspect_field
        self.polarity_text_field = polarity_text_field
        self.polarity_polarity_field = polarity_polarity_field		

class Aspect_analysis():
	def __init__(self,language):
		self.language = language
		self.FILE_PREFIX = "/mnt/minerva1/nlp/projects/sentiment8/analyzer/"

		#loads models and pytorch fields for each aspect,
		self.MODELS_PATH = self.FILE_PREFIX + "bin/"+self.language+"/aspect_analyzer/"
		self.aspect_types = ["actor", "audio_video", "character", "experience", "story"]
		self.aspect_wrappers = {}

		for aspect_type in self.aspect_types:
			aspect_model_path = self.MODELS_PATH + aspect_type + "_aspect.pt"
			pos_neg_model_path = self.MODELS_PATH + aspect_type + "_pos_neg.pt"

			tmp_aspect_model = torch.load(aspect_model_path,map_location=torch.device('cpu'))
			tmp_pos_neg_model = torch.load(pos_neg_model_path,map_location=torch.device('cpu'))

			tmp_aspect_model.eval()
			tmp_pos_neg_model.eval()

			aspect_txt_field = torch.load(self.MODELS_PATH+aspect_type+"_aspect_textfield",map_location=torch.device('cpu'))
			aspect_aspect_field = torch.load(self.MODELS_PATH+aspect_type+"_aspect_aspectfield",map_location=torch.device('cpu'))

			pos_neg_txt_field = torch.load(self.MODELS_PATH+aspect_type+"_pos_neg_textfield",map_location=torch.device('cpu'))
			pos_neg_polarity_field = torch.load(self.MODELS_PATH+aspect_type+"_pos_neg_polarityfield",map_location=torch.device('cpu'))

			#aspect_model, pos_neg_mdoel, aspect_text_field,aspect_aspect_field, polarity_text_field,polarity_polarity_field
			aspect_obj = Aspect_wrapper(tmp_aspect_model,tmp_pos_neg_model,
			aspect_txt_field,aspect_aspect_field,pos_neg_txt_field,pos_neg_polarity_field)

			self.aspect_wrappers[aspect_type] = aspect_obj
	
	def predict_sentiment(self,model, review,text):
	    model.eval()
	    # tokenizes to words
	    tokenized = tokenizer(review,self.language)

	    #preprocess the words
	    if(self.language == "en"):
	    	tokenized = aspect_text_preprocess(tokenized)
	    else:
	    	tokenized = aspect_text_preprocess_cz(tokenized)

	    #indexes the tokenized words using loaded pytorch field	
	    indexed = [text.vocab.stoi[t] for t in tokenized]

	    length = [len(indexed)]
	    tensor = torch.LongTensor(indexed)
	    tensor = tensor.unsqueeze(1)
	    length_tensor = torch.LongTensor(length)
	    prediction = torch.sigmoid(model(tensor, length_tensor))
	    return prediction.item()

	def analyze(self,review):
		#splits review into sentences
		sentences = sentence_splitter(review,self.language)
		
		#keeps overall score of aspects in a given review		
		review_aspects = {"actor_pos":0,"actor_neg":0,"audio_video_pos":0,"audio_video_neg":0,"character_pos":0,
							"character_neg":0,"experience_pos":0,"experience_neg":0,"story_pos":0,"story_neg":0}
		for sentence in sentences:
			for aspect_type in self.aspect_types:
				#each sentence is analyzed against each aspect
				aspect_result = self.predict_sentiment(self.aspect_wrappers[aspect_type].aspect_model,
													sentence, 
													self.aspect_wrappers[aspect_type].aspect_text_field
													)
				

				round_aspect_result = round(aspect_result)

				#if aspect is found, its polarity is predicted
				round_polarity_result = None
				if(self.aspect_wrappers[aspect_type].aspect_aspect_field.vocab.itos[round_aspect_result] != "none"):
					polarity_result = self.predict_sentiment(self.aspect_wrappers[aspect_type].pos_neg_model,
					sentence, 
					self.aspect_wrappers[aspect_type].polarity_text_field)
					
					round_polarity_result = round(polarity_result)

					if (self.aspect_wrappers[aspect_type].polarity_polarity_field.vocab.itos[round_polarity_result] == "pos"):
						review_aspects[aspect_type+"_pos"] += 1
					else:
						review_aspects[aspect_type+"_neg"] += 1
				
		return review_aspects			


pol = Polarity_analysis("en")
#pol.crossdomain_test()


db = database_manager.Database_manager()
db.connect()
#language = "cz"
language = "en"
if(language == "en"):
	source = ["imdb","rottentomatoes"]
else:
	source = ["csfd","fdb"]
limit = 100



analyses = {"polarity":1, "class":1, "aspect":1}
if(analyses["polarity"]):
	polarity_analysis = Polarity_analysis(language)
if(analyses["class"]):
	class_analysis = Class_analysis(language)
if(analyses["aspect"]):
	aspect_analysis = Aspect_analysis(language)


while(True):
	reviews = db.download_reviews(limit,source)


	review_ids = []
	for review in reviews:
		review_id = review[column("id")]
		review_ids.append(review_id)

		#polarity analysis
		if(analyses["polarity"]):
			polarity_result,polarity_class = polarity_analysis.analyze(review[column("text")])
			db.save_polarity(str(review_id),str(polarity_result),str(polarity_class))
		
		#class analysis
		if(analyses["class"]):
			predict_results,class_result = class_analysis.analyze(review[column("text")])
			db.save_class(review_id,predict_results,class_result)
		#aspect analysis
		if(analyses["aspect"]):
			aspect_results = aspect_analysis.analyze(review[column("text")])
			db.save_aspects(review_id,aspect_results)


	#db.reset_tag_analyzed()
	db.tag_analyzed(review_ids)

