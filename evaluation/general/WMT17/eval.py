import json
import os
import sys
import difflib
import argparse
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

def load_infer_res_largescale(jsonfile, inf_key):
    lines = open(jsonfile).readlines()
    res = dict()
    for l in lines:
        data = json.loads(l.strip())
        id = data["id"]
        if inf_key == "6b":
            res[id] = data["6b"]
        elif inf_key == "130b":
            res[id] = data["130b"]
        else:
            print("error:模型的inf_key必须是“6b”或“130b”)")
            exit()
    return res

def load_human_res(jsonfile):
    lines = open(jsonfile).readlines()
    res = []
    for l in lines:
        data = json.loads(l.strip())
        res.append(data)
    return res

def load_human_res_largescale(jsonfile):
    res = list()
    lines = open(jsonfile).readlines()
    for l in lines:
        data = json.loads(l.strip())
        res.append(data)
    return res

def compute_metrics(decoded_preds, decoded_labels, mode):
    assert mode in ["zh", "en"]
    #词级别，分词
    labels = []
    if mode == "zh":
        #for content in decoded_labels:
        labels.append(jieba.lcut(decoded_labels.replace(" ", "")))
        preds = jieba.lcut(decoded_preds.replace(" ", ""))
    if mode == "en":
        #for content in decoded_labels:
        labels.append(re.split('(\W+)',decoded_labels))
        preds = re.split('(\W+)',decoded_preds)
    print("labels:", labels)
    print("preds:", preds)
    #计算bleu
    score = sentence_bleu(labels, preds, weights=(0.25, 0.25, 0.25, 0.25))
    return score


def evals(infer_res, human_res):
    total_bleu_score = 0
    zh_to_en = 0
    en_to_zh = 0
    domain_bleu = {"zh-to-en":0, "en-to-zh":0}    
    for item in human_res:
        id = item['id']
        domain = item['domain'][-1] 
        print("domain:", domain)
        if id in infer_res.keys():
            infer_resp = infer_res[id]
        else:
            infer_resp = ""
        if domain == "zh-to-en":
            human_resp = item['response']
            zh_to_en += 1
            domain_bleu[domain] += compute_metrics(infer_resp, human_resp, "en")
        elif domain == "en-to-zh":
            human_resp = item['response']
            en_to_zh += 1
            domain_bleu[domain] += compute_metrics(infer_resp, human_resp, "zh")
        else:
            print("warning, extra keys in testsets")

    for k in domain_bleu.keys():
        if k == "zh-to-en":
            bleu = domain_bleu[k]/zh_to_en
            print ("Doamin : {}  Count: {}  zh-to-en-bleu: {}".format(k, zh_to_en, bleu))
        if k == "en-to-zh":
            bleu = domain_bleu[k]/en_to_zh
            print ("Doamin : {}  Count: {}  en-to-zh-bleu: {}".format(k, en_to_zh, bleu))

    print ("WMT17 Overall********")
    print("all-bleu: {}".format((domain_bleu["zh-to-en"]+domain_bleu["en-to-zh"])/(zh_to_en+en_to_zh)))
    print ("***********************")

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--inf-file", type=str, required=True)
    parser.add_argument("--inf-key", type=str, default="6b", required=False)
    args = parser.parse_args() 
    infer_res = load_infer_res_largescale(args.inf_file, args.inf_key)
    human_res = load_human_res(args.inf_file)
    evals(infer_res, human_res)
    

