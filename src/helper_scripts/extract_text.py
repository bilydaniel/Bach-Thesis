#extracts text from json data, used for making data for future manual annotation
# xbilyd01

import json
def json_readr(file):
	if(reverse):
		for line in reversed(list(open(file,mode="r"))):
			yield json.loads(line)
	else:
		for line in open(file, mode="r"):
			yield json.loads(line)

reverse = 1
generator = json_readr("train_fixed.txt")


with open("annotation_data.txt","a") as f:
	i = 0
	while i < 10000:
		json_data = next(generator)
		f.write(json_data["text"])
		f.write("\n\n")
		i+=1
