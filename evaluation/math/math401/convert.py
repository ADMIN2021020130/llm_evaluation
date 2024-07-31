import json
import sys
import os

def convert_for_changlong(infile, outfile):
    lines = open(infile).readlines()
    with open(outfile, "w", encoding="utf-8") as fw:
        for l in lines:
            data = json.loads(l.strip())
            id = data['id']
            prompt = data['data'][0]['prompt']
            tag = "sft_math401"
            domain = data['domain']
            res = dict()
            res["id"] = id
            res["prompt"] = prompt
            res["tag"] = tag
            res["domain"] = domain
            fw.write(json.dumps(res,ensure_ascii=False)+ "\n")


if __name__ == '__main__':
    convert_for_changlong("math401_largescale.json", "math401_infer_130.jsonl")
