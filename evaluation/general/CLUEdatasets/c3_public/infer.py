from transformers import AutoTokenizer, AutoModel
import json
import torch
torch.cuda.set_device(6)

model_path = "THUDM/chatglm-6b"
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
model = AutoModel.from_pretrained(model_path, trust_remote_code=True).half().cuda()
model = model.eval()

def load_abx_json_file(json_file):
	data = json.load(open(json_file))
	return data

def process_response_getlabel(response, choice_dict):
	for key in choice_dict.keys():
		if response.find(key) != -1:
			return choice_dict[key]	
	return -1


fr1 = open("d-dev.json", "r")
fr2 = open("m-dev.json", "r")
data1 = json.load(fr1)
data2 = json.load(fr2)
data = data1 + data2
count = 0
right = 0
for content in data:
	conversation = "对话：\n"
	for i in content[0]:
		conversation = conversation + i + "\n"
	conversation = conversation[:-1]
	question = "问题：\n" + content[1][0]["question"]	
	choice = "选项：\n"
	num = 1
	choice_dict = {}
	for i in content[1][0]["choice"]:
		choice = choice + "(" + str(num) + ")" + i + "\n"
		choice_dict[str(num)] = i
		num += 1 
	choice = choice[:-1]	
	label = content[1][0]["answer"]
	prompt = "单项选择题：根据下列对话从选项中选择答案回答问题，以“这道题的答案是”作为开头进行回答。" + "\n\n" + conversation + "\n" + question + "\n" + choice 
	response, history = model.chat(tokenizer, prompt, history=[])
	print("#################################################", flush=True)
	print(prompt, flush=True)
	print("###################################", flush=True)
	print(response, flush=True)
	predict = process_response_getlabel(response, choice_dict)
	print("label:", label)
	print("predict:", predict) 
	count += 1
	if(predict == label):
		right += 1
	print("right:", right)  
	print("count:", count)
	print("acc:", right/count)

print("#################################################", flush=True)
print("acc:", right/count) 


