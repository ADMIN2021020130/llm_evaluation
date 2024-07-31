import sys
import os
import json
import argparse

def parse_json_file(json_file):
    res = dict()
    # data = json.load(open(json_file))
    with open(json_file, 'r') as fr:
        for idx, line in enumerate(fr.readlines()):
            line = json.loads(line)
            id = line["id"]
            data = line["data"][0]
            prompt = data["prompt"]
            response = data["response"][0][0]
            ori_res = response.replace("。"," ").strip()
            try:
                if ori_res.find("因此，") != -1:
                    real_res = float(ori_res.split("因此，")[-1].split("=")[-1].strip())
                elif ori_res.find("所以") != -1:
                    real_res = float(ori_res.split("所以")[-1].split("=")[-1].strip())
                elif ori_res.find("is") != -1:
                    real_res = float(ori_res.split("is")[-1].strip())
                elif ori_res.find("结果是") != -1:
                    real_res = float(ori_res.split("结果是")[-1].strip())
                elif ori_res.find("答案为") != -1:
                    real_res = float(ori_res.split("答案为")[-1].strip())
                elif ori_res.find("等于") != -1:
                    real_res = float(ori_res.split("等于")[-1].strip())
                elif ori_res.find("R") != -1:
                    real_res = float(ori_res.split("=")[-1].strip().split()[0])
                elif ori_res.find("=") != -1:
                    real_res = float(ori_res.split("=")[-1].strip())
                    # real_res = float(ori_res.split("=")[-1].strip())
                else:
                    real_res = float(ori_res)
            except:
                # print(f"id: {id}, query: {prompt}")
                # real_res = str(ori_res)
                real_res = -100000
            res[idx] = real_res
        # print(res)
    return res

def parse_json_file_v2(json_file):
    res = dict()
    # data = json.load(open(json_file))
    with open(json_file, 'r') as fr:
        for idx, line in enumerate(fr.readlines()):
            line = json.loads(line)
            id = line["id"]
            data = line["data"][0]
            prompt = data["prompt"]
            response = data["response"][0][0]
            ori_res = response.strip()
            try:
                if ori_res.find("因此") != -1:
                    if ori_res.find("R") == -1:
                        real_res = float(ori_res.split("因此,")[-1].split("=")[-1].strip())
                    else:
                        real_res = str(ori_res.split("因此,")[-1].split("=")[-1].strip())
                elif ori_res.find("R") != -1:
                    real_res = str(ori_res.split("=")[-1].strip())
                elif ori_res.find("=") != -1:
                    real_res = float(ori_res.split("=")[-1].strip())
                    # real_res = float(ori_res.split("=")[-1].strip())
                else:
                    real_res = float(ori_res)
            except:
                # print(f"id: {id}, query: {prompt}")
                real_res = str(ori_res)
            res[idx] = real_res
        # print(res)
    return res

def load_human_res(json_file):
    res = dict()
    prompts = dict()
    with open(json_file, 'r') as fr:
        for idx, line in enumerate(fr.readlines()):
            line = json.loads(line)
            id = line["id"]
            data = line["data"][0]
            prompt = data["prompt"]
            response = data["response"][0][0]
            prompts[idx] = prompt
            if "R" in response:
                # res[idx] = str(response)
                res[idx] = -10000
            else:
                res[idx] = float(response)
    return res, prompts

def load_human_res_v2(json_file):
    res = dict()
    with open(json_file, 'r') as fr:
        for idx, line in enumerate(fr.readlines()):
            line = json.loads(line)
            id = line["id"]
            data = line["data"][0]
            prompt = data["prompt"]
            response = data["response"][0][0]
            if "R" in response:
                res[idx] = str(response)
                # res[idx] = -10000
            else:
                res[idx] = float(response)
    return res

def eval_acc_2d(res1, res2, diff_bar=0.0001):
    assert len(res1) == len(res2)
    nums_all = len(res1)
    count = 0
    for k in res1.keys():
        v1 = res1[k]
        v2 = res2[k]
        if abs(v1 - v2) < diff_bar:
            count += 1
    acc = round(count/nums_all, 3)
    print(acc)
    return 
    
