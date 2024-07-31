import os
import json
import torch
import argparse
import pandas as pd
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModel

def load_model(model_path, model_type="THUDM/chatglm-6b"):
    tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True)
    model = AutoModel.from_pretrained(model_path, trust_remote_code=True).half().cuda()
    model.cuda()
    model = model.eval()
    return tokenizer, model

def process_response_getlabel(response):
        if response.find("不相近") != -1:
                return 0
        if response.find("不相近") == -1 and response.find("相近") != -1:
                return 1
        return -1

def get_prompt(bustm_sample):
    sentence1 = bustm_sample['sentence1']
    sentence2 = bustm_sample['sentence2']
    prompt = "下面两个句子的含义是否相近，不需要多余解释，只回答“相近”或“不相近”。\n\n" + sentence1 + "\n" + sentence2
    if bustm_sample['label'] == "1":
        label = "相近"
    else:
        label = "不相近"
    return prompt, label

if __name__ == "__main__":
    model_path = "THUDM/chatglm-6b"
    bustm_data_path = "./test_public.json"
    bustm_lst = []
    with open(bustm_data_path, 'r') as file:
        for line in file:
            json_data = json.loads(line)
            bustm_lst.append(json_data)

    tokenizer, model= load_model(model_path)
    count = 0
    right = 0
    fw = open("./logs/" + "bustm_log.txt", "w", encoding='utf-8')
    for i in range(len(bustm_lst)):
        bustm_samples = bustm_lst[i]
        prompt,label =get_prompt(bustm_samples)
        response, history = model.chat(tokenizer, prompt, history=[])
        print("#################################################", flush=True)
        fw.write("#########################################\n")
        print(prompt, flush=True)
        fw.write(str(prompt))
        fw.write("\n")
        fw.write("######################\n")
        print("###################################", flush=True)
        print(response, flush=True)
        fw.write(str(response))
        fw.write("\n")
        predict = process_response_getlabel(response)
        print("label:", bustm_samples['label'])
        print("predict:", predict) 

        count += 1
        if(predict == int(bustm_samples['label'])):
            right += 1

        print("right:", right)
        print("count:", count)
        acc = right/count
        print("acc:", right/count)
        fw.write("label:")
        fw.write(str(label))
        fw.write("\n")
        fw.write("predict:")
        fw.write(str(predict))
        fw.write("\n")
        fw.write("rigth:")
        fw.write(str(right))
        fw.write("\n")
        fw.write("count:")
        fw.write(str(count))
        fw.write("\n")
        fw.write("acc:")
        fw.write(str(acc))
        fw.write("\n")
        fw.flush()

    print("###################################", flush=True)
    print("acc:", right/count)
    fw.write("###################################\n")
    fw.write(str(acc))
    fw.write("\n")
    fw.flush()
    fw.close()
