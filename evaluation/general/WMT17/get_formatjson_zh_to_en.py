import json
import sys
import os
import random
import shortuuid

def get_data_format(id="", prompt="", input="", response="", from_type="", domain=""):
    if type(domain) != list:
        domain = [domain]
    data_format = {
        "id": id,
        "data":[{
            "prompt": str(prompt),
            "input": str(input),
            "response": [[str(response), str(from_type)]],
        }],
        "domain": domain,
    }
    if data_format["id"] == "":
        data_format["id"] = shortuuid.uuid(name=str(data_format["data"]))
    return data_format


def load_abx_json_file(json_file):
    data = json.load(open(json_file))
    return data

PROMPT_PREFIX= [
    "翻译为英文：\n",
    "把这个句子翻译为英文：\n",
    "这句话的英文怎么说？\n",
    "帮我翻译为英文：\n",
    "帮我把这句话翻译为英文：\n",
]

PROMPT_POSTFIX = [
    "\n翻译为英文。",
    "\n把这个句子翻译为英文。",
    "\n这句话的英文怎么说？",
    "\n帮我翻译为英文。",
    "\n帮我把这句话翻译为英文。",
]

def generate_prompt_and_response(en, zh):
    choices = ["PROMPT_PREFIX", "PROMPT_POSTFIX"]
    choice = random.choice(choices)
    if(choice=="PROMPT_PREFIX"):
        prompt = random.choice(PROMPT_PREFIX) + zh
        response = en
        data_format = get_data_format(prompt=prompt, response=response, from_type="wmt17", domain=["General", "wmt17", "zh-to-en"])
    else:
        prompt = zh + random.choice(PROMPT_POSTFIX)
        response = en        
        data_format = get_data_format(prompt=prompt, response=response, from_type="wmt17", domain=["General", "wmt17", "zh-to-en"])

    return data_format

if __name__ == "__main__":
    fr = open(sys.argv[1], "r")
    fw = open(sys.argv[2], "w")
    res = []
    for content in fr.readlines():
        data = eval(content)
        en = data["translation"]["en"]
        zh = data["translation"]["zh"]
        data_format = generate_prompt_and_response(en, zh)
        res.append(data_format)
    for ct in res:
        fw.write(json.dumps(ct, ensure_ascii=False)+"\n")


