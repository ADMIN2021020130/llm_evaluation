import json
import os
import sys
import argparse

def load_infer_res_130b(jsonfile, key="response"):
    lines = open(jsonfile).readlines()
    res = dict()
    for l in lines:
        data = json.loads(l.strip())
        id = data["id"]
        res[id] = data[key]
    return res


def load_human_res_largescale(jsonfile):
    res = list()
    lines = open(jsonfile).readlines()
    for l in lines:
        data = json.loads(l.strip())
        res.append(data)
    return res


def is_right_by_domain(human_label, infer_resp, domain):
    
    
    
    def get_label_by_resp_choices(infer_resp,human_label):
        
        ans_0 = str(infer_resp)[str(infer_resp).find("TALGPT Recommends: "):]
        ans_1 = str(infer_resp)[str(infer_resp).find("the correct option is"):]         
        ans_2 = str(infer_resp)[str(infer_resp).find("recommends that you choose Option"):]
        ans_3 = str(infer_resp)[str(infer_resp).find("答案"):]    
        ans_4 = str(infer_resp)[str(infer_resp).find("TALGPT的回答:"):]   
        ans_5 = str(infer_resp)[str(infer_resp).find("从A到D, 我们应选择"):]
        ans_6 = str(infer_resp)[str(infer_resp).find("TALGPT认为"):]   
        ans_7 = str(infer_resp)[str(infer_resp).find("故选"):]
        
     
        
        if ans_0 is not None and human_label in ans_0:
             return True

        if ans_1 is not None and human_label in ans_1:
            return True
            
           
        if ans_2 is not None and human_label in ans_2:
            return True
        elif ans_3 is not None and human_label in ans_3:
            return True
        elif ans_4 is not None and human_label in ans_4:
            return True
        if  ans_5 is not None and human_label in ans_5:
            return True

        elif ans_6 is not None and human_label in ans_6:
            return True

        elif ans_7 is not None and human_label in ans_7:
             return True
        else:
            False
       
           
    assert domain  in {"gaokao-biology",  
                          "gaokao-chemistry",  
                          "gaokao-chinese", 
                          "gaokao-english", 
                          "gaokao-geography", 
                          "gaokao-history",
                          "gaokao-mathqa",
                          "gaokao-physics",
                          "logiqa-en",
                          "logiqa-zh",
                          "lsat-ar",
                          "lsat-lr",
                          "lsat-rc",
                          "sat-en",
                          "sat-math",
                          "aqua-rat",
                           "JEC-QA-CA",
                           "JEC-QA-KD",
                           "math",  
                           "gaokao-mathcloze",}

    if domain == "gaokao-biology" or "gaokao-chemistry" or "gaokao-chinese" or  "gaokao-geography" :
        if len(human_label)  == 1:
            human_label = human_label
        elif len(human_label) != 1:
            human_label = ''.join(human_label)
            
        result = get_label_by_resp_choices(infer_resp,human_label)
        if result:
            return 1
        else:
            return 0

    elif domain == "gaokao-history" or "gaokao-mathqa" or "gaokao-physics" or  "logiqa-en"or "logiqa-zh":  
        result = get_label_by_resp_choices(infer_resp,human_label)
       
        if len(human_label)  == 1:
            human_label = human_label
        elif len(human_label) != 1:
            human_label = ''.join(human_label)
            
        if result:
            return 1
        else:
            return 0
    
    
    elif domain == "lsat-ar" or "lsat-lr" or "lsat-rc" or  "sat-en"or "sat-math" or "aqua-rat":    
        result = get_label_by_resp_choices(infer_resp,human_label)
        if len(human_label)  == 1:
            human_label = human_label
        elif len(human_label) != 1:
            human_label = ''.join(human_label)
            
        if result:
            return 1
        else:
            return 0
    
    elif domain == "JEC-QA-CA" or "JEC-QA-KD":
        if len(human_label)  == 1:
            human_label = human_label
        elif len(human_label) != 1:
            human_label = ''.join(human_label)
             
        result = get_label_by_resp_choices(human_label)
        if result:
            return 1
        else:
            return 0
        
    elif domain == "math" or "gaokao-mathcloze":
        if len(human_label)  == 1:
            human_label = human_label
        elif len(human_label) != 1:
            human_label = ''.join(human_label)
            
        result = get_label_by_resp_choices(infer_resp,human_label)
        if result:
            return 1
        else:
            return 0


        
