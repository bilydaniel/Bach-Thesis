#Trains aspect analyzer model, neural network
# xbilyd01
from models import rnn_model
import torch
from torchtext import data
import time
import torch.optim as optim
import torch.nn as nn
import nltk
import unidecode
import spacy
from nltk.stem import WordNetLemmatizer 
from corpy.morphodita import Tagger
from pprint import pprint

#libraries for lemmatization
lemmatizer = WordNetLemmatizer() 
tagger = Tagger("/mnt/minerva1/nlp/projects/sentiment8/analyzer/data/czech-morfflex-pdt-161115/czech-morfflex-pdt-161115.tagger")

#returns list of tokens (words), made from czech text
def nltk_tokenizer(text):
	return nltk.word_tokenize(text,language="czech")

#measures time, mainly used for measuring training
def epoch_time(start_time, end_time):
	elapsed_time = end_time - start_time
	elapsed_mins = int(elapsed_time / 60)
	elapsed_secs = int(elapsed_time - (elapsed_mins * 60))
	return elapsed_mins, elapsed_secs

#preprocessor of aspect tag
def aspect_preprocess(x):
	return x

#preprocessor of polarity tag
def polarity_preprocess(x):
    return x.lower()

#czech text preprocessor, takes tokens (words) as input
def aspect_text_preprocess_cz(incoming_list):
	global tagger
	for i,word in enumerate(incoming_list):

		#removes diacritics from each token, lowers each token
		incoming_list[i] = unidecode.unidecode(word.lower())
		
		#lemmatizes each token
		token = list(tagger.tag(incoming_list[i]))
		incoming_list[i] = token[0].lemma

	return incoming_list

#english text preprocessor, takes tokens (words) as input
def aspect_text_preprocess(incoming_list):
	global lemmatizer
	for i,word in enumerate(incoming_list):

		#lemmatizes and lowers tokens
		incoming_list[i] = lemmatizer.lemmatize(word.lower())

	return incoming_list 