def eval_acc(res1, res2, prompts, diff_bar=0.001):
    count = 0
    right_count = 0

    jiajian_count = 0
    right_jiajian_count = 0

    dashu_count = 0
    right_dashu_count = 0

    fushu_jiajian_count = 0
    right_fushu_jiajian_count = 0

    xiaoshu_jiajian_count = 0
    right_xiaoshu_jiajian_count = 0

    zhengshu_cheng_count = 0
    right_zhengshu_cheng_count = 0

    xiaoshu_cheng_count = 0
    right_xiaoshu_cheng_count = 0

    dashu_cheng_count = 0
    right_dashu_cheng_count = 0

    zhengshu_chu_count = 0
    right_zhengshu_chu_count = 0

    zhengshu_zhishu_count = 0
    right_zhengshu_zhishu_count = 0

    xiaoshu_zhishu_count = 0
    right_xiaoshu_zhishu_count = 0

    fuhao_count = 0
    right_fuhao_count = 0

    fuza_size_count = 0
    right_fuza_size_count = 0

    sanjiao_count = 0
    right_sanjiao_count = 0

    log_count = 0
    right_log_count = 0


    for k in res1.keys():
        idx = k #int(k.split("_")[-1])
        
        if not k in res2.keys():
            print (k)
            continue
        else:
            if idx < 76:
                jiajian_count += 1
            elif idx < 101:
                dashu_count += 1
            elif idx < 126:
                fushu_jiajian_count += 1
            elif idx < 151:
                xiaoshu_jiajian_count += 1
            elif idx < 176:
                zhengshu_cheng_count += 1
            elif idx < 201:
                xiaoshu_cheng_count += 1
            elif idx < 226:
                dashu_cheng_count += 1
            elif idx < 251:
                zhengshu_chu_count += 1
            elif idx < 276:
                zhengshu_zhishu_count += 1
            elif idx < 301:
                xiaoshu_zhishu_count += 1
            elif idx < 326:
                fuhao_count += 1
            elif idx < 351:
                fuza_size_count += 1
            elif idx < 376:
                sanjiao_count += 1
            else:
                log_count += 1

            count += 1
            if abs(res1[k] - res2[k]) < diff_bar:
                right_count += 1
                if idx < 76:
                    right_jiajian_count += 1
                elif idx < 101:
                    right_dashu_count += 1
                elif idx < 126:
                    right_fushu_jiajian_count += 1
                elif idx < 151:
                    right_xiaoshu_jiajian_count += 1
                elif idx < 176:
                    right_zhengshu_cheng_count += 1
                elif idx < 201:
                    right_xiaoshu_cheng_count += 1
                elif idx < 226:
                    right_dashu_cheng_count += 1
                elif idx < 251:
                    right_zhengshu_chu_count += 1
                elif idx < 276:
                    right_zhengshu_zhishu_count += 1
                elif idx < 301:
                    right_xiaoshu_zhishu_count += 1
                elif idx < 326:
                    right_fuhao_count += 1
                elif idx < 351:
                    right_fuza_size_count += 1
                elif idx < 376:
                    right_sanjiao_count += 1
                else:
                    right_log_count += 1
            # else:
            #     print(k, prompts[k], res1[k], res2[k])
                
    print ("count :{}".format(count))
    print ("right count:{}".format(right_count))
    print ("acc :{}".format(float(right_count)/float(count)))
    print ("**********************************")
    print ("加减 count: {}".format(jiajian_count))
    print ("right count: {}".format(right_jiajian_count))
    print ("加减 acc: {}".format(float(right_jiajian_count) / float(jiajian_count)))
    print ("**********************************")
    print ("大数加减 count: {}".format(dashu_count))
    print ("right count: {}".format(right_dashu_count))
    print ("大数加减 acc: {}".format(float(right_dashu_count) / float(dashu_count)))
    print ("**********************************")
    print ("负数加减  count: {}".format(fushu_jiajian_count))
    print ("right count: {}".format(right_fushu_jiajian_count))
    print ("负数加减  acc: {}".format(float(right_fushu_jiajian_count) / float(fushu_jiajian_count)))
    print ("**********************************")
    print ("小数加减  count: {}".format(xiaoshu_jiajian_count))
    print ("right count: {}".format(right_xiaoshu_jiajian_count))
    print ("小数加减  acc: {}".format(float(right_xiaoshu_jiajian_count) / float(xiaoshu_jiajian_count)))
    print ("**********************************")
    print ("整数乘法  count: {}".format(zhengshu_cheng_count))
    print ("right count: {}".format(right_zhengshu_cheng_count))
    print ("整数乘法  acc: {}".format(float(right_zhengshu_cheng_count) / float(zhengshu_cheng_count)))
    print ("**********************************")
    print ("小数乘法  count: {}".format(xiaoshu_cheng_count))
    print ("right count: {}".format(right_xiaoshu_cheng_count))
    print ("小数乘法  acc: {}".format(float(right_xiaoshu_cheng_count) / float(xiaoshu_cheng_count)))
    print ("**********************************")
    print ("大数乘法  count: {}".format(dashu_cheng_count))
    print ("right count: {}".format(right_dashu_cheng_count))
    print ("大数乘法  acc: {}".format(float(right_dashu_cheng_count) / float(dashu_cheng_count)))
    print ("**********************************")
    print ("整数除法  count: {}".format(zhengshu_chu_count))
    print ("right count: {}".format(right_zhengshu_chu_count))
    print ("整数除法  acc: {}".format(float(right_zhengshu_chu_count) / float(zhengshu_chu_count)))
    print ("**********************************")
    print ("整数指数  count: {}".format(zhengshu_zhishu_count))
    print ("right count: {}".format(right_zhengshu_zhishu_count))
    print ("整数指数  acc: {}".format(float(right_zhengshu_zhishu_count) / float(zhengshu_zhishu_count)))
    print ("**********************************")
    print ("小数指数  count: {}".format(xiaoshu_zhishu_count))
    print ("right count: {}".format(right_xiaoshu_zhishu_count))
    print ("小数指数  acc: {}".format(float(right_xiaoshu_zhishu_count) / float(xiaoshu_zhishu_count)))
    print ("**********************************")
    print ("符号运算  count: {}".format(fuhao_count))
    print ("right count: {}".format(right_fuhao_count))
    print ("符号运算  acc: {}".format(float(right_fuhao_count) / float(fuhao_count)))
    print ("**********************************")
    print ("复杂四则运算  count: {}".format(fuza_size_count))
    print ("right count: {}".format(right_fuza_size_count))
    print ("复杂四则运算  acc: {}".format(float(right_fuza_size_count) / float(fuza_size_count)))
    print ("**********************************")
    print ("三角函数运算  count: {}".format(sanjiao_count))
    print ("right count: {}".format(right_sanjiao_count))
    print ("三角函数运算  acc: {}".format(float(right_sanjiao_count) / float(sanjiao_count)))
    print ("**********************************")
    print ("log运算  count: {}".format(log_count))
    print ("right count: {}".format(right_log_count))
    print ("log运算  acc: {}".format(float(right_log_count) / float(log_count)))
    print ("**********************************")

