import json
import sys
import os

def convert_largescale_to_130b(input_file, out_file):
    lines = open(input_file).readlines()
    with open(out_file, "w", encoding="utf-8") as fw:
        for l in lines:
            tmpd = dict()
            data = json.loads(l.strip())
            id = data['id']
            prompt = data['data'][0]['prompt']
            resp = data['data'][0]['response'][0][0]
            tmpd['id'] = id
            tmpd['prompt'] = prompt
            tmpd['response'] = resp
            tmpd['tag'] = "SFT_ape210k"
            fw.write(json.dumps(tmpd, ensure_ascii=False) + "\n")


if __name__ == '__main__':
    convert_largescale_to_130b("test_ape_largescale.json", "test_ape_130b.json")