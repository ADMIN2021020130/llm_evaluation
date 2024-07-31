import os
# coding=utf-8
import pandas as pd
import codecs
import csv
import argparse
from transformers import AutoTokenizer, AutoModel
import json
from tqdm import tqdm
import os
import difflib
import torch
import ray

def load_model(model_path, model_type="THUDM/chatglm-6b"):
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model = AutoModel.from_pretrained(model_path, trust_remote_code=True).half().cuda()
    model.cuda()
    model = model.eval()
    return tokenizer, model

def get_data_format(id="", prompt="", input="", response="", from_type="", answer="", domain="", choose="", predict=""):
    domain = [d for d in domain.split(" ")]
    data_format = {
        "id": id,
        "data":[{
            "prompt": prompt,
            "input": input,
            "response": [[response, from_type]],
            "answer":answer
    }],
    "domain": domain,
    "choose": choose,
    "predict": predict
    }
    if data_format["id"] == "":
        data_format["id"] = shortuuid.uuid(name=str(data_format["data"]))
    return data_format

def disable_torch_init():
    """
    Disable the redundant torch default initialization to accelerate model creation.
    """
    import torch
    setattr(torch.nn.Linear, "reset_parameters", lambda self: None)
    setattr(torch.nn.LayerNorm, "reset_parameters", lambda self: None)

@ray.remote(num_gpus=1)
@torch.inference_mode()
def get_model_answers_largescale(model_path, qas_jsons, max_length=1024):
    disable_torch_init()
    model_path = os.path.expanduser(model_path)
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model = AutoModel.from_pretrained(model_path, trust_remote_code=True).half().cuda()
    model = model.eval()

    response_jsons = []
    for i, line in enumerate(tqdm(qas_jsons)):
        prompt = line["data"][0]["prompt"]
        response, _ = model.chat(tokenizer, prompt, max_length=max_length)
        line["data"][0]["response"][0][0] = response 
        response_jsons.append(line)
    return response_jsons


def infer_multiplegpu(model_path, qas_jsons, num_gpus, max_length, response_file):
    chunk_size = len(qas_jsons) // num_gpus
    response_handles = []
    for i in range(0, len(qas_jsons), chunk_size):
        response_handles.append(get_model_answers_largescale.remote(model_path, qas_jsons[i:i + chunk_size], max_length))
    response_jsons = []
    for response_handle in response_handles:
        response_jsons.extend(ray.get(response_handle))
    #print("len1:", len(qas_jsons))
    #print("len2:", len(response_jsons))
    assert len(qas_jsons) == len(response_jsons)
    with open(os.path.expanduser(response_file), "w") as response_file:
        for line in response_jsons:
            response_file.write(json.dumps(line, ensure_ascii=False) + "\n")

def load_human_res(jsonfile):
    lines = open(jsonfile).readlines()
    res = []
    for l in lines:
        data = json.loads(l.strip())
        res.append(data)
    return res


if __name__ == '__main__':
    ray.init()
    model_path = "/mnt/pfs/jinfeng_team/SFT/caiguodu/workspace/projects/largescale_for_glm_series/exp/chatglm-sft-combine-v3.2/global_step9675-hf"
    #model_path = "/mnt/pfs/jinfeng_team/SFT/dengshuhao1/workspace/largescale/exp/chatglm-sft-combine-v3.2-v1.0/global_step488-hf"
    #model_path = "/mnt/pfs/jinfeng_team/SFT/dengshuhao1/workspace/largescale/exp/chatglm-sft-combine-v3.2-v1.1/global_step2700-hf"
    qas_jsons = load_human_res("human_res.json")
    num_gpus = 8
    max_length = 2048
    response_file = "infer_res_v3.2.json"
    infer_multiplegpu(model_path, qas_jsons, num_gpus, max_length,  response_file)


