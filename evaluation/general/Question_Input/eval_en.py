
import json
import os
import sys
import difflib
import argparse

def load_res_largescale(jsonfile):
    res = list()
    lines = open(jsonfile).readlines()
    for l in lines:
        data = json.loads(l.strip())
        res.append(data)
    return res

def evalation(human_res, key):
    temp_count = 0
    grade_count = 0
    subject_count = 0
    grade_group_name_count = 0
    semester_count = 0
    type_count = 0
    diffuculty_count = 0

    for line in human_res:
        

        try:
            temp_rate =  eval(line[key])
            temp_count = temp_count + 1
            

            subject = line['response']["subject"]
            subject_flag = "'{}': '{}'".format("subject",subject)  
            if subject_flag in str(temp_rate):
                subject_count = subject_count  +1
        

            grade = line['response']["grade"]
            grade_flag =  "'{}': '{}'".format("grade",grade)  
            if grade_flag in str(temp_rate):
                grade_count = grade_count  +1

            grade_group_name = line['response']["grade_group_name"]
            grade_group_name_flag =   "'{}': '{}'".format("grade_group_name",grade_group_name)  
            if grade_group_name_flag in str(temp_rate):
                grade_group_name_count = grade_group_name_count  +1


            semester_count_name = line['response']["semester"]
            semester_count_name_flag = "'{}': '{}'".format("semester",semester_count_name)  
            if semester_count_name_flag in str(temp_rate):
                semester_count = semester_count  +1

            type_name = line['response']["que_type"]
            type_name_flag =  "'{}': '{}'".format("que_type",type_name)  
            if type_name_flag in str(temp_rate):
                type_count = type_count  +1 

            diffuculty_name = line['response']["diffuculty"]
            diffuculty_name_flag =   "'{}': '{}'".format("diffuculty",diffuculty_name)  
            if diffuculty_name_flag in str(temp_rate):
                diffuculty_count = diffuculty_count  +1 
        except:
            continue

    print('#############################')
    print('temp_rate_acc:', temp_count, len(human_res),  temp_count/len(human_res))
    print('#############################')
    print('subject_acc:', subject_count, len(human_res), subject_count/len(human_res))
    print('#############################')
    print('grade_acc:',grade_count,len(human_res),grade_count/len(human_res))
    print('#############################')
    print('grade_group_name_acc:', grade_group_name_count, len(human_res), grade_group_name_count/len(human_res))
    print('#############################')
    print('semester_acc:', semester_count, len(human_res), semester_count/len(human_res))
    print('#############################')
    print('que_type_acc:', type_count, len(human_res), type_count/len(human_res))
    print('#############################')
    print('diffuculty_acc:', diffuculty_count, len(human_res), diffuculty_count/len(human_res))


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--inf-file", type=str, required=True)
    parser.add_argument("--inf-key", type=str, default="130b", required=False)
    args = parser.parse_args()

    human_res = load_res_largescale(args.inf_file)
    evalation(human_res, args.inf_key)
   
    print('########### End #############')








    
