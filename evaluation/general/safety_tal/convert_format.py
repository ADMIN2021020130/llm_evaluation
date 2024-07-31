import json
import sys
import os

def load_human_res(jsonfile):
    lines = open(jsonfile).readlines()
    res = []
    for l in lines:
        data = json.loads(l.strip())
        res.append(data)
    return res

if __name__ == "__main__":
    data = load_human_res("ff1.jsonl")
    res = []
    fw = open("ff.jsonl",'w')
    for item in data:
        item["taskid"] = item["id"]
        item["key"] = item["origin_id"]
        item["mathgpt"] = ""
        item["type"] = "通用-安全"
        item["score"] = ""
        item["data"] = []
        del item["id"]
        del item["origin_id"]
        res.append(item)
        fw.write(json.dumps(item, ensure_ascii=False)+"\n")
        print(item)
