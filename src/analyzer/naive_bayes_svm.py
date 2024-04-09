#analyzes reviews, does polarity analysis, class analysis(1-5 stars) and aspect analysis
#naive bayes classifier, SVM
# xbilyd01

import json
import nltk
import unidecode
import spacy
import random
import nltk.classify
from sklearn.svm import LinearSVC
from nltk.stem import WordNetLemmatizer 
from corpy.morphodita import Tagger
import pickle

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

#implements both polarity analysis and 1-5 stars analysis
class Polarity_analyzer():
	def __init__(self):
		#set language, cz or en
		self.language = "en"
		self.FILE_PREFIX = "/mnt/minerva1/nlp/projects/sentiment8/analyzer/"

		#number of training examples for each class
		self.each_class_size = 20000
		self.most_common_words = 13000
		self.train_split = 10000

		#method of prediction
		#svm or bayes
		#self.method = "svm"
		self.method = "bayes" 
		#False = Polarity analysis
		#True = 1-5 stars analysis
		self.stars = False

		if(self.stars):
			self.model_postfix = "stars"
		else:
			self.model_postfix = "polarity"

	def train_analyzer(self):
		if(self.stars):
			self.data = self.load_stars_data()
		else:
			self.data = self.load_data()	
		
		random.shuffle(self.data)
		self.word_features = self.make_word_features(self.data)

		save_features = open(self.FILE_PREFIX+'bin/'+self.language+'/'+self.method+'/'+self.model_postfix+'_features.pickle',"wb")
		pickle.dump(self.word_features,save_features)
		save_features.close()

		feature_sets = []
		for x in self.data:
			feature_sets.append((self.find_features(x[0]),x[1]))


		training_data = feature_sets[:self.train_split] 
		testing_data = feature_sets[self.train_split:]

				

		'''
		if(self.method == "bayes"):
			classifier = nltk.NaiveBayesClassifier.train(training_data)
		else:
			classifier = nltk.classify.SklearnClassifier(LinearSVC()).train(training_data)
		'''
		classifier_b = nltk.NaiveBayesClassifier.train(training_data)
		print(nltk.classify.accuracy(classifier_b,testing_data))
		print(classifier_b.show_most_informative_features(100))
		#save classifier
		save_classifier = open(self.FILE_PREFIX+'bin/'+self.language+'/'+"bayes"+'/'+self.model_postfix+'.pickle',"wb")
		pickle.dump(classifier_b,save_classifier)
		save_classifier.close()
		classifier_b = None
		
		classifier_s = nltk.classify.SklearnClassifier(LinearSVC(dual=False)).train(training_data)
		print(nltk.classify.accuracy(classifier_s,testing_data))
		save_classifier = open(self.FILE_PREFIX+'bin/'+self.language+'/'+"svm"+'/'+self.model_postfix+'.pickle',"wb")
		pickle.dump(classifier_s,save_classifier)
		save_classifier.close()
		
		'''	
		if(self.method == "bayes"):
			print(classifier_b.show_most_informative_features(100))
		'''
	#finds all learned words in a document
	def find_features(self, doc):
		words = set(doc)
		features = {}
		for w in self.word_features:
			features[w]= (w in words)

		return features

	#makes a list of most common words in the training examples
	def make_word_features(self,data):
		all_words = []
		for x in data:
			all_words.extend(x[0])

		all_words = nltk.FreqDist(all_words) 
		word_features = []
		for i in all_words.most_common(self.most_common_words):#10_000
			word_features.append(i[0])

		return word_features

	def load_data(self):
		data = []
		classes = {"pos":0,"neg":0}
		with open(self.FILE_PREFIX+"data/"+self.language+"/train.txt") as f:
			for i,line in enumerate(f):
				json_data = json.loads(line)
				if(float(json_data["rating"]) > 0.5 and classes["pos"] != self.each_class_size):
					classes["pos"] += 1	
					data.append((self.preprocess_data(json_data["text"]),"pos"))
				if(float(json_data["rating"]) <= 0.5 and classes["neg"] != self.each_class_size):
					classes["neg"] += 1
					data.append((self.preprocess_data(json_data["text"]),"neg"))
			return data

	def load_stars_data(self):
		data = []
		classes = {"one_star":0,"two_star":0,"three_star":0,"four_star":0,"five_star":0}
		with open(self.FILE_PREFIX+"data/"+self.language+"/train.txt") as f:
			for i,line in enumerate(f):
				json_data = json.loads(line)
				if(float(json_data["rating"]) <= 0.2 and classes["one_star"] != self.each_class_size):
					classes["one_star"] += 1	
					data.append((self.preprocess_data(json_data["text"]),"one_star"))
				elif(float(json_data["rating"]) <= 0.4 and classes["two_star"] != self.each_class_size):
					classes["two_star"] += 1
					data.append((self.preprocess_data(json_data["text"]),"two_star"))
				elif(float(json_data["rating"]) <= 0.6 and classes["three_star"] != self.each_class_size):
					classes["three_star"] += 1
					data.append((self.preprocess_data(json_data["text"]),"three_star"))
				elif(float(json_data["rating"]) <= 0.8 and classes["four_star"] != self.each_class_size):
					classes["four_star"] += 1
					data.append((self.preprocess_data(json_data["text"]),"four_star"))
				elif(float(json_data["rating"]) <= 1.0 and classes["five_star"] != self.each_class_size):
					classes["five_star"] += 1
					data.append((self.preprocess_data(json_data["text"]),"five_star"))
					
			return data

	def preprocess_data(self,data):
		if(self.language=="cz"):
			tokens = nltk.word_tokenize(data,language="czech")
			for i,word in enumerate(tokens):
				tokens[i] = unidecode.unidecode(word.lower())
			return tokens

		else:
			global nlp
			doc = nlp(data)
			tokens = []
			for token in doc:
				tokens.append(token.text.lower())

			return tokens

	def crossdomain_test(self):
		print("CROSSING")
		test_file = self.FILE_PREFIX + "data/crossdomain/reviews_Musical_Instruments_5.json"
		bayes_path = self.FILE_PREFIX + "bin/" + self.language + "/bayes/polarity.pickle"
		svm_path = self.FILE_PREFIX + "bin/" + self.language + "/svm/polarity.pickle"
		features_path = self.FILE_PREFIX + "bin/" + self.language + "/bayes/polarity_features.pickle"

		classifier_b = pickle.load(open(bayes_path,"rb"))
		classifier_s = pickle.load(open(svm_path,"rb"))
		self.word_features = pickle.load(open(features_path,"rb"))
		polarity_mapping = {"p":"pos","n":"neg"}

		data = []
		with open(test_file,"r") as f:
			for line in f:
				json_data = json.loads(line)
				if(json_data["overall"]>2.5):
					res_polarity = "pos"
				else:
					res_polarity = "neg"

				data.append((self.preprocess_data(json_data["reviewText"]),res_polarity))
		
		feature_sets = []
		for x in data:
			feature_sets.append((self.find_features(x[0]),x[1]))


		print(nltk.classify.accuracy(classifier_b,feature_sets))
		print(nltk.classify.accuracy(classifier_s,feature_sets))
				
				

			

