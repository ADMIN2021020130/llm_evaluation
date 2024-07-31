import json
import os
import sys

def convert_to_history(ori_jsonfile, out_jsonfile, prompt_prefix="计算：3+2\n结果：5\n计算：5*3\n结果：15\n计算："):
    lines = open(ori_jsonfile).readlines()
    with open(out_jsonfile, "w", encoding="utf-8") as fw:
        for l in lines:
            data = json.loads(l.strip())
            prompt = "{} {}".format(prompt_prefix, data["query"])
            response = data["response"]
            out_data = {"prompt": prompt, "response": response, "history":[]}
            fw.write(json.dumps(out_data, ensure_ascii=False) + "\n")
        

if __name__ == '__main__':
    convert_to_history("math401.json", "math401_history.json")
