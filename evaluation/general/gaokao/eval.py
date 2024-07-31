import json
from tqdm import tqdm
import os
import numpy as np
import csv
import pandas as pd
import sys
import argparse


def load_jsonl_file(file_path):
    print("load jsonl data {}".format(file_path))   
    data = []
    with open(file_path, 'r') as file:
        for line in tqdm(file.readlines()):
            data_j = json.loads(line)
            data.append(data_j)

    return data

def save_jsonl_file(data, file_path):
    print("save data {}".format(file_path))
    with open(file_path, 'w') as file:
        for item in data:
            json_str = json.dumps(item, ensure_ascii=False)
            file.write(json_str + '\n')
            

def result_analysis(data, key):
    
    data_res = []
    for item in tqdm(data):
        response = item["response"]
        result = item[key]
        q_type = item["logicQuesTypeName"]
        
        score = res_match(result, response, q_type)
        item["score"] = score
    
        data_res.append(item)
    
    return data_res
        
        
def res_match(result, response, q_type):
    
    try:
        answer_idx = result.index("答案:")
        answer = result[answer_idx + len("答案:"):].strip()
        
        if q_type == "QA":
            score = 0
            answer = answer.replace("\n", "")
            if answer in response:
                score = 1
        elif q_type == "cloze":
            response = response.replace("\n", "").replace("$", "").replace(" ", "")
            answers = answer.replace("\n", "").replace("$", "").replace(" ", "")
            score = 1
            if response != answers:
                    score = 0
                    #print(response, "|", answers, "|", answer)
        else:
            #print("Unknown q_type {}".format(q_type))
            score = 0
    except ValueError:
        score = 0
                          
    return score  



def res_statistics_type(data):
    
    statistic = {}
    for item in tqdm(data):
        score = item["score"]
        q_type = item["logicQuesTypeName"]
        exam = item["exam"]

        if q_type not in statistic.keys(): 
            statistic[q_type] = {exam:[score]}
        else:
            if exam in statistic[q_type].keys():
                statistic[q_type][exam].append(score)
            else:
                 statistic[q_type][exam] = [score]
    
    all_count = 0
    avg_acc = 0
    for key in statistic.keys():
        for exam in statistic[key].keys(): 
                q_num = len(statistic[key][exam])
                q_num_t = np.sum(statistic[key][exam])
                all_count += q_num
               
                acc = round(q_num_t / q_num, 2)
                avg_acc += float(q_num) * acc

                #statistic[key][exam]["res"] = [q_num, acc]
                
                log = "subject:{} q_type:{} num:{} acc:{}".format(key, exam, q_num, acc)
                # ["subject", "grade", "type", "number", "Acc"]
    
                print(log)
    avg_acc = avg_acc / float(all_count)
    print ("All count: {} Avg acc: {}".format(all_count, avg_acc))
    
    return statistic






if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--inf-file", type=str, required=True)
    parser.add_argument("--inf-key", type=str, default="6b", required=False)
    args = parser.parse_args()
    # file_path = "/tal-vePFS/PPO/Zack/GAOKAO-Bench/result/2100_Mathgpt_tk0_tp1_t0.jsonl"
    file_path = args.inf_file
     
    data = load_jsonl_file(file_path)

    data = result_analysis(data, key=args.inf_key)
    
    data_type = res_statistics_type(data)
    


    

    
    
    
