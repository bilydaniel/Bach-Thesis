#saves annotated data as json
# xbilyd01

import json
from contextlib import ExitStack
def json_readr(file):
	for line in open(file, mode="r"):
		yield json.loads(line)


generator = json_readr("annotated_json.txt")

filenames = ["actor_pos_neg","story_pos_neg","character_pos_neg","audio_video_pos_neg", "experience_pos_neg"]
with ExitStack() as stack:
	files = [
		stack.enter_context(open(filename,"a"))
		for filename in filenames
	]
    

	for line in open("annotated_json.txt", mode="r"):
			json_data = json.loads(line)
			
			if(json_data["aspect"] == "actor"):
				json.dump(json_data,files[0],ensure_ascii=False)
				files[0].write('\n')
			if(json_data["aspect"] == "story"):
				json.dump(json_data,files[1],ensure_ascii=False)
				files[1].write('\n')
			if(json_data["aspect"] == "character"):
				json.dump(json_data,files[2],ensure_ascii=False)
				files[2].write('\n')
			if(json_data["aspect"] == "audio_video"):
				json.dump(json_data,files[3],ensure_ascii=False)
				files[3].write('\n')
			if(json_data["aspect"] == "experience"):
				json.dump(json_data,files[4],ensure_ascii=False)
				files[4].write('\n')

			

