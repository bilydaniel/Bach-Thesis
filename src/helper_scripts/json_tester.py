#tests json data, copies only the correct ones 
#(some contained characters that caused errors in loading the data)
# xbilyd01

import json
input_file = "train.txt"
output_file = "train_.txt"


with open(input_file,"r") as f_in:
	with open(output_file,"a") as f_out:
		for x,line in enumerate(f_in):
			#f_out.write(line.encode('ascii', 'ignore').decode("utf-8"))
			try:
				json.loads(line)
				f_out.write(line)
			except Exception as e:
				print(line)
				print(x)
			
