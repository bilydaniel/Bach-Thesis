#splits data into train, test and validate
# xbilyd01

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


line_counts = {}
file_names = ["one_star.txt","two_star.txt"
,"three_star.txt","four_star.txt","five_star.txt"]

file_names = ["json_csfd.txt"]

for file_name in file_names:
	line_counts[file_name] = file_len(file_name)

print(line_counts)
lines_used = min(line_counts.values())


prefix = "csfd_"
train = prefix + "train.txt"
test = prefix + "test.txt"
validate = prefix + "validate.txt"



with open("wtf.txt","w") as wtf,open(train,"w") as trainf,open(test,"w") as testf,open(validate,"w") as validatef:
	for file_name in file_names:
		with open(file_name) as f:

			for i, l in enumerate(f):
				if(i < 10):
					wtf.write(l)#.replace('\n', '')
				if(i<(0.6*lines_used)):
					trainf.write(l)
				elif(i<(0.75*lines_used)):
					validatef.write(l)
				elif(i<=lines_used):
					testf.write(l)

            
    