# saves pytorch models and fields for each aspect
# each aspect has an aspect model (predicts if the aspect is present in a sentence)
# and polarity model (predicts polarity of given aspect)
class Aspect_wrapper():
    def __init__(self, aspect_model, pos_neg_model,aspect_features,polarity_features):
        self.aspect_model = aspect_model
        self.pos_neg_model = pos_neg_model
        self.aspect_features = aspect_features
        self.polarity_features = polarity_features
        			

class Aspect_analyzer():
	def __init__(self):
		#cz or en
		self.language = "cz"
		self.FILE_PREFIX = "/mnt/minerva1/nlp/projects/sentiment8/analyzer/"
		#svm or bayes
		self.method = "bayes"
	
	def train_all_analyzers(self):
		trained_aspects = ["actor", "audio_video", "character", "experience", "story"]
		polarity_flags = [True, False] #models for determining aspect occurance (False) and its polarity (True)
		
		for trained_aspect in trained_aspects:
			for polarity_flag in polarity_flags:
				self.curr_aspect = trained_aspect
				self.curr_polarity = polarity_flag

				
				if(self.curr_polarity):
					self.model_postfix = "_pos_neg"
				else:
					self.model_postfix = "_aspect"
			
				self.train_analyzer()

	#makes a vocabulary
	def make_word_features(self,data):
		all_words = []
		for x in data:
			all_words.extend(x[0])

		all_words = nltk.FreqDist(all_words) 
		word_features = []
		for i in all_words:
			word_features.append(i[0])
		return word_features

	#find learned word in a document
	def find_features(self, doc):
		words = set(doc)
		features = {}
		for w in self.word_features:
			features[w]= (w in words)

		return features

	def train_analyzer(self):
		data = self.load_data()
		random.shuffle(data)
		self.word_features = self.make_word_features(data)

		save_features = open(self.FILE_PREFIX+'bin/'+self.language+'/'+self.method+'/'+self.curr_aspect+self.model_postfix+'_features.pickle',"wb")
		pickle.dump(self.word_features,save_features)
		save_features.close()

		feature_sets = []
		for x in data:
			feature_sets.append((self.find_features(x[0]),x[1]))

		training_data = feature_sets

		if(self.method == "bayes"):
			classifier = nltk.NaiveBayesClassifier.train(training_data)
		else:
			classifier = nltk.classify.SklearnClassifier(LinearSVC()).train(training_data)


		save_classifier = open(self.FILE_PREFIX+'bin/'+self.language+'/'+self.method+'/'+self.curr_aspect+self.model_postfix+'.pickle',"wb")
		pickle.dump(classifier,save_classifier)
		save_classifier.close()

	def load_data(self):
		data = []
		with open(self.FILE_PREFIX+"data/"+self.language+"/" + self.curr_aspect+self.model_postfix + ".txt") as f:
			for i,line in enumerate(f):
				json_data = json.loads(line)
				
				if(self.curr_polarity):
					data.append((self.preprocess_data(json_data["text"]),json_data["polarity"]))
				else:
					data.append((self.preprocess_data(json_data["text"]),json_data["aspect"]))
			return data

	def preprocess_data(self,data):
		if(self.language=="cz"):
			global tagger
			tokens = nltk.word_tokenize(data,language="czech")
			for i,word in enumerate(tokens):
				tokens[i] = unidecode.unidecode(word.lower())
				token = list(tagger.tag(tokens[i]))
				tokens[i] = token[0].lemma
			return tokens


		else:
			global nlp
			global lemmatizer
			doc = nlp(data)
			tokens = []
			for token in doc:
				tokens.append(lemmatizer.lemmatize(token.text.lower()))

			return tokens

	def predict_sentiment(self,model, review,features):
	    tokenized = self.preprocess_data(review)
	    self.word_features = features
	    review_features = self.find_features(review)
	    prediction = model.classify(review_features)

	    return prediction	
	

	def analyze(self,review):
		self.load_models()
		sentences = sentence_splitter(review,self.language)
		review_aspects = {"actor_pos":0,"actor_neg":0,"audio_video_pos":0,"audio_video_neg":0,"character_pos":0,
							"character_neg":0,"experience_pos":0,"experience_neg":0,"story_pos":0,"story_neg":0}

		for sentence in sentences:
			print(sentence)
			for aspect_type in self.aspect_types:
				print(aspect_type)
				aspect_result = self.predict_sentiment(self.aspect_wrappers[aspect_type].aspect_model,sentence,self.aspect_wrappers[aspect_type].aspect_features)
				print(aspect_result)
				
				if(aspect_result != "none"):
					polarity_result = self.predict_sentiment(self.aspect_wrappers[aspect_type].pos_neg_model,sentence,self.aspect_wrappers[aspect_type].polarity_features)
					print(polarity_result)
				print("**************************")

	def load_models(self):
		self.MODELS_PATH = self.FILE_PREFIX + "bin/"+self.language+"/"+self.method+"/"
		self.aspect_types = ["actor", "audio_video", "character", "experience", "story"]
		self.aspect_wrappers = {}

		for aspect_type in self.aspect_types:
			aspect_model_path = self.MODELS_PATH + aspect_type + "_aspect.pickle"
			pos_neg_model_path = self.MODELS_PATH + aspect_type + "_pos_neg.pickle"
			feature_path_aspect = self.MODELS_PATH + aspect_type + "_aspect_features.pickle"
			feature_path_polarity = self.MODELS_PATH + aspect_type + "_pos_neg_features.pickle"

			aspect_model = pickle.load(open(aspect_model_path,"rb"))
			pos_neg_model = pickle.load(open(pos_neg_model_path,"rb"))
			aspect_features = pickle.load(open(feature_path_aspect,"rb"))
			polarity_features = pickle.load(open(feature_path_polarity,"rb"))
			aspect_obj = Aspect_wrapper(aspect_model,pos_neg_model,aspect_features,polarity_features)
			self.aspect_wrappers[aspect_type] = aspect_obj


#polar_analyzer = Polarity_analyzer()
#polar_analyzer.crossdomain_test()
#polar_analyzer.train_analyzer()

#aspect_analyzer = Aspect_analyzer()

#aspect_analyzer.train_all_analyzers()
#aspect_analyzer.analyze("The actors were awesome. I didn't like the story.")
