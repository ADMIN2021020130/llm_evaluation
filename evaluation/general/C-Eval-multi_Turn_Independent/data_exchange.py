import os
import json
import uuid
import random
import numpy as np

def generate_unique_id(): 
    unique_id = str(uuid.uuid4()) 
    return unique_id

def multi_format(prompt,response,label):
    content = {'prompt':prompt,'input':'','response':[response , label]}
    return content

def standard_format(id,data,domain):
    sample =  {'id':id,'data':data,'domain':[domain]}
    return sample

def multi_format_activate(id,multi_round_bucket,domain):
    round_scond = [multi_round_bucket[-2],multi_round_bucket[-1]]
    round_third =  [multi_round_bucket[-3],multi_round_bucket[-2],multi_round_bucket[-1]]
    round_fourth =  [multi_round_bucket[-4],multi_round_bucket[-3],multi_round_bucket[-2],multi_round_bucket[-1]]
    round_five =  [multi_round_bucket[-5],multi_round_bucket[-4],multi_round_bucket[-3],multi_round_bucket[-2],multi_round_bucket[-1]]

    round_scond_sample = standard_format(id,round_scond,domain)
    round_third_sample = standard_format(id,round_third,domain)
    round_fourth_sample = standard_format(id,round_fourth,domain)
    round_five_sample = standard_format(id,round_five,domain)


    return round_scond_sample, round_third_sample, round_fourth_sample, round_five_sample


# 数据层
"""
    non_format_data: math401和教研云无格式训练集数据组成
    地址：/mnt/pfs/jinfeng_team/SFT/dengshuhao1/wzd_folder/online_badcase_fix/non_format_data/
    biaozhun_format_data：教研云标准格式的数据
    地址：/mnt/pfs/jinfeng_team/SFT/dengshuhao1/wzd_folder/online_badcase_fix/non_format_data/
    [分析 详解  点睛]

"""
def data_bucket():
    biaozhun_format_data = "./format_data/ceval_all_no_shot_v3_middle_school_mathematics.json"
    non_format_data ="./non_format_data/non_format_data_shuf.jsonl"
    fr_biaozhun_format_data = open(biaozhun_format_data).readlines()
    fr_non_format_data= open(non_format_data).readlines()

    return fr_biaozhun_format_data,fr_non_format_data


def multi_round_prepare(fr_biaozhun_format_data,fr_non_format_data,output_file):
    fw_second = open(output_file.split('.')[0] + "_RD2.jsonl",'w')
    fw_third = open(output_file.split('.')[0] + "_RD3.jsonl",'w')
    fw_fourth = open(output_file.split('.')[0] + "_RD4.jsonl",'w')
    fw_five = open(output_file.split('.')[0] + "_RD5.jsonl",'w')
    fw = open(output_file,'w')
    
    for l in range(177):
        sample =  json.loads(fr_biaozhun_format_data[l])

        # 防止重采样
        biaozhun_format_data_ = np.arange(0,len(fr_biaozhun_format_data))
        non_format_data_ = np.arange(0,len(fr_non_format_data))
       
        # 轮数拼接
        task_lst = ['biaozhun_format_data','non_format_data', 'non_format_data', 'non_format_data']
        multi_round_bucket = []

        for i in range(7):
            task = random.choice(task_lst)
            if task == "biaozhun_format_data":
                count = np.random.choice(biaozhun_format_data_)
                biaozhun_format_data_ = biaozhun_format_data_[biaozhun_format_data_ != count]
                pro = json.loads(fr_biaozhun_format_data[count])["prompt"]
                res = json.loads(fr_biaozhun_format_data[count])["response"]
                label = json.loads(fr_biaozhun_format_data[count])["domain"][1]
                multi_round_bucket.append(multi_format(pro,res,label))
               
            elif task == "non_format_data":
                count = np.random.choice(non_format_data_)
                non_format_data_ = non_format_data_[non_format_data_ != count]
                pro = json.loads(fr_non_format_data[count])['data'][0]["prompt"]
                res = json.loads(fr_non_format_data[count])['data'][0]["response"][0][0]
                label = json.loads(fr_non_format_data[count])['data'][0]["response"][0][1]
                multi_round_bucket.append(multi_format(pro,res,label))

        # 准备最后一轮样本
        id = generate_unique_id()
        pro = json.loads(fr_biaozhun_format_data[l])["prompt"]
        res = json.loads(fr_biaozhun_format_data[l])["response"]
        label = json.loads(fr_biaozhun_format_data[l])["domain"][1]
        multi_round_bucket.append(multi_format(pro,res,label))

        domain = "online badcase fix --多轮抗干扰数据"
        sample_fromat = standard_format(id,multi_round_bucket,domain)
        second_ , third_, fourth_, five_ = multi_format_activate(id,multi_round_bucket,domain)
   
        fw_second.write(json.dumps(second_,ensure_ascii=False)+"\n")
        fw_third.write(json.dumps(third_,ensure_ascii=False)+"\n")
        fw_fourth.write(json.dumps(fourth_,ensure_ascii=False)+"\n")
        fw_five.write(json.dumps(fourth_,ensure_ascii=False)+"\n")
        fw.write(json.dumps(sample_fromat,ensure_ascii=False)+"\n")
        
    fw.close()
    fw_second.close()
    fw_third.close()
    fw_fourth.close()
       

if __name__ == "__main__":

    # 数据准备
    fr_biaozhun_format_data,fr_non_format_data = data_bucket()
    print(len(fr_biaozhun_format_data),len(fr_non_format_data))
    output_file = "ceval_all_no_shot_v3_middle_school_mathematics.json"
    multi_round_prepare(fr_biaozhun_format_data,fr_non_format_data,output_file)



