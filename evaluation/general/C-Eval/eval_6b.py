import json
import os
import sys
import difflib
import argparse



c_eval_set = {}
c_eval_set['accountant'] = ""
c_eval_set['advanced_mathematics'] = ""
c_eval_set['art_studies'] = ""
c_eval_set['basic_medicine'] = ""
c_eval_set['business_administration'] =""
c_eval_set['chinese_language_and_literature'] = ""
c_eval_set['civil_servant']= ""
c_eval_set['clinical_medicine'] =""
c_eval_set['college_chemistry'] = ""
c_eval_set['college_economics'] = ""
c_eval_set['college_physics'] = ""
c_eval_set['college_programming'] = ""
c_eval_set['computer_architecture'] = ""
c_eval_set['computer_network'] = ""
c_eval_set['discrete_mathematics'] = ""
c_eval_set['education_science'] = ""
c_eval_set['electrical_engineer'] = ""  
c_eval_set['environmental_impact_assessment_engineer'] = ""
c_eval_set['fire_engineer'] = ""
c_eval_set["high_school_biology"] = ""
c_eval_set["high_school_chemistry"] = ""
c_eval_set["high_school_chinese"] = ""
c_eval_set["high_school_geography"] = ""
c_eval_set["high_school_history"] = ""
c_eval_set["high_school_mathematics"] = ""
c_eval_set["high_school_physics"] = ""
c_eval_set["high_school_politics"] =""
c_eval_set["ideological_and_moral_cultivation"] = ""
c_eval_set["law"] = ""
c_eval_set['legal_professional'] =""
c_eval_set["logic"] = ""
c_eval_set['mao_zedong_thought'] = ""
c_eval_set['marxism'] = ""
c_eval_set['metrology_engineer'] = ""
c_eval_set["middle_school_biology"] = ""
c_eval_set["middle_school_chemistry"] = ""
c_eval_set["middle_school_geography"] = ""
c_eval_set["middle_school_history"] = ""
c_eval_set["middle_school_mathematics"] = ""
c_eval_set["middle_school_physics"] = ""
c_eval_set["middle_school_politics"] = ""
c_eval_set["modern_chinese_history"]= ""
c_eval_set["operating_system"] = ""
c_eval_set["physician"] = ""
c_eval_set["plant_protection"]= ""
c_eval_set['probability_and_statistics'] = ""
c_eval_set['professional_tour_guide'] = ""
c_eval_set['sports_science'] = ""
c_eval_set['tax_accountant'] = ""
c_eval_set['teacher_qualification'] = ""
c_eval_set['urban_and_rural_planner'] = ""
c_eval_set['veterinary_medicine'] = ""


def load_ref_res(jsonfile):
    ref_res = {}
    with open(jsonfile, 'r') as f:
        for line in f.readlines():
            line = json.loads(line.strip())
            id, data = line["id"], line["data"]
            ref_res[id] = data
    return ref_res

def load_inf_res(jsonfile):
    inf_res = {}
    with open(jsonfile, 'r') as f:
        for line in f.readlines():
            line = json.loads(line.strip())
            id, data = line["id"], line["data"]
            inf_res[id] = data
    return inf_res


def load_res_largescale(jsonfile):
    res = list()
    lines = open(jsonfile).readlines()
    for l in lines:
        data = json.loads(l.strip())
        res.append(data)
    return res

def string_similar(s1, s2):
    return difflib.SequenceMatcher(None, s1, s2).quick_ratio()


