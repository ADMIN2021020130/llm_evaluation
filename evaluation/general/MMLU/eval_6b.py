import json
import os
import sys
import difflib
import argparse

def load_infer_res_largescale(jsonfile):
    lines = open(jsonfile).readlines()
    res = dict()
    for l in lines:
        data = json.loads(l.strip())
        id = data["id"]
        res[id] = data["data"][0]["response"][0][0]
    return res

def load_human_res(jsonfile):
    lines = open(jsonfile).readlines()
    res = []
    for l in lines:
        data = json.loads(l.strip())
        res.append(data)
    return res

def string_similar(s1, s2):
    return difflib.SequenceMatcher(None, s1, s2).quick_ratio()

def is_right_by_domain(human_resp, infer_resp, domain):
    def get_label_by_resp_MMLU(resp, choice):
        if resp[:3].find("A") != -1:
            return "A"
        if resp[:3].find("B") != -1:
            return "B"
        if resp[:3].find("C") != -1:
            return "C"
        if resp[:3].find("D") != -1:
            return "D"
        
        num = max(resp.find("answer"), resp.find("Answer"))
        if (num>-1):
            ans = resp[num:]
            if "A" in ans:
                 return "A"
            if "B" in ans:
                return "B"
            if "C" in ans:
                return "C"
            if "D" in ans:
                return "D"
        
        ration = 0.8
        reslut_key = ""
        for key in choice.keys():
            try:
                similar = string_similar(resp, choice[key])
                if similar > ration:
                    reslut_key = key
                    ration = similar
            except:
                pass
        if reslut_key != "":
            return reslut_key
        return -1
 
    choice = human_resp["data"][0]["choice"]
    predict = get_label_by_resp_MMLU(infer_resp, choice)
    label = human_resp["data"][0]["response"][0][0]
    print("*******"*15)
    print("infer_resp:", infer_resp)
    print("choice:", choice)
    print("predict:", predict)
    print("label:", label)
    if(predict == label):
        return 1
    else:
        return 0    

def load_human_res_largescale(jsonfile):
    res = list()
    lines = open(jsonfile).readlines()
    for l in lines:
        data = json.loads(l.strip())
        res.append(data)
    return res

def evals(infer_res, human_res):
    subcategories = {
    "abstract_algebra": ["math"],
    "anatomy": ["health"],
    "astronomy": ["physics"],
    "business_ethics": ["business"],
    "clinical_knowledge": ["health"],
    "college_biology": ["biology"],
    "college_chemistry": ["chemistry"],
    "college_computer_science": ["computer science"],
    "college_mathematics": ["math"],
    "college_medicine": ["health"],
    "college_physics": ["physics"],
    "computer_security": ["computer science"],
    "conceptual_physics": ["physics"],
    "econometrics": ["economics"],
    "electrical_engineering": ["engineering"],
    "elementary_mathematics": ["math"],
    "formal_logic": ["philosophy"],
    "global_facts": ["other"],
    "high_school_biology": ["biology"],
    "high_school_chemistry": ["chemistry"],
    "high_school_computer_science": ["computer science"],
    "high_school_european_history": ["history"],
    "high_school_geography": ["geography"],
    "high_school_government_and_politics": ["politics"],
    "high_school_macroeconomics": ["economics"],
    "high_school_mathematics": ["math"],
    "high_school_microeconomics": ["economics"],
    "high_school_physics": ["physics"],
    "high_school_psychology": ["psychology"],
    "high_school_statistics": ["math"],
    "high_school_us_history": ["history"],
    "high_school_world_history": ["history"],
    "human_aging": ["health"],
    "human_sexuality": ["culture"],
    "international_law": ["law"],
    "jurisprudence": ["law"],
    "logical_fallacies": ["philosophy"],
    "machine_learning": ["computer science"],
    "management": ["business"],
    "marketing": ["business"],
    "medical_genetics": ["health"],
    "miscellaneous": ["other"],
    "moral_disputes": ["philosophy"],
    "moral_scenarios": ["philosophy"],
    "nutrition": ["health"],
    "philosophy": ["philosophy"],
    "prehistory": ["history"],
    "professional_accounting": ["other"],
    "professional_law": ["law"],
    "professional_medicine": ["health"],
    "professional_psychology": ["psychology"],
    "public_relations": ["politics"],
    "security_studies": ["politics"],
    "sociology": ["culture"],
    "us_foreign_policy": ["politics"],
    "virology": ["health"],
    "world_religions": ["philosophy"],
    }
    categories = {
    "STEM": ["physics", "chemistry", "biology", "computer science", "math", "engineering"],
    "humanities": ["history", "philosophy", "law"],
    "social sciences": ["politics", "culture", "economics", "geography", "psychology"],
    "other (business, health, misc.)": ["other", "business", "health"],
    }
    domain_count = {}
    domain_rightcount = {}
    for key in subcategories.keys():
        domain_count[key] = 0
        domain_rightcount[key] = 0

    for item in human_res:
        id = item['id']
        if id in infer_res.keys():
            infer_resp = infer_res[id]
        else:
            infer_resp = ""
        
        domain = item['domain'][-1]
        domain_count[domain] += 1
        human_resp = item
        domain_rightcount[domain] += is_right_by_domain(human_resp, infer_resp, domain)
    
    all_count = 0
    all_rightcount = 0
    for k in domain_count.keys():
        count = domain_count[k]
        all_count += count
        right_count = domain_rightcount[k]
        all_rightcount += right_count
        acc = float(right_count) / float(count)
        print ("Doamin : {}  Count: {}  RightCount: {}  ACC: {}".format(k, count, right_count, acc))

    print ("MMLU Overall********")
    print ("Count: {}  RightCount: {} Acc: {}".format(all_count, all_rightcount, all_rightcount/all_count))
    print ("***********************")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--ref-file", type=str, required=True)
    parser.add_argument("--inf-file", type=str, required=True)
    args = parser.parse_args()
    human_res = load_human_res_largescale(args.ref_file)
    infer_res = load_infer_res_largescale(args.inf_file)
    evals(infer_res, human_res)
     
    #infer_res = load_infer_res_largescale("infer_res_v3.2.json")
    #human_res = load_human_res("human_res.json")
    #evals(infer_res, human_res)
    
