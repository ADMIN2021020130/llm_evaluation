import json
import sys
import os

def load_res_largescale(jsonfile):
    res = list()
    lines = open(jsonfile).readlines()
    for l in lines:
        data = json.loads(l.strip())
        res.append(data)
    return res 

if __name__ == '__main__':
    data = load_res_largescale("ceval_all_no_shot_v3_middle_school_mathematics_RD8.jsonl")
    res = []
    for item in data:
        lists = [item["data"][-5], item["data"][-4], item["data"][-3], item["data"][-2], item["data"][-1]]
        item["data"] = lists
        res.append(item)
    fw = open("ceval_all_no_shot_v3_middle_school_mathematics_RD5.jsonl", "w")
    for line in data:
        fw.write(json.dumps(line, ensure_ascii=False) + "\n")
