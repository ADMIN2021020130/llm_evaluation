import re
import os
import sys
import json
import argparse


def load_res_largescale(jsonfile):
    res = list()
    lines = open(jsonfile).readlines()
    for l in lines:
        data = json.loads(l.strip())
        res.append(data)
    return res



cmmlu_set = {}
cmmlu_set = {}
cmmlu_set['ancient_chinese'] = ""
cmmlu_set['modern_chinese'] = ""
cmmlu_set['virology'] = ""
cmmlu_set['nutrition'] = ""
cmmlu_set['chinese_driving_rule'] =""
cmmlu_set['human_sexuality'] = ""
cmmlu_set['college_mathematics']= ""
cmmlu_set['education'] =""
cmmlu_set['agronomy'] = ""
cmmlu_set['computer_security'] = ""
cmmlu_set['clinical_knowledge'] = ""
cmmlu_set['chinese_food_culture'] = ""
cmmlu_set['machine_learning'] = ""
cmmlu_set['high_school_chemistry'] = ""
cmmlu_set['traditional_chinese_medicine'] = ""
cmmlu_set['college_actuarial_science'] = ""
cmmlu_set['journalism'] = ""   
cmmlu_set['sociology'] = ""
cmmlu_set['college_engineering_hydrology'] = ""
cmmlu_set["ethnology"] = ""
cmmlu_set["construction_project_management"] = ""
cmmlu_set["high_school_physics"] = ""
cmmlu_set["college_education"] = ""
cmmlu_set["anatomy"] = ""
cmmlu_set["economics"] = ""
cmmlu_set["business_ethics"] = ""
cmmlu_set["professional_psychology"] =""
cmmlu_set["security_study"] = ""
cmmlu_set["college_medicine"] = ""
cmmlu_set['elementary_mathematics'] =""
cmmlu_set["chinese_foreign_policy"] = ""
cmmlu_set['college_medical_statistics'] = ""
cmmlu_set['computer_science'] = ""
cmmlu_set['marketing'] = ""
cmmlu_set["elementary_information_and_technology"] = ""
cmmlu_set["arts"] = ""
cmmlu_set["chinese_history"] = ""
cmmlu_set["elementary_chinese"] = ""
cmmlu_set["legal_and_moral_basis"] = ""
cmmlu_set["world_religions"] = ""
cmmlu_set["professional_law"] = ""
cmmlu_set["chinese_literature"]= ""
cmmlu_set["conceptual_physics"] = ""
cmmlu_set["professional_medicine"] = ""
cmmlu_set["high_school_mathematics"]= ""
cmmlu_set['genetics'] = ""
cmmlu_set['international_law'] = ""
cmmlu_set['elementary_commonsense'] = ""
cmmlu_set['philosophy'] = ""
cmmlu_set['management'] = ""
cmmlu_set['food_science'] = ""
cmmlu_set['public_relations'] = ""
cmmlu_set['professional_accounting'] = ""
cmmlu_set['global_facts'] = ""
cmmlu_set['chinese_civil_service_exam'] = ""
cmmlu_set['college_law'] = ""
cmmlu_set['sports_science'] = ""
cmmlu_set['high_school_geography'] = ""
cmmlu_set['world_history'] = ""
cmmlu_set['high_school_politics'] = ""
cmmlu_set['high_school_biology'] = ""
cmmlu_set['marxist_theory'] = ""
cmmlu_set['logical'] = ""
cmmlu_set['chinese_teacher_qualification'] = ""
cmmlu_set['electrical_engineering'] = ""
cmmlu_set['astronomy'] = ""
cmmlu_set['jurisprudence'] = ""





