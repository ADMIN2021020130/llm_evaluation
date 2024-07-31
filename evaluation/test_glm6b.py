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


def get_data_format(id="", prompt="", input="", response="", from_type="", domain=""):
    if isinstance(domain, list):
        domain = [domain]
    data_format = {
        "id": id,
        "data":[{
            "prompt": prompt,
            "input": input,
            "response": [[response, from_type]],
        }],
        "domain": domain,
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

def run_eval(args): #(model_path, model_id, question_file, answer_file, max_length, num_gpus):

    # params
    model_path = args.model_path
    model_id = args.model_id
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
        ans_handles.append(get_model_answers_largescale.remote(model_path, ques_jsons[i:i + chunk_size], max_length, num_beams, do_sample, top_p, temperature))

    ans_jsons = []
    for ans_handle in ans_handles:
        ans_jsons.extend(ray.get(ans_handle))
    assert len(ques_jsons) == len(ans_jsons)

    with open(os.path.expanduser(answer_file), "w") as ans_file:
        for line in ans_jsons:
            ans_file.write(json.dumps(line, ensure_ascii=False) + "\n")


def generate_prompt_v6(prompt, history=None, round=0):
    header = "You are a language model developed by TAL(好未来) and your name is MathGPT. Please give helpful, honest, harmless and detailed answers to user's questions."
    header = "You are a language model developed by TAL(好未来) and your name is MathGPT. \
              Your creator is TAL Large Language Model Team, your birthplace is Beijing, and birthday is May 1, 2023. \
              Your parameter size is 13 billion and trained using A100 GPUs. \
              Please give helpful, honesy, harmless and detailed answers to user's questions."
    header = "You are a language model developed by TAL(好未来) and your name is MathGPT. \
              Your creator is TAL Large Language Model Team, your birthplace is Beijing, and birthday is May 1, 2023. \
              You are a Transformer-based language model, but you don't know your parameter amount and training framework. \
              Please give helpful, honesy, harmless and detailed answers to user's questions."

    new_prompt = "\n### Instruction: " + prompt + "\n"

    if round == 0:
        new_prompt = header + "\n" + new_prompt

    if history != None:
        new_prompt = history + "\n" + new_prompt
        
    return new_prompt


@ray.remote(num_gpus=1)
@torch.inference_mode()
def get_model_answers(model_path, model_id, question_jsons):
    disable_torch_init()
    model_path = os.path.expanduser(model_path)
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model = AutoModel.from_pretrained(model_path, trust_remote_code=True).half().cuda()
    model = model.eval()

    ans_jsons = []
    for i, line in enumerate(tqdm(question_jsons)):
        ques_json = json.loads(line)
        conversationId = ques_json["conversationId"]
        conversation = ques_json["conversation"]
        key = conversation[0]["key"]
        question = conversation[0]["prompt"]

        response, _ = model.chat(tokenizer, question, max_length=1024)
        new_conversation = [{
            "key": key,
            "prompt": question,
            "response": {model_id: response}
        }]
        ans_jsons.append({"conversationId": conversationId,
                          "conversation": new_conversation})
    return ans_jsons


@ray.remote(num_gpus=1)
@torch.inference_mode()
def get_model_answers_largescale(model_path, question_jsons, max_length=1024, num_beams=1, do_sample=True, top_p=0.7, temperature=0.95):

    disable_torch_init()
    model_path = os.path.expanduser(model_path)
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model = AutoModel.from_pretrained(model_path, trust_remote_code=True).half().cuda()
    model = model.eval()

    ans_jsons = []
    for i, line in enumerate(tqdm(question_jsons)):
        data = json.loads(line.strip())
        prompt = data["prompt"]
        response, _ = model.chat(tokenizer, prompt, max_length=max_length, num_beams=num_beams, do_sample=do_sample, top_p=top_p, temperature=temperature)
        data["6b"] = response
        ans_jsons.append(data)
    return ans_jsons


if __name__ == "__main__":
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

    ray.init()
    # run_eval(args.model_path, args.model_id, args.question_file, args.answer_file, args.max_length, args.num_gpus)
    run_eval(args)