def eval(human_res, key):
    domain_count = {}
    domain_count['gaokao-biology'] = 0
    domain_count['gaokao-chemistry'] = 0
    domain_count['gaokao-history'] = 0
    domain_count['gaokao-chinese'] = 0
    domain_count['gaokao-english'] = 0
    domain_count['gaokao-geography'] = 0
    domain_count['gaokao-mathqa'] = 0
    domain_count['gaokao-physics'] = 0
    domain_count['logiqa-en'] = 0
    domain_count['logiqa-zh'] = 0
    domain_count['lsat-ar'] = 0
    domain_count['lsat-lr'] = 0
    domain_count['lsat-rc'] = 0
    domain_count['sat-en'] = 0
    domain_count['sat-math'] = 0
    domain_count['aqua-rat'] = 0
    domain_count['JEC-QA-CA'] = 0
    domain_count['JEC-QA-KD'] = 0
    domain_count['math'] = 0
    domain_count['gaokao-mathcloze'] = 0
    
    
    
    domain_rightcount = {}
    domain_rightcount['gaokao-biology'] = 0
    domain_rightcount['gaokao-chemistry'] = 0
    domain_rightcount['gaokao-chinese'] = 0
    domain_rightcount['gaokao-english'] = 0
    domain_rightcount['gaokao-geography'] = 0
    domain_rightcount['gaokao-mathqa'] = 0
    domain_rightcount['gaokao-physics'] = 0
    domain_rightcount['gaokao-history'] = 0
    domain_rightcount['logiqa-en'] = 0
    domain_rightcount['logiqa-zh'] = 0
    domain_rightcount['lsat-ar'] = 0
    domain_rightcount['lsat-lr'] = 0
    domain_rightcount['lsat-rc'] = 0
    domain_rightcount['sat-en'] = 0
    domain_rightcount['sat-math'] = 0
    domain_rightcount['aqua-rat'] = 0
    domain_rightcount['JEC-QA-CA'] = 0
    domain_rightcount['JEC-QA-KD'] = 0
    domain_rightcount['math'] = 0
    domain_rightcount['gaokao-mathcloze'] = 0
    
    
    
    for item in human_res:
        infer_resp = item[key]
        domain = item['domain'][2]
        if domain != "sat-en-without-passage":
            domain_count[domain] += 1
            human_label = item['response']
            domain_rightcount[domain] += is_right_by_domain(human_label,infer_resp, domain)
    

    all_count = 0
    all_rightcount = 0
    for k in domain_count.keys():
        sub_name = k
        count = domain_count[k]
        all_count += count
        right_count = domain_rightcount[k]
        all_rightcount += right_count
        acc = float(right_count) / float(count)
        print ("Doamin : {}  Count: {}  RightCount: {}  ACC: {}".format(sub_name, count, right_count, acc))
    
    chinese_acc_pre = {"gaokao-biology","gaokao-chemistry","gaokao-history","gaokao-chinese","gaokao-geography","gaokao-physics","gaokao-mathqa","JEC-QA-CA","JEC-QA-KD","logiqa-zh", "gaokao-mathcloze" }
    
    ch_count = 0
    ch_right_count = 0
    for c in chinese_acc_pre:
        ch_name = c
        count = domain_count[c]
        ch_count += count
        right_count = domain_rightcount[c]
        ch_right_count += right_count
        acc = float(right_count) / float(count)
    
    ch_acc_count = ch_right_count/ch_count
    print ("Ch-AGI-Eval Overall********")
    print ("Ch-Count: {}  Ch-RightCount: {} Ch-Acc: {}".format(ch_count, ch_right_count, ch_acc_count))
    print ("***********************")



    all_acc = all_rightcount / all_count
    print ("AGI-Eval Overall********")
    print ("Count: {}  RightCount: {} Acc: {}".format(all_count, all_rightcount, all_acc))
    print ("***********************")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--inf-file", type=str, required=True)
    parser.add_argument("--inf-key", type=str, default="6b", required=False)
    args = parser.parse_args()
    human_res = load_human_res_largescale(args.inf_file)
    eval(human_res, args.inf_key)
