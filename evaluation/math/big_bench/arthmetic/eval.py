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
                print(f"id: {id}, query: {prompt}")
                real_res = str(ori_res)
            try:
                res[id]= float(real_res)
            except:
                res[id]= float(real_res.split("R")[0].strip())
        # print(res)
    return res

def load_human_res(json_file):
    res = dict()
    with open(json_file, 'r') as fr:
        for idx, line in enumerate(fr.readlines()):
            line = json.loads(line)
            id = line["id"]
            data = line["data"][0]
            prompt = data["prompt"]
            response = data["response"][0][0]
            if "R" in response:
                res[id] = str(response)
            else:
                res[id] = float(response)
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

def eval_acc(res1, res2, diff_bar=0.0001):
    count = 0
    right_count = 0

    detail_count_dict = dict()
    detail_right_count_dict = dict()

    for k in res1.keys():
        if not k in res2.keys():
            print (k)
            continue
        count += 1
        sub_key = k.split("-")[0]
        if not sub_key in detail_count_dict.keys():
            detail_count_dict[sub_key] = 1
        else:
            detail_count_dict[sub_key] += 1
        if abs(res1[k] - res2[k]) < diff_bar:
            right_count += 1
            if not sub_key in detail_right_count_dict.keys():
                detail_right_count_dict[sub_key] = 1
            else:
                detail_right_count_dict[sub_key] += 1
        
    print ("count :{}".format(count))
    print ("right count:{}".format(right_count))
    print ("acc :{}".format(float(right_count)/float(count)))
    print ("**********************************")

    for k in detail_count_dict.keys():
        print ("Task: {} **************".format(k))
        print ("count :{}".format(detail_count_dict[k]))
        print ("right count:{}".format(detail_right_count_dict[k]))
        print ("acc :{}".format(float(detail_right_count_dict[k])/float(detail_count_dict[k])))
        print ("**********************************")


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--ref-file", type=str, required=True)
    parser.add_argument("--inf-file", type=str, required=True)
    args = parser.parse_args()

    human_resd = load_human_res(args.ref_file)
    infer_resd = parse_json_file(args.inf_file)
    import pdb
    pdb.set_trace()
    eval_acc(infer_resd, human_resd)
