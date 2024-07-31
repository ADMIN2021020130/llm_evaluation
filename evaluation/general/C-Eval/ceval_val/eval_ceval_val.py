# coding=utf-8
import pandas as pd
import codecs
import csv
from transformers import AutoTokenizer, AutoModel
import json
from tqdm import tqdm
import os
import difflib
import torch
torch.cuda.set_device(2)

def load_model(model_path, model_type="THUDM/chatglm-6b"):
	tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True)
	model = AutoModel.from_pretrained(model_path, trust_remote_code=True).half().cuda()
	model.cuda()
	model = model.eval()
	return tokenizer, model

def load_csv(csv_file):
	data = []
	with codecs.open(csv_file, encoding='utf-8-sig') as f:
		for row in csv.DictReader(f, skipinitialspace=True):
			data.append(row)
	return data

def five_shots(five_shots_data, name, use_tag):
	title = "以下是中国关于" + str(name) + "考试的单项选择题，请选出其中正确的答案"+"\n"
	prompt = title
	for i in five_shots_data[:5]:
		question = i["question"] + "\n"
		choice = "A.%s  B.%s  C.%s  D.%s "% (i["A"], i["B"], i["C"], i["C"]) +"\n"
		if use_tag == "AO":
			answer = "答案：%s"%i["answer"]
		if use_tag == "COT":
			explanation = i["explanation"]
			answer = "答案：让我们一步一步思考，\n" + explanation + "\n所以答案是：%s"%i["answer"]
		prompt = prompt + question + choice + answer+"\n"
	return prompt

def get_prompt(sample, cache_prompt, use_tag):
	question = sample["question"] + "\n"
	choice = "A.%s  B.%s  C.%s  D.%s "% (sample["A"], sample["B"], sample["C"], sample["C"]) +"\n"
	label = sample["answer"]
	if use_tag == "AO":
		answer = ""
	if use_tag == "COT":
		answer = ""
	prompt = cache_prompt + question + choice + answer
	return prompt, label

def dicts_for_name():
	dicts = {}
	dicts["high_school_biology"] = "高中生物"
	dicts["high_school_chemistry"] = "高中化学"
	dicts["high_school_chinese"] = "高中语文"
	dicts["high_school_geography"] = "高中地理"
	dicts["high_school_history"] = "高中历史"
	dicts["high_school_mathematics"] = "高中数学"
	dicts["high_school_physics"] = "高中物理"
	dicts["high_school_politics"] = "高中政治"
	dicts["middle_school_biology"] = "初中生物"
	dicts["middle_school_chemistry"] = "初中化学"
	dicts["middle_school_geography"] = "初中地理"
	dicts["middle_school_history"] = "初中历史"
	dicts["middle_school_mathematics"] = "初中数学"
	dicts["middle_school_physics"] = "初中物理"
	dicts["middle_school_politics"] = "初中政治"
	dicts["modern_chinese_history"] = "近代中国史"
	dicts["logic"] = "逻辑"
	dicts["ideological_and_moral_cultivation"] = "思想道德修养"
	return dicts

def dicts_for_singlename():
	dicts = {}
	dicts["high_school_biology"] = "高中生物"
	#dicts["modern_chinese_history"] = "近代中国史"
	return dicts

def get_model_response(tokenizer, model, prompt):
	response, history = model.chat(tokenizer, prompt, history=[])
	return response

def string_similar(s1, s2):
	return difflib.SequenceMatcher(None, s1, s2).quick_ratio()

def process_response_getlabel(response, sample):
	ans = response[response.find("答"):]
	if "A" in ans:
		return "A"
	if "B" in ans:
		return "B"
	if "C" in ans:
		return "C"
	if "D" in ans:
		return "D"
	ans = response[response.find("选"):]
	if "A" in ans:
		 return "A"
	if "B" in ans:
		return "B"
	if "C" in ans:
		 return "C"
	if "D" in ans:
		return "D"
	ans = response[response.find("正确")-10:]
	if "A" in ans:
		return "A"
	if "B" in ans:
		return "B"
	if "C" in ans:
		return "C"
	if "D" in ans:
		return "D"
	ration = 0
	reslut_key = ""
	lists = ["A", "B", "C", "D"]
	for key in lists:
		similar = string_similar(response, sample[key])
		if similar > ration:
			reslut_key = key
			ration = similar
		if reslut_key != "":
			return reslut_key
	return -1

def ceval_val(model_path, five_shots_data_file, eval_data_file, use_tag, repeat_num, name, fw):
	five_shots_data = load_csv(five_shots_data_file)
	eval_datas = []
	eval_data = load_csv(eval_data_file)
	for i in range(repeat_num):
		eval_datas = eval_datas + eval_data
	cache_prompt = five_shots(five_shots_data, name,  use_tag)
	tokenizer, model = load_model(model_path, model_type="THUDM/chatglm-6b")
	count = 0
	rigth = 0
	for i in eval_datas:
		prompt, label = get_prompt(i, cache_prompt, use_tag)
		response = get_model_response(tokenizer, model, prompt)
		print("#########################################", flush=True)
		fw.write("#########################################\n")
		print(prompt, flush=True)
		fw.write(str(prompt))
		fw.write("\n")
		print("######################", flush=True)
		fw.write("######################\n")
		print(response, flush=True)
		fw.write(str(response))
		fw.write("\n")
		predict = process_response_getlabel(response, i)
		if(predict==label):
			rigth+=1
		count += 1
		acc = rigth/count
		print("##############", flush=True)
		fw.write("##############\n")
		print("predict:", predict, flush=True)
		fw.write("predict:")
		fw.write(str(predict))
		fw.write("\n")
		print("label:", label, flush=True)
		fw.write("label:")
		fw.write(str(label))
		fw.write("\n")
		print("rigth:", rigth, flush=True)
		fw.write("rigth:")
		fw.write(str(rigth))
		fw.write("\n")
		print("count:", count, flush=True)
		fw.write("count:")
		fw.write(str(count))
		fw.write("\n")
		print("acc:", acc, flush=True)
		fw.write("acc:")
		fw.write(str(acc))
		fw.write("\n")
		fw.flush()
	return acc

#use_tag = sys.argv[1]
#use_tag = "COT"	
#model_path = "THUDM/chatglm-6b"	
#five_shots_data_file = "../ceval_dev/middle_school_mathematics_dev.csv"
#eval_data_file = "./middle_school_mathematics_val.csv"
#acc = ceval_val(model_path, five_shots_data_file, eval_data_file,  use_tag)
#print("#########################################", flush=True)
#print("acc:", acc, flush=True)
if __name__ == "__main__":
	dicts_for_name = dicts_for_name()
	ave_acc = 0
	count =0
	for i in dicts_for_name.keys():
		print("#########################################################################################################", flush=True)
		use_tag = "AO"
		repeat_num = 9
		model_path = "THUDM/chatglm-6b"
		five_shots_data_file = "../ceval_dev/" + str(i) + "_dev.csv"
		eval_data_file = "./" + str(i) + "_val.csv"
		fw = open("./logs4/" + str(i) + "_" + use_tag + "_log.txt", "w", encoding='utf-8')
		acc = ceval_val(model_path, five_shots_data_file, eval_data_file, use_tag, repeat_num, dicts_for_name[i], fw)
		ave_acc += acc
		count += 1
		print("#########################################", flush=True)
		print("acc:", acc, flush=True)
		fw.write("#########################################\n")
		fw.write("acc:")
		fw.write(str(acc))
		fw.write("\n")
		fw.flush()
		fw.close()
	print("acv_acc:", ave_acc/count, flush=True)

