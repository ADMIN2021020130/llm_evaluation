from transformers import AutoTokenizer, AutoModel
import json
import torch
torch.cuda.set_device(7)
model_path = "THUDM/chatglm-6b"
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
model = AutoModel.from_pretrained(model_path, trust_remote_code=True).half().cuda()
model = model.eval()

def load_abx_json_file(json_file):
    data = json.load(open(json_file))
    return data

def process_response_getlabel(response):
        if response.find("正确") != -1 and response.find("错误") == -1:
                return "true"
        if response.find("正确") == -1 and response.find("错误") != -1:
                return "false"
        return -1

#fr = open("/mnt/pfs/dengshuhao1/data/DataForSFT/Multiple_rounds_dialogue_data/testsets/afqmc/dev.json")
fr = open("dev.json", "r")
count = 0
right = 0
for i in fr.readlines():
	content = eval(i)
	print(content)
	text = content["text"]
	span1_text = content["target"]["span1_text"]
	span2_text = content["target"]["span2_text"]
	label = content["label"]
	prompt = "判断题：句子“" + text + "”中的，“" + span2_text + "”是指代“" + span1_text + "”，直接回答“正确”或者“错误”，不需要解释。"
	response, history = model.chat(tokenizer, prompt, history=[])
	print("#################################################", flush=True)
	print(prompt, flush=True)
	print("###################################", flush=True)
	print(response, flush=True)
	predict = process_response_getlabel(response)
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

