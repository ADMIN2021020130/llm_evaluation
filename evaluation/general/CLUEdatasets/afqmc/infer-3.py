from transformers import AutoTokenizer, AutoModel
import json
import torch
torch.cuda.set_device(1)
model_path = "THUDM/chatglm-6b"
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
model = AutoModel.from_pretrained(model_path, trust_remote_code=True).half().cuda()
model = model.eval()

def load_abx_json_file(json_file):
    data = json.load(open(json_file))
    return data

def process_response_getlabel(response):
        if response.find("不相近") != -1:
                return 0
        if response.find("不相近") == -1 and response.find("相近") != -1:
                return 1
        return -1

#fr = open("/mnt/pfs/dengshuhao1/data/DataForSFT/Multiple_rounds_dialogue_data/testsets/afqmc/dev.json")
fr = open("/mnt/pfs/dengshuhao1/data/DataForSFT/Multiple_rounds_dialogue_data/testsets/CLUEdatasets/afqmc/dev.json")
count = 0
right = 0
for i in fr.readlines():
	content = eval(i)
	#print(content)
	sentence1 = content["sentence1"]
	sentence2 = content["sentence2"]
	label = content["label"]
	prompt = "下面两个句子的含义是否相近，不需要多余解释，只回答“相近”或“不相近”。\n\n" + sentence1 + "\n" + sentence2
	response, history = model.chat(tokenizer, prompt, history=[])
	print("#################################################", flush=True)
	print(prompt, flush=True)
	print("###################################", flush=True)
	print(response, flush=True)
	predict = process_response_getlabel(response)
	print("label:", label)
	print("predict:", predict) 
	count += 1
	if(predict == int(label)):
		right += 1
	print("right:", right)
	print("count:", count)
	print("acc:", right/count)

print("###################################", flush=True)
print("acc:", right/count)	

