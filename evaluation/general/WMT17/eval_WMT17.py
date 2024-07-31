import json
import re, copy
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge import Rouge
import numpy as np
from transformers import BertTokenizer
from transformers import AutoTokenizer, AutoModel
import jieba
import torch

torch.cuda.set_device(4)

def compute_metrics(decoded_preds, decoded_labels, mode):
    assert mode in ["zh", "en"]
    #词级别，分词
    labels = []
    if mode == "zh":
        for content in decoded_labels:
            labels.append(jieba.lcut(content.replace(" ", "")))
        preds = jieba.lcut(decoded_preds.replace(" ", ""))
    if mode == "en":
        for content in decoded_labels:
            labels.append(re.split('(\W+)',content))
        preds = re.split('(\W+)',decoded_preds) 
    print("labels:", labels)
    print("preds:", preds)
    #计算bleu
    score = sentence_bleu(labels, preds, weights=(0.25, 0.25, 0.25, 0.25))
    return score

def load_model(model_path, model_type="THUDM/chatglm-6b"):
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model = AutoModel.from_pretrained(model_path, trust_remote_code=True).half().cuda()
    model.cuda()
    model = model.eval()
    return tokenizer, model

def get_model_response(tokenizer, model, prompt):
    response, history = model.chat(tokenizer, prompt, history=[])
    return response

if __name__ == "__main__":
    fr = open("test_en_to_zh.json", "r")
    count = 0
    total_bleu_score = 0
    model_path = "/mnt/pfs/jinfeng_team/SFT/caiguodu/workspace/projects/largescale_for_glm_series/exp/chatglm-sft-combine-v3.2/global_step9675-hf"
    tokenizer, model = load_model(model_path, model_type="THUDM/chatglm-6b")
    for i in fr.readlines():
        print("*****"*10,  flush=True)
        content = eval(i)
        prompt = content["data"][0]["prompt"]
        label = [content["data"][0]["response"][0][0]]
        response = get_model_response(tokenizer, model, prompt)
        bleu_score = compute_metrics(response, label, "zh")
        count += 1
        total_bleu_score += bleu_score
        print("prompt:", prompt,  flush=True)
        print("label:", label,  flush=True)
        print("response:", response,  flush=True)
        print("bleu_score:", bleu_score,  flush=True)
    print("ave_bleu_score:", total_bleu_score/count,  flush=True)
         
