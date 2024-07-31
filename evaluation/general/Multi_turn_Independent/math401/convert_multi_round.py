import json
import sys
import os

def data_formats(id="", prompt="", response="", domain=[], tag="", choice={}):
    
    data = {"id": id,
            "prompt": prompt,
            "response": response,
            "domain": domain,
            "tag": tag,
            "choice": choice,
    }
    return data


def load_res_largescale(jsonfile):
    res = list()
    lines = open(jsonfile).readlines()
    for l in lines:
        data = json.loads(l.strip())
        res.append(data)
    return res

def covert_json(item):
    id = item["id"]
    domain = item["domain"]
    data = item["data"]
    num = len(data)
    print("num:", num)
    tag = "Sft-C-Eval-middle_school_mathematics-" + str(num) + "-rounds"
    choice = {}
    prefix = "###Instruction:\n"
    postfix = "\n\n\n###Response:\n"
    prompt = ""
    for i in range(len(data)-1):
        temp = data[i]
        temp_prompt = temp["prompt"]
        temp_response = temp["response"][0]
        prompt = prompt + temp_prompt + postfix + temp_response + prefix

    prompt = prompt + data[-1]["prompt"] #+ postfix
    response = data[-1]["response"][0]
    return data_formats(id=id, prompt=prompt, response=response, domain=domain, tag=tag, choice=choice)

if __name__ == '__main__':
    json_data = load_res_largescale("math401_v3_round_4.jsonl")
    res_data = []
    fw = open("math401_v3_round_4_130b.jsonl", "w")
    for item in json_data:
        data_item = covert_json(item)
        fw.write(json.dumps(data_item, ensure_ascii=False) + "\n")
        print("********************"*5)
        print(data_item["prompt"])
        print("********************"*3)
        print(data_item["response"])
        print("\n\n\n\n")
    

