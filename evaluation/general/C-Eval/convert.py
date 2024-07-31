import json
import sys
import os

def convert_for_changlong(infile, outfile):
    lines = open(infile).readlines()
    with open(outfile, "w", encoding="utf-8") as fw:
        for l in lines:
            try:
                data = json.loads(l.strip())
                id = data['id']
                prompt = data['data'][0]['prompt']
                response = data['data'][0]['response'][0][0]
                tag = "sft_ceval_valid"
                domain = data['data'][0]['domain']
                res = dict()
                res["id"] = id
                res["prompt"] = prompt
                res["tag"] = tag
                res["domain"] = domain
                res["response"] = response
                fw.write(json.dumps(res,ensure_ascii=False)+ "\n")
            except:
                print (l)


if __name__ == '__main__':
    convert_for_changlong("C-Eval_no_shot_validation.json", "C-Eval_no_shot_validation_infer_130.jsonl")