def is_right_by_domain(human_label, infer_resp, domain,choice):
    
        
    def get_label_by_resp_choices(infer_resp):
        ans = infer_resp[infer_resp.find("答案"):]
        if "A" in ans:
            return "A"
        if "B" in ans:
            return "B"
        if "C" in ans:
            return "C"
        if "D" in ans:
            return "D"
        ans = infer_resp[infer_resp.find("选"):]
        if "A" in ans:
            return "A"
        if "B" in ans:
            return "B"
        if "C" in ans:
            return "C"
        if "D" in ans:
            return "D"
        ans = infer_resp[infer_resp.find("正确")-10:]
        if "A" in ans:
            return "A"
        if "B" in ans:
            return "B"
        if "C" in ans:
            return "C"
        if "D" in ans:
            return "D"
        ration = 0.5
        reslut_key = ""
        lists = ["A", "B", "C", "D"]
        for key in lists:
            similar = string_similar(infer_resp, choice[key])
            if similar > ration:
                reslut_key = key
                ration = similar
            if reslut_key != "":
                return reslut_key
        return -1
        
       
           
    assert domain  in { 
         
        "accountant",
        "advanced_mathematics",
        "art_studies",
        "basic_medicine",
        "business_administration",
        "chinese_language_and_literature",
        "civil_servant",
        "clinical_medicine",
        "college_chemistry",
        "college_economics",
        "college_physics",
        "college_programming",
        "computer_architecture",
        "computer_network",
        "discrete_mathematics",
        "education_science",
        "electrical_engineer",
        "environmental_impact_assessment_engineer",
        "fire_engineer",
        "high_school_biology",
        "high_school_chemistry",
        "high_school_chinese",
        "high_school_geography",
        "high_school_history",
        "high_school_mathematics",
        "high_school_physics",
        "high_school_politics",
        "ideological_and_moral_cultivation",
        "law",
        "legal_professional",
        "logic",
        "mao_zedong_thought",
        "marxism",
        "metrology_engineer",
        "middle_school_biology",
        "middle_school_chemistry",
        "middle_school_geography",
        "middle_school_history",
        "middle_school_mathematics",
        "middle_school_physics",
        "middle_school_politics",
        "modern_chinese_history",
        "operating_system",
        "physician",
        "plant_protection",
        "probability_and_statistics",
        "professional_tour_guide",
        "sports_science",
        "tax_accountant",
        "teacher_qualification",
        "urban_and_rural_planner",
        "veterinary_medicine",}




    if domain in c_eval_set:
        infer_label = get_label_by_resp_choices(infer_resp)
        if human_label == infer_label:
            return 1
        else:
            return 0

        
