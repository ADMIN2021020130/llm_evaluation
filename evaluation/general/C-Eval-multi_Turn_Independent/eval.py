import os
import re
import json
import argparse

def get_label_by_resp_choices(infer_resp):
    ans = infer_resp[infer_resp.find("答"):]
    if "A" in ans:
        return "A" 
    if "B" in ans:
        return "B" 
    if "C" in ans:
        return "C" 
    if "D" in ans:
        return "D" 
    ans = infer_resp[infer_resp.find("选"):]
    if "A" in ans:
        return "A" 
    if "B" in ans:
        return "B" 
    if "C" in ans:
        return "C" 
    if "D" in ans:
        return "D" 
    ans = infer_resp[infer_resp.find("正确")-10:]
    if "A" in ans:
        return "A" 
    if "B" in ans:
        return "B" 
    if "C" in ans:
        return "C" 
    if "D" in ans:
        return "D" 
    return -1

def calculate_accuracy(text):
    pattern = r'\【(.*?)\】'  # 匹配以【和】括起来的任意内容
    fields = re.findall(pattern, text)

    if '分析' in fields and '详解' in fields and '点睛' in fields:
        return 1
    else:
        return 0

def eval_format(inf_file, inf_key):
    cnt = 0
    cnt_all = 0
    with open(inf_file, 'r') as f:
        for line in f.readlines():
            cnt_all += 1
            line = json.loads(line.strip())
            if inf_key in line.keys():
                inf_res = line[inf_key]
            else:
                raise ValueError("Unvalid inf key")
            cnt += calculate_accuracy(inf_res)
    acc_format = round((cnt/cnt_all), 4)
    print(f"格式解析准确率为：{acc_format}")

def load_res_largescale(jsonfile):
    res = list()
    lines = open(jsonfile).readlines()
    for l in lines:
        data = json.loads(l.strip())
        res.append(data)
    return res 

def eval_acc(inf_file, inf_key):
    data = load_res_largescale(inf_file)
    cnt = 0
    cnt_all = 0
    for item in data:
        prompt = item["prompt"]
        inf_res = item[inf_key]
        response = item["response"]
        cnt_all += 1
        if get_label_by_resp_choices(inf_res) == response:
            cnt += 1
    acc = round((cnt/cnt_all), 4)
    print(f"答案准确率为：{acc}")

def evals(inf_file, inf_key):
    eval_acc(inf_file, inf_key)
    eval_format(inf_file, inf_key)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--inf-file", type=str, required=True)
    parser.add_argument("--inf-key", type=str, default="6b", required=False)
    args = parser.parse_args()
    evals(args.inf_file, args.inf_key)
