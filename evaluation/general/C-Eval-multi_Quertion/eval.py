import os
import re
import json
import argparse

def calculate_accuracy(text):
    pattern = r'\【(.*?)\】'  # 匹配以【和】括起来的任意内容
    fields = re.findall(pattern, text)

    if '分析' in fields and '详解' in fields and '点睛' in fields:
        return 1
    else:
        return 0

def load_res_largescale(jsonfile):
    res = list()
    lines = open(jsonfile).readlines()
    for l in lines:
        data = json.loads(l.strip())
        res.append(data)
    return res 

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

def evals(inf_file, inf_key):
    cnt_acc = 0
    cnt_format = 0
    cnt_all = 0
    data = load_res_largescale(inf_file)
    prefix1 = ["第一题", "第二题", "第三题", "第四题", "第五题"]
    prefix2 = ["[1]", "[2]", "[3]", "[4]", "[5]"]
    prefix3 = ["(1)", "(2)", "(3)", "(4)", "(5)"]
    for item in data:
        split = []
        que_num = len(item["single_id"])
        for i in range(que_num):
            split.append("")
        cnt_all += que_num
        prompt = item["prompt"]
        inf_res = item[inf_key]
        a = item[inf_key]
        response = item["response"]
        if item["prompt"][:3] == "第一题":
            flag = 1
            for i in range(que_num):
                if prefix1[i] not in inf_res:
                    flag = 0
                    break
            if flag == 0:
                continue
            for i in range(1, que_num):
                try:
                    split[i-1]=inf_res.split(prefix1[i])[0]
                    inf_res = inf_res.split(prefix1[i])[1]
                except:
                    #print("##################################")
                    #print(a)
                    #print("*********************")
                    #print(inf_res)
                    print("1:some parse error occur!!!")
                    break
            split[-1]=inf_res
            for i in range(len(split)):
                if get_label_by_resp_choices(split[i]) == response[i]:
                    cnt_acc+=1
                cnt_format += calculate_accuracy(split[i])
        elif item["prompt"][:3] == "[1]":
            flag = 1
            for i in range(que_num):
                if prefix2[i] not in inf_res:
                    flag = 0
                    break
            if flag == 0:
                continue
            for i in range(1, que_num):
                try:
                    split[i-1]=inf_res.split(prefix2[i])[0]
                    inf_res = inf_res.split(prefix2[i])[1]
                except:
                    #print(inf_res)
                    print("2:some parse error occur!!!")
                    break
            split[-1]=inf_res
            for i in range(len(split)):
                if get_label_by_resp_choices(split[i]) == response[i]:
                    cnt_acc+=1
                cnt_format += calculate_accuracy(split[i])
        elif item["prompt"][:3] == "(1)":
            flag = 1
            for i in range(que_num):
                if prefix3[i] not in inf_res:
                    flag = 0
                    break
            if flag == 0:
                continue
            for i in range(1, que_num):
                try:
                    split[i-1]=inf_res.split(prefix3[i])[0]
                    inf_res = inf_res.split(prefix3[i])[1]
                except:
                    #print(inf_res)
                    #print("##################################")
                    #print(a)
                    #print("*********************")
                    #print(inf_res)
                    print("3:some parse error occur!!!")
                    break
            split[-1]=inf_res
            for i in range(len(split)):
                if get_label_by_resp_choices(split[i]) == response[i]:
                    cnt_acc+=1
                cnt_format += calculate_accuracy(split[i])
        else:
            print("no formats")

    acc =  round((cnt_acc/cnt_all), 4)
    acc_format = round((cnt_format/cnt_all), 4)
    print(f"答案准确率为：{acc}")
    print(f"格式解析准确率为：{acc_format}")


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--inf-file", type=str, required=True)
    parser.add_argument("--inf-key", type=str, default="6b", required=False)
    args = parser.parse_args()
    evals(args.inf_file, args.inf_key)


