# -*- coding: utf-8 -*-
import argparse
from transformers import AutoTokenizer, AutoModel
import torch
import os
import sys
import json
from tqdm import tqdm
import ray
import shortuuid


def disable_torch_init():
    """
    Disable the redundant torch default initialization to accelerate model creation.
    """
    import torch
    setattr(torch.nn.Linear, "reset_parameters", lambda self: None)
    setattr(torch.nn.LayerNorm, "reset_parameters", lambda self: None)

def run_eval(args): #(model_path, model_id, question_file, answer_file, max_length, num_gpus):

    # params
   
    model_A = args.A_model
    model_B = args.B_model

    model_A_path = args.model_A_path
    model_B_path = args.model_B_path


    question_file = args.question_file
    answer_file = args.answer_file
    max_length = args.max_length
    num_beams = args.num_beams
    do_sample = args.do_sample
    top_p = args.top_p
    temperature = args.temperature
    num_gpus = args.num_gpus

    # split question file into num_gpus files
    ques_jsons = []
    with open(os.path.expanduser(question_file), "r") as ques_file:
        for line in ques_file:
            ques_jsons.append(line)
    print(len(ques_jsons))

    chunk_size = len(ques_jsons) // num_gpus
    ans_handles = []
    for i in range(0, len(ques_jsons), chunk_size):
        ans_handles.append(get_model_answers_largescale.remote(model_A_path, model_B_path,ques_jsons[i:i + chunk_size], max_length, num_beams, do_sample, top_p, temperature))

    ans_jsons = []
    for ans_handle in ans_handles:
        ans_jsons.extend(ray.get(ans_handle))
    assert len(ques_jsons) == len(ans_jsons)

    with open(os.path.expanduser(answer_file), "w") as ans_file:
        for line in ans_jsons:
            ans_file.write(json.dumps(line, ensure_ascii=False) + "\n")


@ray.remote(num_gpus=1)
@torch.inference_mode()
def get_model_answers_largescale(model_A_path,model_B_path, question_jsons, max_length=1024, num_beams=1, do_sample=True, top_p=0.7, temperature=0.95):

    disable_torch_init()
    model_A_path = os.path.expanduser(model_A_path)
    model_B_path = os.path.expanduser(model_B_path)
    tokenizer_A = AutoTokenizer.from_pretrained(model_A_path, trust_remote_code=True)
    tokenizer_B = AutoTokenizer.from_pretrained(model_B_path, trust_remote_code=True)
    model_A = AutoModel.from_pretrained(model_A_path, trust_remote_code=True).half().cuda()
    model_B = AutoModel.from_pretrained(model_B_path, trust_remote_code=True).half().cuda()
    model_A = model_A.eval()
    model_B = model_B.eval()

    ans_jsons = []
    for i, line in enumerate(tqdm(question_jsons)):
        data = json.loads(line.strip())
        prompt = data["prompt"] 
        history = []
        l = data['data']
        if len(l) == 0:
            history = []
        else:
            for ll in l:
                history.append([ll['prompt'],ll['response']])
        response_A, _ = model_A.chat(tokenizer_A, prompt, history=history,max_length=max_length, num_beams=num_beams, do_sample=do_sample, top_p=top_p, temperature=temperature)
        response_B, _ = model_B.chat(tokenizer_B, prompt,history=history, max_length=max_length, num_beams=num_beams, do_sample=do_sample, top_p=top_p, temperature=temperature)
        data["model_A"] = response_A
        data["model_B"] = response_B
        ans_jsons.append(data)

    return ans_jsons


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--A-model", type=str, required=True)
    parser.add_argument("--B-model", type=str, required=True)
    parser.add_argument("--model-A-path", type=str, required=True)
    parser.add_argument("--model-B-path", type=str, required=True)
    parser.add_argument("--question-file", type=str, required=True)
    parser.add_argument("--answer-file", type=str, default="answer.jsonl")
    parser.add_argument("--num-gpus", type=int, default=8)
    parser.add_argument("--max-length", type=int, default=1024)
    parser.add_argument("--num-beams", type=int, default=1)
    parser.add_argument("--do-sample", type=bool, default=True)
    parser.add_argument("--top-p", type=float, default=0.7)
    parser.add_argument("--temperature", type=float, default=0)

    args = parser.parse_args()

    ray.init()
    # run_eval(args.model_path, args.model_id, args.question_file, args.answer_file, args.max_length, args.num_gpus)
    run_eval(args)