def eval_acc_v2(res1, res2, diff_bar=0.0001):
    count = 0
    right_count = 0

    jiajian_count = 0
    right_jiajian_count = 0

    dashu_count = 0
    right_dashu_count = 0

    fushu_jiajian_count = 0
    right_fushu_jiajian_count = 0

    xiaoshu_jiajian_count = 0
    right_xiaoshu_jiajian_count = 0

    zhengshu_cheng_count = 0
    right_zhengshu_cheng_count = 0

    xiaoshu_cheng_count = 0
    right_xiaoshu_cheng_count = 0

    dashu_cheng_count = 0
    right_dashu_cheng_count = 0

    zhengshu_chu_count = 0
    right_zhengshu_chu_count = 0

    zhengshu_zhishu_count = 0
    right_zhengshu_zhishu_count = 0

    xiaoshu_zhishu_count = 0
    right_xiaoshu_zhishu_count = 0

    fuhao_count = 0
    right_fuhao_count = 0

    fuza_size_count = 0
    right_fuza_size_count = 0

    sanjiao_count = 0
    right_sanjiao_count = 0

    log_count = 0
    right_log_count = 0


    for k in res1.keys():
        idx = k #int(k.split("_")[-1])
        
        if not k in res2.keys():
            print (k)
            continue
        else:
            if idx < 76:
                jiajian_count += 1
            elif idx < 101:
                dashu_count += 1
            elif idx < 126:
                fushu_jiajian_count += 1
            elif idx < 151:
                xiaoshu_jiajian_count += 1
            elif idx < 176:
                zhengshu_cheng_count += 1
            elif idx < 201:
                xiaoshu_cheng_count += 1
            elif idx < 226:
                dashu_cheng_count += 1
            elif idx < 251:
                zhengshu_chu_count += 1
            elif idx < 276:
                zhengshu_zhishu_count += 1
            elif idx < 301:
                xiaoshu_zhishu_count += 1
            elif idx < 326:
                fuhao_count += 1
            elif idx < 351:
                fuza_size_count += 1
            elif idx < 376:
                sanjiao_count += 1
            else:
                log_count += 1

            count += 1
            if type(res1[k]) == float and type(res2[k]) == float:
                if abs(res1[k] - res2[k]) < diff_bar :
                    right_count += 1
                    if idx < 76:
                        right_jiajian_count += 1
                    elif idx < 101:
                        right_dashu_count += 1
                    elif idx < 126:
                        right_fushu_jiajian_count += 1
                    elif idx < 151:
                        right_xiaoshu_jiajian_count += 1
                    elif idx < 176:
                        right_zhengshu_cheng_count += 1
                    elif idx < 201:
                        right_xiaoshu_cheng_count += 1
                    elif idx < 226:
                        right_dashu_cheng_count += 1
                    elif idx < 251:
                        right_zhengshu_chu_count += 1
                    elif idx < 276:
                        right_zhengshu_zhishu_count += 1
                    elif idx < 301:
                        right_xiaoshu_zhishu_count += 1
                    elif idx < 326:
                        right_fuhao_count += 1
                    elif idx < 351:
                        right_fuza_size_count += 1
                    elif idx < 376:
                        right_sanjiao_count += 1
                    else:
                        right_log_count += 1
                # else:
                #     print(k, res1[k], res2[k])
            if type(res1[k]) == str and type(res2[k]) == str:
                if res1[k] == res2[k]:
                    right_count += 1
                    if idx < 76:
                        right_jiajian_count += 1
                    elif idx < 101:
                        right_dashu_count += 1
                    elif idx < 126:
                        right_fushu_jiajian_count += 1
                    elif idx < 151:
                        right_xiaoshu_jiajian_count += 1
                    elif idx < 176:
                        right_zhengshu_cheng_count += 1
                    elif idx < 201:
                        right_xiaoshu_cheng_count += 1
                    elif idx < 226:
                        right_dashu_cheng_count += 1
                    elif idx < 251:
                        right_zhengshu_chu_count += 1
                    elif idx < 276:
                        right_zhengshu_zhishu_count += 1
                    elif idx < 301:
                        right_xiaoshu_zhishu_count += 1
                    elif idx < 326:
                        right_fuhao_count += 1
                    elif idx < 351:
                        right_fuza_size_count += 1
                    elif idx < 376:
                        right_sanjiao_count += 1
                    else:
                        right_log_count += 1
                
    print ("count :{}".format(count))
    print ("right count:{}".format(right_count))
    print ("acc :{}".format(float(right_count)/float(count)))
    print ("**********************************")
    print ("加减 count: {}".format(jiajian_count))
    print ("right count: {}".format(right_jiajian_count))
    print ("加减 acc: {}".format(float(right_jiajian_count) / float(jiajian_count)))
    print ("**********************************")
    print ("大数加减 count: {}".format(dashu_count))
    print ("right count: {}".format(right_dashu_count))
    print ("大数加减 acc: {}".format(float(right_dashu_count) / float(dashu_count)))
    print ("**********************************")
    print ("负数加减  count: {}".format(fushu_jiajian_count))
    print ("right count: {}".format(right_fushu_jiajian_count))
    print ("负数加减  acc: {}".format(float(right_fushu_jiajian_count) / float(fushu_jiajian_count)))
    print ("**********************************")
    print ("小数加减  count: {}".format(xiaoshu_jiajian_count))
    print ("right count: {}".format(right_xiaoshu_jiajian_count))
    print ("小数加减  acc: {}".format(float(right_xiaoshu_jiajian_count) / float(xiaoshu_jiajian_count)))
    print ("**********************************")
    print ("整数乘法  count: {}".format(zhengshu_cheng_count))
    print ("right count: {}".format(right_zhengshu_cheng_count))
    print ("整数乘法  acc: {}".format(float(right_zhengshu_cheng_count) / float(zhengshu_cheng_count)))
    print ("**********************************")
    print ("小数乘法  count: {}".format(xiaoshu_cheng_count))
    print ("right count: {}".format(right_xiaoshu_cheng_count))
    print ("小数乘法  acc: {}".format(float(right_xiaoshu_cheng_count) / float(xiaoshu_cheng_count)))
    print ("**********************************")
    print ("大数乘法  count: {}".format(dashu_cheng_count))
    print ("right count: {}".format(right_dashu_cheng_count))
    print ("大数乘法  acc: {}".format(float(right_dashu_cheng_count) / float(dashu_cheng_count)))
    print ("**********************************")
    print ("整数除法  count: {}".format(zhengshu_chu_count))
    print ("right count: {}".format(right_zhengshu_chu_count))
    print ("整数除法  acc: {}".format(float(right_zhengshu_chu_count) / float(zhengshu_chu_count)))
    print ("**********************************")
    print ("整数指数  count: {}".format(zhengshu_zhishu_count))
    print ("right count: {}".format(right_zhengshu_zhishu_count))
    print ("整数指数  acc: {}".format(float(right_zhengshu_zhishu_count) / float(zhengshu_zhishu_count)))
    print ("**********************************")
    print ("小数指数  count: {}".format(xiaoshu_zhishu_count))
    print ("right count: {}".format(right_xiaoshu_zhishu_count))
    print ("小数指数  acc: {}".format(float(right_xiaoshu_zhishu_count) / float(xiaoshu_zhishu_count)))
    print ("**********************************")
    print ("符号运算  count: {}".format(fuhao_count))
    print ("right count: {}".format(right_fuhao_count))
    print ("符号运算  acc: {}".format(float(right_fuhao_count) / float(fuhao_count)))
    print ("**********************************")
    print ("复杂四则运算  count: {}".format(fuza_size_count))
    print ("right count: {}".format(right_fuza_size_count))
    print ("复杂四则运算  acc: {}".format(float(right_fuza_size_count) / float(fuza_size_count)))
    print ("**********************************")
    print ("三角函数运算  count: {}".format(sanjiao_count))
    print ("right count: {}".format(right_sanjiao_count))
    print ("三角函数运算  acc: {}".format(float(right_sanjiao_count) / float(sanjiao_count)))
    print ("**********************************")
    print ("log运算  count: {}".format(log_count))
    print ("right count: {}".format(right_log_count))
    print ("log运算  acc: {}".format(float(right_log_count) / float(log_count)))
    print ("**********************************")




if __name__ == '__main__':
    # infer_resd = parse_json_file_cgd("/mnt/pfs/cgd/workspace/projects/largescale/exp/chatglm-sft-zero2-tp1-pp1-math-self-v10/output/math401_fix-global_step296.json")
    # human_resd = load_human_res_cgd("/mnt/pfs/cgd/workspace/projects/LargeScale.integrate/data/math401-llm/math401_fix.json")
    # print(len(infer_resd), len(human_resd))
    # eval_acc(infer_resd, human_resd)
    # print (infer_resd)

    parser = argparse.ArgumentParser()
    parser.add_argument("--ref-file", type=str, required=True)
    parser.add_argument("--inf-file", type=str, required=True)
    args = parser.parse_args()

    if "v2" in args.ref_file:
        human_resd = load_human_res_v2(args.ref_file)
        infer_resd = parse_json_file_v2(args.inf_file)
        eval_acc_v2(infer_resd, human_resd)
    else:
        human_resd, prompts = load_human_res(args.ref_file)
        infer_resd = parse_json_file(args.inf_file)
        eval_acc(infer_resd, human_resd, prompts)