def is_right_by_domain(human_label, infer_resp, domain):
    
        
    def get_label_by_resp_choices(infer_resp):
        
        """
        if re.search("答案:|答案为", infer_resp) is not None:

        res = re.split("答案:|答案为[:]*", infer_resp)[-1].strip().split("\n")[0].strip().upper()
        ans = re.sub(r"\$|\;|\n|；|\\right|\\left|。", "", res).replace("\.$", "").replace(" ", "").replace("dfrac", "frac")
        return ans
        """
        if "A" or "B" or "C" or "D" in infer_resp:
            if "答案" in infer_resp:
                infer_resp = infer_resp[infer_resp.find("答案")]
                pattern = r'[A-Da-d]'
                matches = re.findall(pattern, infer_resp)
                ans = "".join(matches).strip().upper()
                return ans
            
            elif "故选" in infer_resp:
                pattern = r'[A-Da-d]'
                match = re.search(pattern, infer_resp)
                ans = match.group().strip().upper()
                return ans
            else:
                ans = re.sub(r'\$+', '', infer_resp).strip().upper()
                return ans
       



            
      

    assert domain  in { 
       "ancient_chinese" ,
       "modern_chinese",
       "virology",
       "nutrition",
       "chinese_driving_rule",
       "human_sexuality",
       "college_mathematics",
       "education",
       "agronomy",
       "computer_security",
       "clinical_knowledge",
       "chinese_food_culture",
       "machine_learning",
       "high_school_chemistry",
       "traditional_chinese_medicine",
       "college_actuarial_science",
       "journalism",
       "sociology",
       "college_engineering_hydrology",
       "ethnology",
       "construction_project_management",
       "high_school_physics",
       "college_education",
       "anatomy",
       "economics",
       "business_ethics",
       "professional_psychology",
       "security_study",
       "college_medicine",
       "elementary_mathematics",
       "chinese_foreign_policy",
       "college_medical_statistics",
       "computer_science",
       "marketing",
       "elementary_information_and_technology",
       "arts",
       "chinese_history",
       "elementary_chinese",
       "legal_and_moral_basis",
       "world_religions",
       "professional_law",
       "chinese_literature",
       "conceptual_physics",
       "professional_medicine",
       "high_school_mathematics",
       "genetics",
       "international_law",
       "elementary_commonsense",
       "philosophy",
       "management",
       "food_science",
       "public_relations",
       "professional_accounting",
       "global_facts",
       "chinese_civil_service_exam",
       "college_law",
       "sports_science",
       "high_school_geography",
       "world_history",
       "high_school_politics",
       "high_school_biology",
       "marxist_theory",
       "logical",
       "chinese_teacher_qualification",
       "electrical_engineering",
       "astronomy",
       "jurisprudence",
    }

    if domain in cmmlu_set:
        
    
        infer_label = get_label_by_resp_choices(infer_resp)

        # print('############### infer_label  #############')
        # print(infer_label)

        
        if human_label == infer_label:
            return 1
        else:
            return 0
        


