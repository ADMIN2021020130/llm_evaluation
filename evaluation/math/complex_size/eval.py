import sys
import os
import json
import argparse

def parse_json_file(json_file, inf_key):
    res = dict()
    prompts = dict()
    with open(json_file, 'r') as fr:
        for idx, line in enumerate(fr.readlines()):
            line = json.loads(line.strip())
            id = line["id"]
            if id != "":
                idx = id
            prompt = line["prompt"]
            ref_resp = float(line["response"])
            inf_resp = line[inf_key]
            ori_res = inf_resp.strip()
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
                print(f"id: {id}, query: {prompt}")
                # real_res = str(ori_res)
                real_res = -100000
            res[idx] = [ref_resp, real_res]
            prompts[idx] = prompt
    return res, prompts
    
def eval_acc(res, prompts, diff_bar=0.001):
    count = 0
    right_count = 0

    for k in res.keys():
        count += 1
        ref_resp, inf_resp = res[k]
        prompt = prompts[k]
        if abs(ref_resp - inf_resp) < diff_bar:
            right_count += 1
        else:
            print(k, prompt, ref_resp, inf_resp)
                
    print ("count :{}".format(count))
    print ("right count:{}".format(right_count))
    print ("acc :{}".format(float(right_count)/float(count)))



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--inf-file", type=str, required=True)
    parser.add_argument("--inf-key", type=str, default="6b", required=False)
    args = parser.parse_args()

    infer_res, prompts = parse_json_file(args.inf_file, args.inf_key)
    eval_acc(infer_res, prompts)