# -*- coding: utf-8 -*-
import argparse


import os
import ray
import sys
import torch
import json
import shortuuid
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModel


def disable_torch_init():
    """
    Disable the redundant torch default initialization to accelerate model creation.
    """
    import torch
    setattr(torch.nn.Linear, "reset_parameters", lambda self: None)
    setattr(torch.nn.LayerNorm, "reset_parameters", lambda self: None)

def run_eval(args): #(model_path, model_id, question_file, answer_file, max_length, num_gpus):
    model_path = args.model_path
    # model_id = args.model_id
    question_file = args.question_file
    answer_file = args.answer_file
    num_gpus = args.num_gpus
    # max_length = args.max_length
    # num_beams = args.num_beams
    # do_sample = args.do_sample
    # top_p = args.top_p
    # temperature = args.temperature
    

    # split question file into num_gpus files
    ques_jsons = []
    with open(os.path.expanduser(question_file), "r") as ques_file:
        for line in ques_file:
            ques_jsons.append(line)
    print(len(ques_jsons))

    chunk_size = len(ques_jsons) // num_gpus
    ans_handles = []
    for i in range(0, len(ques_jsons), chunk_size):
        ans_handles.append(get_model_answers_largescale.remote(model_path, ques_jsons[i:i + chunk_size]))

    ans_jsons = []
    for ans_handle in ans_handles:
        ans_jsons.extend(ray.get(ans_handle))
    assert len(ques_jsons) == len(ans_jsons)

    with open(os.path.expanduser(answer_file), "w") as ans_file:
        for line in ans_jsons:
            ans_file.write(json.dumps(line, ensure_ascii=False) + "\n")



@ray.remote(num_gpus=1)
@torch.inference_mode()
def get_model_answers(model_path, question_jsons):
    disable_torch_init()
    model_path = os.path.expanduser(model_path)
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model = AutoModel.from_pretrained(model_path, trust_remote_code=True).half().cuda()
    model = model.eval()
    ans_jsons = []
    for i, line in enumerate(tqdm(question_jsons)):
      
        sample = json.loads(line)
        id = sample['id']

        history = []
        for i in range(len(sample['data'])):
            
            history_prompt = sample['data'][i]['prompt']
            response, history = model.chat(tokenizer, history_prompt, history=history, max_length=2048, num_beams=1,do_sample=False,top_p=0.7,temperature=0.01 )
         
        prompt = sample['data'][-1]['prompt']
        Answer = sample['data'][-1]["response"][0]

        domain = sample['data'][-1]['response'][-1]
        if 'choice' in sample:
            choice = sample['choice']
            tmp_dict = {"id":id,"prompt":prompt,"response":Answer,"6b":response,"choice":choice,"domain":domain}
        else:
            tmp_dict = {"id":id,"prompt":prompt,"response":Answer,"6b":response, "domain":domain}

        ans_jsons.append(tmp_dict)

    return ans_jsons





@ray.remote(num_gpus=1)
@torch.inference_mode()
def get_model_answers_largescale(model_path, question_jsons):

    disable_torch_init()
    model_path = os.path.expanduser(model_path)
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model = AutoModel.from_pretrained(model_path, trust_remote_code=True).half().cuda()
    model = model.eval()
    ans_jsons = []
    for i, line in enumerate(tqdm(question_jsons)):
      
        sample = json.loads(line)
        
        id = sample['id']
        

        history_par = []
        for i in range(len(sample['data'])-1):
            
            tmp_lst = []
            history_prompt = sample['data'][i]['prompt']
            history_res = sample['data'][i]['response'][0]
            tmp_lst.append(history_prompt)
            tmp_lst.append(history_res)
            history_par.append(tmp_lst)
    
        
        prompt = sample['data'][-1]['prompt']
        Answer = sample['data'][-1]["response"][0]
       
        response, _ = model.chat(tokenizer, prompt, history=history_par,max_length=2048,num_beams=1,do_sample=False,top_p=0.7,temperature=0.01)
        
        
        domain = sample['data'][-1]['response'][-1]
        if 'choice' in sample:
            choice = sample['choice']
            tmp_dict = {"id":id,"prompt":prompt,"response":Answer,"6b":response,"history":history_par,"choice":choice,"domain":domain}
        else:
            tmp_dict = {"id":id,"prompt":prompt,"response":Answer,"6b":response,"history":history_par,"domain":domain}

        ans_jsons.append(tmp_dict)

    return ans_jsons


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-path", type=str,required=True)
    parser.add_argument("--question-file", type=str,required=True)
    parser.add_argument("--answer-file", type=str, default="answer.jsonl")
    parser.add_argument("--num-gpus", type=int, default=8)
    args = parser.parse_args()
    ray.init()
    run_eval(args)



    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-id", type=str, required=True)
    parser.add_argument("--model-path", type=str, required=True)
    parser.add_argument("--question-file", type=str, required=True)
    parser.add_argument("--answer-file", type=str, default="answer.jsonl")
    parser.add_argument("--num-gpus", type=int, default=1)
    parser.add_argument("--max-length", type=int, default=1024)
    parser.add_argument("--num-beams", type=int, default=1)
    parser.add_argument("--do-sample", type=bool, default=True)
    parser.add_argument("--top-p", type=float, default=0.7)
    parser.add_argument("--temperature", type=float, default=0.95)

    args = parser.parse_args()
    """

    #ray.init()
    # run_eval(args.model_path, args.model_id, args.question_file, args.answer_file, args.max_length, args.num_gpus)
    #run_eval(args)
