from transformers import AutoTokenizer, AutoModel
import json
import difflib
import torch
torch.cuda.set_device(5)

model_path = "THUDM/chatglm-6b"
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
model = AutoModel.from_pretrained(model_path, trust_remote_code=True).half().cuda()
model = model.eval()

def string_similar(s1, s2):
	return difflib.SequenceMatcher(None, s1, s2).quick_ratio()

def load_abx_json_file(json_file):
	data = json.load(open(json_file))
	return data

def process_response_getlabel(response, labels_dict):
	for key in labels_dict.keys():
		if response.find(key) != -1:
			return labels_dict[key]	
	ration = 0
	reslut_key = ""
	for key in labels_dict.keys():
		similar = string_similar(response, labels_dict[key])
		if similar > ration:
			reslut_key = key
			ration = similar
	if reslut_key != "":
		return labels_dict[reslut_key]
	return -1

f_label = open("labels.json", "r")
labels = []
for i in f_label.readlines():
	labels.append(eval(i)["label_desc"])
#print(labels)
labels = ["故事", "文化", "娱乐", "运动", "财经", "房屋", "汽车", "教育", "科技", "军事", "旅游", "世界", "股票", "农业", "游戏"]
labels_dict = {"故事":"news_story", "文化":"news_culture", "娱乐":"news_entertainment", "运动":"news_sports", "财经":"news_finance", "房屋":"news_house", "汽车":"news_car", "教育":"news_edu", "科技":"news_tech", "军事":"news_military", "旅游":"news_travel", "世界":"news_world", "股票":"news_stock", "农业":"news_agriculture", "游戏":"news_game"}
fr = open("dev.json", "r")
count = 0
right = 0
for i in fr.readlines():
	content = eval(i)
	sentence = content["sentence"]
	keywords = content["keywords"]	
	label = content["label_desc"]
	Label = ""
	for i in labels:
                Label = Label + "“" + i + "”" +"、"	
	Label = Label[:-1]
	prompt = "单项选择题：根据下列句子和关键词判断它属于下列新闻的那个版块分类，以“该新闻属于***板块”作为开头进行回答。\n\n句子：" + sentence + "\n" + "关键词：" + keywords + "\n" + "新闻板块：" + Label 
	response, history = model.chat(tokenizer, prompt, history=[])
	print("#################################################", flush=True)
	print(prompt, flush=True)
	print("###################################", flush=True)
	print(response, flush=True)
	predict = process_response_getlabel(response, labels_dict)
	print("label:", label)
	print("predict:", predict) 
	count += 1
	if(predict == label):
		right += 1
	print("right:", right)	
	print("count:", count)

print("acc:", right/count) 
