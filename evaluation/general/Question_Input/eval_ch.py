
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
            temp_rate = eval(line[key])
            temp_count = temp_count + 1
            subject = line['response']["学科"]
        

            subject_flag = "'{}': '{}'".format("学科",subject)
            if subject_flag in str(temp_rate):
                subject_count = subject_count  +1
            
            grade = line['response']["年级"]
            grade_flag = "'{}': '{}'".format("年级",grade)
            if grade_flag in str(temp_rate):
                grade_count = grade_count  +1


            grade_group_name = line['response']["学段"]
            grade_group_name_flag =  "'{}': '{}'".format("学段",grade_group_name)
            if grade_group_name_flag in str(eval(line['130b'])):
                grade_group_name_count = grade_group_name_count  +1


            semester_count_name = line['response']["学期"]
            semester_count_name_flag =  "'{}': '{}'".format("学期",semester_count_name)
            if semester_count_name_flag in str(eval(line['130b'])):
                semester_count = semester_count  +1

            type_name = line['response']["类型"]
            type_name_flag = "'{}': '{}'".format("类型",type_name)
            if type_name_flag in str(eval(line['130b'])):
                type_count = type_count  +1 

            diffuculty_name = line['response']["难度"]
            diffuculty_name_flag =  "'{}': '{}'".format("难度",diffuculty_name)
            if diffuculty_name_flag in str(eval(line['130b'])):
                diffuculty_count = diffuculty_count  +1 
      
        
        except:
            continue


  
    print('模版转化率:', temp_count/len(human_res))
    print('#############################')
    print('学科:',subject_count/len(human_res))
    print('#############################')
    print('年级:',grade_count/len(human_res))
    print('#############################')
    print('学段:',grade_group_name_count/len(human_res))
    print('#############################')
    print('学期:',semester_count/len(human_res))
    print('#############################')
    print('类型:',type_count/len(human_res))
    print('#############################')
    print('难度:',diffuculty_count/len(human_res))



if __name__ == '__main__':

    

    parser = argparse.ArgumentParser()
    parser.add_argument("--inf-file", type=str, required=True)
    parser.add_argument("--inf-key", type=str, default="130b", required=False)
    args = parser.parse_args()

    human_res = load_res_largescale(args.inf_file)
    evalation(human_res, args.inf_key)
   
    print('########### End #############')








    