def eval(human_res, inf_key):
    domain_count = {}
    domain_count['ancient_chinese'] = 0
    domain_count['modern_chinese'] = 0
    domain_count['virology'] = 0
    domain_count['nutrition'] = 0
    domain_count['chinese_driving_rule'] =0
    domain_count['human_sexuality'] = 0
    domain_count['college_mathematics']= 0
    domain_count['education'] =0
    domain_count['agronomy'] = 0
    domain_count['computer_security'] = 0
    domain_count['clinical_knowledge'] = 0
    domain_count['chinese_food_culture'] = 0
    domain_count['machine_learning'] = 0
    domain_count['high_school_chemistry'] = 0
    domain_count['traditional_chinese_medicine'] = 0
    domain_count['college_actuarial_science'] = 0
    domain_count['journalism'] = 0   
    domain_count['sociology'] = 0
    domain_count['college_engineering_hydrology'] = 0
    domain_count["ethnology"] = 0
    domain_count["construction_project_management"] = 0
    domain_count["high_school_physics"] = 0
    domain_count["college_education"] = 0
    domain_count["anatomy"] = 0
    domain_count["economics"] = 0
    domain_count["business_ethics"] = 0
    domain_count["professional_psychology"] =0
    domain_count["security_study"] = 0
    domain_count["college_medicine"] = 0
    domain_count['elementary_mathematics'] =0
    domain_count["chinese_foreign_policy"] = 0
    domain_count['college_medical_statistics'] = 0
    domain_count['computer_science'] = 0
    domain_count['marketing'] = 0
    domain_count["elementary_information_and_technology"] = 0
    domain_count["arts"] = 0
    domain_count["chinese_history"] = 0
    domain_count["elementary_chinese"] = 0
    domain_count["legal_and_moral_basis"] = 0
    domain_count["world_religions"] = 0
    domain_count["professional_law"] = 0
    domain_count["chinese_literature"]= 0
    domain_count["conceptual_physics"] = 0
    domain_count["professional_medicine"] = 0
    domain_count["high_school_mathematics"]= 0
    domain_count['genetics'] = 0
    domain_count['international_law'] = 0
    domain_count['elementary_commonsense'] = 0
    domain_count['philosophy'] = 0
    domain_count['management'] = 0
    domain_count['food_science'] = 0
    domain_count['public_relations'] = 0
    domain_count['professional_accounting'] = 0
    domain_count['global_facts'] = 0
    domain_count['chinese_civil_service_exam'] = 0
    domain_count['college_law'] = 0
    domain_count['sports_science'] = 0
    domain_count['high_school_geography'] = 0
    domain_count['world_history'] = 0
    domain_count['high_school_politics'] = 0
    domain_count['high_school_biology'] = 0
    domain_count['marxist_theory'] = 0
    domain_count['logical'] = 0
    domain_count['chinese_teacher_qualification'] = 0
    domain_count['electrical_engineering'] = 0
    domain_count['astronomy'] = 0
    domain_count['jurisprudence'] = 0


    domain_rightcount = {}
    domain_rightcount['ancient_chinese'] = 0
    domain_rightcount['modern_chinese'] = 0
    domain_rightcount['virology'] = 0
    domain_rightcount['nutrition'] = 0
    domain_rightcount['chinese_driving_rule'] =0
    domain_rightcount['human_sexuality'] = 0
    domain_rightcount['college_mathematics']= 0
    domain_rightcount['education'] =0
    domain_rightcount['agronomy'] = 0
    domain_rightcount['computer_security'] = 0
    domain_rightcount['clinical_knowledge'] = 0
    domain_rightcount['chinese_food_culture'] = 0
    domain_rightcount['machine_learning'] = 0
    domain_rightcount['high_school_chemistry'] = 0
    domain_rightcount['traditional_chinese_medicine'] = 0
    domain_rightcount['college_actuarial_science'] = 0
    domain_rightcount['journalism'] = 0   
    domain_rightcount['sociology'] = 0
    domain_rightcount['college_engineering_hydrology'] = 0
    domain_rightcount["ethnology"] = 0
    domain_rightcount["construction_project_management"] = 0
    domain_rightcount["high_school_physics"] = 0
    domain_rightcount["college_education"] = 0
    domain_rightcount["anatomy"] = 0
    domain_rightcount["economics"] = 0
    domain_rightcount["business_ethics"] = 0
    domain_rightcount["professional_psychology"] =0
    domain_rightcount["security_study"] = 0
    domain_rightcount["college_medicine"] = 0
    domain_rightcount['elementary_mathematics'] =0
    domain_rightcount["chinese_foreign_policy"] = 0
    domain_rightcount['college_medical_statistics'] = 0
    domain_rightcount['computer_science'] = 0
    domain_rightcount['marketing'] = 0
    domain_rightcount["elementary_information_and_technology"] = 0
    domain_rightcount["arts"] = 0
    domain_rightcount["chinese_history"] = 0
    domain_rightcount["elementary_chinese"] = 0
    domain_rightcount["legal_and_moral_basis"] = 0
    domain_rightcount["world_religions"] = 0
    domain_rightcount["professional_law"] = 0
    domain_rightcount["chinese_literature"]= 0
    domain_rightcount["conceptual_physics"] = 0
    domain_rightcount["professional_medicine"] = 0
    domain_rightcount["high_school_mathematics"]= 0
    domain_rightcount['genetics'] = 0
    domain_rightcount['international_law'] = 0
    domain_rightcount['elementary_commonsense'] = 0
    domain_rightcount['philosophy'] = 0
    domain_rightcount['management'] = 0
    domain_rightcount['food_science'] = 0
    domain_rightcount['public_relations'] = 0
    domain_rightcount['professional_accounting'] = 0
    domain_rightcount['global_facts'] = 0
    domain_rightcount['chinese_civil_service_exam'] = 0
    domain_rightcount['college_law'] = 0
    domain_rightcount['sports_science'] = 0
    domain_rightcount['high_school_geography'] = 0
    domain_rightcount['world_history'] = 0
    domain_rightcount['high_school_politics'] = 0
    domain_rightcount['high_school_biology'] = 0
    domain_rightcount['marxist_theory'] = 0
    domain_rightcount['logical'] = 0
    domain_rightcount['chinese_teacher_qualification'] = 0
    domain_rightcount['electrical_engineering'] = 0
    domain_rightcount['astronomy'] = 0
    domain_rightcount['jurisprudence'] = 0

    for item in human_res:
        if inf_key in item.keys():
            infer_resp = item[inf_key]
        else:
            infer_resp = item['6b']
   

        domain = item['domain'][2]
        domain_count[domain] += 1
        

        human_label = item['response'][0].upper()
      
      


    
        defen  = is_right_by_domain(human_label,infer_resp, domain)


        # if defen == 0:
        #     print (infer_resp)
        domain_rightcount[domain] += defen

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
   

    math_acc_pre = {"high_school_mathematics","elementary_mathematics","college_mathematics"}
    math_count = 0
    math_right_count = 0
    for c in math_acc_pre:
        math_name = c
        count = domain_count[c]
        math_count += count
        right_count = domain_rightcount[c]
        math_right_count += right_count
        acc = float(right_count) / float(count)

    math_acc_count = math_right_count/math_count
    print ("MATH-CMMLU-Eval Overall********")
    print ("MATH-Count: {}  MATH-RightCount: {} MATH-Acc: {}".format(math_count, math_right_count, math_acc_count))
    print ("***********************")



    print ("CCMLU Overall********")
    print ("Count: {}  RightCount: {} Acc: {}".format(all_count, all_rightcount, all_acc))
    print ("***********************")  




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--inf-file", type=str, required=True)
    parser.add_argument("--inf-key", type=str, default="6b", required=False)
    args = parser.parse_args()
    human_res = load_res_largescale(args.inf_file)
    eval(human_res, args.inf_key)