class Aspect_analyzer():
	def __init__(self):
		#sets the language being used for training, changes training data, preprocessing, tokenizing
		#cz or en
		self.language = "cz"

		self.FILE_PREFIX = "/mnt/minerva1/nlp/projects/sentiment8/analyzer/"

		#vocabulary size of each model
		self.VOCABULARY_SIZE = 500 
		self.DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
		self.BATCH_SIZE = 4

		#number of epochs
		self.N_EPOCHS = 200

		#pytorch fields, the hold vocabularies, data, etc.
		self.text = None
		self.aspect = None
		self.polarity = None

		self.train_data = self.valid_data = self.test_data = None
		self.model = None
		self.optimizer = None
		self.criterion = None
		self.train_iterator = self.valid_iterator = self.test_iterator = None
		
		#list of aspects
		# each aspect has an aspect model (predicts if the aspect is present in a sentence)
		# and polarity model (predicts polarity of given aspect)
		#trained_aspects = ["actor", "audio_video", "character", "experience", "story"]
		#trained_aspects = ["story"]
		trained_aspects = ["actor"]
		#there are two models for each aspect,
		#models for determining aspect occurance (False) and its polarity (True)
		polarity_flags = [True, False] 

		#iterating over all combinations
		for trained_aspect in trained_aspects:
			for polarity_flag in polarity_flags:

				print("**************************************************")
				self.curr_aspect = trained_aspect
				self.curr_polarity = polarity_flag

				if(self.language == "cz"):
					if(self.curr_polarity):
						self.VOCABULARY_SIZE = 1000
					else:
						self.VOCABULARY_SIZE = 1900
				else:
					if(self.curr_polarity):
						self.VOCABULARY_SIZE = 500
					else:
						self.VOCABULARY_SIZE = 1500
				 

				
				if(self.curr_polarity):
					self.model_postfix = "_pos_neg"
				else:
					self.model_postfix = "_aspect"

				self.setup_analyzer()
				self.train_analyzer()
		
	#loads data for current trained model
	def load_data(self):
		fields = {"aspect":('aspect', self.aspect), "text":('text', self.text), "polarity":('polarity', self.polarity)}
		train_data = data.TabularDataset.splits(
			path = '',
			train = self.FILE_PREFIX+"data/"+self.language+"/" + self.curr_aspect+self.model_postfix + ".txt",#path to file with train data
			format = 'json',
			fields = fields
			)[0]#TODO 0, because I use only train,

		train_data, valid_data = data.TabularDataset.splits(
			path = '',
			train = self.FILE_PREFIX+"data/"+self.language+"/aa" + self.curr_aspect+self.model_postfix + "_train.txt",#path to file with train data
			validation = self.FILE_PREFIX+"data/"+self.language+"/aa" + self.curr_aspect+self.model_postfix + "_test.txt",
			format = 'json',
			fields = fields
			)

		return train_data,valid_data

		return train_data

	#sets up configurations of current model
	def setup_analyzer(self):
		if(self.language == "cz"):
			tokenizer = nltk_tokenizer
			preprocessor = aspect_text_preprocess_cz
		else:
			tokenizer = "spacy"
			preprocessor = aspect_text_preprocess

		#pytorch fields, the hold vocabularies, data, etc.
		self.text = data.Field(include_lengths = True,preprocessing=preprocessor,tokenize=tokenizer)
		self.aspect = data.LabelField(dtype = torch.float,preprocessing=aspect_preprocess) 
		self.polarity = data.LabelField(dtype = torch.float,preprocessing=polarity_preprocess)

		
		#self.train_data = self.load_data()
		self.train_data,self.valid_data = self.load_data()

		self.text.build_vocab(self.train_data, max_size = self.VOCABULARY_SIZE)
		self.aspect.build_vocab(self.train_data)
		self.polarity.build_vocab(self.train_data)

		print(len(self.text.vocab))
		

		self.train_iterator = data.BucketIterator(
            (self.train_data), 
            batch_size = self.BATCH_SIZE,
            sort_key = lambda x: len(x.text),
            sort = True,
            sort_within_batch = True,#TODO True?
            device = self.DEVICE)

		self.train_iterator,self.valid_iterator = data.BucketIterator.splits(
            (self.train_data,self.valid_data), 
            batch_size = self.BATCH_SIZE,
            sort_key = lambda x: len(x.text),
            sort = True,
            sort_within_batch = True,#TODO True?
            device = self.DEVICE)

		#model parameters
		INPUT_DIM = len(self.text.vocab)
		EMBEDDING_DIM = 50 
		HIDDEN_DIM = 64
		OUTPUT_DIM = 1
		N_LAYERS = 2
		BIDIRECTIONAL = True
		DROPOUT = 0.5

		PAD_IDX = self.text.vocab.stoi[self.text.pad_token]
		UNK_IDX = self.text.vocab.stoi[self.text.unk_token]
		self.model = rnn_model.RNN(INPUT_DIM, 
			EMBEDDING_DIM, 
			HIDDEN_DIM, 
			OUTPUT_DIM, 
			N_LAYERS, 
			BIDIRECTIONAL, 
			DROPOUT, 
			PAD_IDX
		)
		self.model.embedding.weight.data[UNK_IDX] = torch.zeros(EMBEDDING_DIM)
		self.model.embedding.weight.data[PAD_IDX] = torch.zeros(EMBEDDING_DIM)

		self.optimizer = optim.Adam([p for p in self.model.parameters() if p.requires_grad], lr=0.001)
		self.criterion = nn.BCEWithLogitsLoss()

		self.model = self.model.to(self.DEVICE)
		self.criterion = self.criterion.to(self.DEVICE)
	
	#compares prediction and correct tag, takes a whole batch as inputs, return accuracy of the batch
	def binary_accuracy(self,preds,y):
		rounded_preds = torch.round(torch.sigmoid(preds))
		correct = (rounded_preds == y).float()
		acc = correct.sum() / len(correct)
		return acc   
       

	def train(self):
		epoch_loss = 0
		epoch_acc = 0
		self.model.train()
	    
		for batch in self.train_iterator:
			self.optimizer.zero_grad()

			text, text_lengths = batch.text

			predictions = self.model(text, text_lengths).squeeze(1)
			if(self.curr_polarity):
				batch_label = batch.polarity
			else:
				batch_label = batch.aspect

			loss = self.criterion(predictions, batch_label)
			acc = self.binary_accuracy(predictions, batch_label)
			loss.backward()
			self.optimizer.step()
			epoch_loss += loss.item()
			epoch_acc += acc.item()

		return epoch_loss / len(self.train_iterator), epoch_acc / len(self.train_iterator)	

	def evaluate(self,eval_type):
		#two types of evaluation, valid is during training and test is at the end of training, each uses diferent data
		if(eval_type == "valid"):
			iterator = self.valid_iterator
		else:
			iterator = self.test_iterator
		
		epoch_loss = 0
		epoch_acc = 0
		self.model.eval()
	    
		with torch.no_grad():
			for batch in iterator:
				text, text_lengths = batch.text

				if(self.curr_polarity):
					batch_label = batch.polarity
				else:
					batch_label = batch.aspect

				predictions = self.model(text, text_lengths).squeeze(1)
				loss = self.criterion(predictions, batch_label)
				acc = self.binary_accuracy(predictions, batch_label)

				epoch_loss += loss.item()
				epoch_acc += acc.item()
		return epoch_loss / len(iterator), epoch_acc / len(iterator)

	def train_analyzer(self):
		best_valid_loss = float('inf')

		for epoch in range(self.N_EPOCHS):
			start_time = time.time()

			train_loss, train_acc = self.train()
			valid_loss, valid_acc = self.evaluate("valid")

			

			end_time = time.time()

			epoch_mins, epoch_secs = epoch_time(start_time, end_time)

			#saves the model with smallest loss and its fields
			
			if valid_loss < best_valid_loss:
				best_valid_loss = valid_loss
				print(self.curr_aspect, self.curr_polarity)
				print(valid_loss,valid_acc)
				'''
				torch.save(self.model, self.FILE_PREFIX+'bin/'+self.language+'/aspect_analyzer/'+self.curr_aspect+self.model_postfix+'.pt')
				torch.save(self.text,self.FILE_PREFIX+"bin/"+self.language+"/aspect_analyzer/" + self.curr_aspect + self.model_postfix + "_textfield")
				if(self.curr_polarity):
					torch.save(self.polarity,self.FILE_PREFIX+"bin/"+self.language+"/aspect_analyzer/" + self.curr_aspect + self.model_postfix + "_polarityfield")
				else:
					torch.save(self.aspect,self.FILE_PREFIX+"bin/"+self.language+"/aspect_analyzer/" + self.curr_aspect + self.model_postfix + "_aspectfield")
				'''				
analyze = Aspect_analyzer()
