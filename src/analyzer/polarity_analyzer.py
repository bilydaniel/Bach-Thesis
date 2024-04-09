#Trains polarity classifier, neural network
# xbilyd01

from models import rnn_model
import torch
from torchtext import data
import time
import torch.optim as optim
import torch.nn as nn
import spacy
import nltk
import unidecode
num_pos = 0
num_neg = 0
#returns list of tokens (words), made from czech text
def nltk_tokenizer(text):
	return nltk.word_tokenize(text,language="czech")

#measures time, mainly used for measuring training
def epoch_time(start_time, end_time):
	elapsed_time = end_time - start_time
	elapsed_mins = int(elapsed_time / 60)
	elapsed_secs = int(elapsed_time - (elapsed_mins * 60))
	return elapsed_mins, elapsed_secs

#text preprocessor, takes tokens (words) as input
def text_preprocess(incoming_list):
	for i,word in enumerate(incoming_list):
		incoming_list[i] = word.lower()
	 
	return incoming_list    

#czech text preprocessor, takes tokens (words) as input
def text_preprocess_cz(incoming_list):
	for i,word in enumerate(incoming_list):
		#lowers the token and removes diacritics
		incoming_list[i] = unidecode.unidecode(word.lower())
		

	return incoming_list

#splits ratings into positive and negative classes
def polarity_label_preprocess(incoming_list):
	#global num_pos 
	#global num_neg
	if(float(incoming_list) <= 0.5):
		#num_neg += 1
		return "neg"
	else:
		#num_pos += 1
		return "pos"


class Polarity_analyzer():
	def __init__(self):
		#sets the language being used for training, changes training data, preprocessing, tokenizing
		#cz or en
		self.language = "en"

		if(self.language == "cz"):
			tokenizer = nltk_tokenizer
			preprocessor = text_preprocess_cz
		else:
			tokenizer = "spacy"
			preprocessor = text_preprocess

		self.FILE_PREFIX = "/mnt/minerva1/nlp/projects/sentiment8/analyzer/"
		self.VOCABULARY_SIZE = 25000
		self.DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
		self.BATCH_SIZE = 64	
		self.N_EPOCHS = 15

		#pytorch fields, the hold vocabularies, data, etc.
		self.text = data.Field(include_lengths = True,preprocessing=preprocessor,tokenize=tokenizer)
		self.label = data.LabelField(dtype = torch.float,preprocessing=polarity_label_preprocess)

		self.train_data = self.valid_data = self.test_data = None
		self.model = None
		self.optimizer = None
		self.criterion = None
		self.train_iterator = self.valid_iterator = self.test_iterator = None

		self.setup_analyzer()
		
		self.train_analyzer()
		
	#loads data for training, validating and testing
	def load_data(self):
		fields = {"rating":('label', self.label), "text":('text', self.text)}
		train_data, valid_data, test_data = data.TabularDataset.splits(
                                        path = '',
                                        train = self.FILE_PREFIX + 'data/'+self.language+'/train.txt',
                                        validation = self.FILE_PREFIX + 'data/'+self.language+'/validate.txt',
                                        test = self.FILE_PREFIX + 'data/'+self.language+'/test.txt',
                                        format = 'json',
                                        fields = fields
    	)	
   

		return train_data, valid_data, test_data

	#sets up configurations of the model
	def setup_analyzer(self):
		self.train_data , self.valid_data, self.test_data = self.load_data()

		self.text.build_vocab(self.train_data, max_size = self.VOCABULARY_SIZE)
		self.label.build_vocab(self.train_data)
		
		self.train_iterator, self.valid_iterator, self.test_iterator = data.BucketIterator.splits(
            (self.train_data, self.valid_data, self.test_data), 
            batch_size = self.BATCH_SIZE,
            sort_key = lambda x: len(x.text),
            sort_within_batch = True,
            device = self.DEVICE)

		INPUT_DIM = len(self.text.vocab)
		EMBEDDING_DIM = 100
		HIDDEN_DIM = 256
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
		#weights for unbalanced data
		
		if(self.language=="en"):
			pos_weight = torch.Tensor([646020.0/678625.0])
		else:
			pos_weight = torch.Tensor([209561.0/643098.0])
		
		self.model.embedding.weight.data[UNK_IDX] = torch.zeros(EMBEDDING_DIM)
		self.model.embedding.weight.data[PAD_IDX] = torch.zeros(EMBEDDING_DIM)

		self.optimizer = optim.Adam([p for p in self.model.parameters() if p.requires_grad], lr=0.001)
		self.criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)#

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
	    
		for i,batch in enumerate(self.train_iterator):
			#if(i > 1000):
			#	break
			self.optimizer.zero_grad()

			text, text_lengths = batch.text#batch.text

			predictions = self.model(text, text_lengths).squeeze(1)
			loss = self.criterion(predictions, batch.label)
			acc = self.binary_accuracy(predictions, batch.label)
			loss.backward()
			self.optimizer.step()
			epoch_loss += loss.item()
			epoch_acc += acc.item()

		return epoch_loss / i, epoch_acc / i		
		
	
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
			for i,batch in enumerate(iterator):
				#if(i>10000):
				#	break
				text, text_lengths = batch.text

				predictions = self.model(text, text_lengths).squeeze(1)
				loss = self.criterion(predictions, batch.label)
				acc = self.binary_accuracy(predictions, batch.label)

				epoch_loss += loss.item()
				epoch_acc += acc.item()

		return epoch_loss / i, epoch_acc / i
		


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
				torch.save(self.model, self.FILE_PREFIX+'bin/'+self.language+'/polarity_analyzer/polarity_model.pt')
				torch.save(self.text, self.FILE_PREFIX+'bin/'+self.language+'/polarity_analyzer/text_field.pt')
				torch.save(self.label, self.FILE_PREFIX+'bin/'+self.language+'/polarity_analyzer/label_field.pt')
				
				print("MODEL SAVED")


			print(f'Epoch: {epoch+1:02} | Epoch Time: {epoch_mins}m {epoch_secs}s')
			print(f'\tTrain Loss: {train_loss:.3f} | Train Acc: {train_acc*100:.2f}%')
			print(f'\t Val. Loss: {valid_loss:.3f} |  Val. Acc: {valid_acc*100:.2f}%')

		#loads the best trained model and performs test
		self.model = torch.load(self.FILE_PREFIX+'bin/'+self.language+'/polarity_analyzer/polarity_model.pt')
		self.model.eval()
		test_loss, test_acc = self.evaluate("test")
		print(f'Test Loss: {test_loss:.3f} | Test Acc: {test_acc*100:.2f}%')

analyze = Polarity_analyzer()