def eval(ref_res, inf_res):

    domain_count = {}
    domain_count['accountant'] = 0
    domain_count['advanced_mathematics'] = 0
    domain_count['art_studies'] = 0
    domain_count['basic_medicine'] = 0
    domain_count['business_administration'] =0
    domain_count['chinese_language_and_literature'] = 0
    domain_count['civil_servant']= 0
    domain_count['clinical_medicine'] =0
    domain_count['college_chemistry'] = 0
    domain_count['college_economics'] = 0
    domain_count['college_physics'] = 0
    domain_count['college_programming'] = 0
    domain_count['computer_architecture'] = 0
    domain_count['computer_network'] = 0
    domain_count['discrete_mathematics'] = 0
    domain_count['education_science'] = 0
    domain_count['electrical_engineer'] = 0   
    domain_count['environmental_impact_assessment_engineer'] = 0
    domain_count['fire_engineer'] = 0
    domain_count["high_school_biology"] = 0
    domain_count["high_school_chemistry"] = 0
    domain_count["high_school_chinese"] = 0
    domain_count["high_school_geography"] = 0
    domain_count["high_school_history"] = 0
    domain_count["high_school_mathematics"] = 0
    domain_count["high_school_physics"] = 0
    domain_count["high_school_politics"] =0
    domain_count["ideological_and_moral_cultivation"] = 0
    domain_count["law"] = 0
    domain_count['legal_professional'] =0
    domain_count["logic"] = 0
    domain_count['mao_zedong_thought'] = 0
    domain_count['marxism'] = 0
    domain_count['metrology_engineer'] = 0
    domain_count["middle_school_biology"] = 0
    domain_count["middle_school_chemistry"] = 0
    domain_count["middle_school_geography"] = 0
    domain_count["middle_school_history"] = 0
    domain_count["middle_school_mathematics"] = 0
    domain_count["middle_school_physics"] = 0
    domain_count["middle_school_politics"] = 0
    domain_count["modern_chinese_history"]= 0
    domain_count["operating_system"] = 0
    domain_count["physician"] = 0
    domain_count["plant_protection"]= 0
    domain_count['probability_and_statistics'] = 0
    domain_count['professional_tour_guide'] = 0
    domain_count['sports_science'] = 0
    domain_count['tax_accountant'] = 0
    domain_count['teacher_qualification'] = 0
    domain_count['urban_and_rural_planner'] = 0
    domain_count['veterinary_medicine'] = 0


    domain_rightcount = {}
    domain_rightcount['accountant'] = 0
    domain_rightcount['advanced_mathematics'] = 0
    domain_rightcount['art_studies'] = 0
    domain_rightcount['basic_medicine'] = 0
    domain_rightcount['business_administration'] =0
    domain_rightcount['chinese_language_and_literature'] = 0
    domain_rightcount['civil_servant']= 0
    domain_rightcount['clinical_medicine'] =0
    domain_rightcount['college_chemistry'] = 0
    domain_rightcount['college_economics'] = 0
    domain_rightcount['college_physics'] = 0
    domain_rightcount['college_programming'] = 0
    domain_rightcount['computer_architecture'] = 0
    domain_rightcount['computer_network'] = 0
    domain_rightcount['discrete_mathematics'] = 0
    domain_rightcount['education_science'] = 0
    domain_rightcount['electrical_engineer'] = 0   
    domain_rightcount['environmental_impact_assessment_engineer'] = 0
    domain_rightcount['fire_engineer'] = 0
    domain_rightcount["high_school_biology"] = 0
    domain_rightcount["high_school_chemistry"] = 0
    domain_rightcount["high_school_chinese"] = 0
    domain_rightcount["high_school_geography"] = 0
    domain_rightcount["high_school_history"] = 0
    domain_rightcount["high_school_mathematics"] = 0
    domain_rightcount["high_school_physics"] = 0
    domain_rightcount["high_school_politics"] =0
    domain_rightcount["ideological_and_moral_cultivation"] = 0
    domain_rightcount["law"] = 0
    domain_rightcount['legal_professional'] =0
    domain_rightcount["logic"] = 0
    domain_rightcount['mao_zedong_thought'] = 0
    domain_rightcount['marxism'] = 0
    domain_rightcount['metrology_engineer'] = 0
    domain_rightcount["middle_school_biology"] = 0
    domain_rightcount["middle_school_chemistry"] = 0
    domain_rightcount["middle_school_geography"] = 0
    domain_rightcount["middle_school_history"] = 0
    domain_rightcount["middle_school_mathematics"] = 0
    domain_rightcount["middle_school_physics"] = 0
    domain_rightcount["middle_school_politics"] = 0
    domain_rightcount["modern_chinese_history"]= 0
    domain_rightcount["operating_system"] = 0
    domain_rightcount["physician"] = 0
    domain_rightcount["plant_protection"]= 0
    domain_rightcount['probability_and_statistics'] = 0
    domain_rightcount['professional_tour_guide'] = 0
    domain_rightcount['sports_science'] = 0
    domain_rightcount['tax_accountant'] = 0
    domain_rightcount['teacher_qualification'] = 0
    domain_rightcount['urban_and_rural_planner'] = 0
    domain_rightcount['veterinary_medicine'] = 0



    
    # for item in human_res:
    #     infer_resp = item['130b']
    #     domain = item['domain'][2]
    #     domain_count[domain] += 1
    #     human_label = item['response']
    #     choice = item['choice']
    #     domain_rightcount[domain] += is_right_by_domain(human_label,infer_resp, domain,choice)

    for id in ref_res.keys():
        ref_data = ref_res[id][0]
        domain = ref_data['domain'][2]
        domain_count[domain] += 1
        ref_label = ref_data['response'][0][0]
        choice = ref_data['choice']

        inf_data = inf_res[id][0]
        inf_response = inf_data['response'][0][0]

        domain_rightcount[domain] += is_right_by_domain(ref_label, inf_response, domain, choice)


    all_count = 0
    all_rightcount = 0
    for k in domain_count.keys():
        sub_name = k
        count = domain_count[k]
        if  count == 0:
             continue
        else:
            all_count += count
            right_count = domain_rightcount[k]
            all_rightcount += right_count
            acc = float(right_count) / float(count)
            print ("Doamin : {}  Count: {}  RightCount: {}  ACC: {}".format(sub_name, count, right_count, acc))

    all_acc = all_rightcount / all_count
    print ("C-Eval Overall********")
    print ("Count: {}  RightCount: {} Acc: {}".format(all_count, all_rightcount, all_acc))
    print ("***********************")
  
if __name__ == '__main__':
    # human_res = load_res_largescale("./ceval_2240.jsonl")
    #human_res = load_res_largescale("./ceval_8000.jsonl")
    # human_res = load_res_largescale("./ceval_00047_step3000.jsonl")

    parser = argparse.ArgumentParser()
    parser.add_argument("--ref-file", type=str, required=True)
    parser.add_argument("--inf-file", type=str, required=True)
    args = parser.parse_args()

    ref_res = load_ref_res(args.ref_file)
    inf_res = load_inf_res(args.inf_file)
    eval(ref_res, inf_res)
