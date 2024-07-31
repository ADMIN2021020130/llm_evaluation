import json
import sys
import os

def load_finetune_res(jsonfile):
    res = dict()
    lines = open(jsonfile, 'r').readlines()
    for l in lines:
        data = json.loads(l.strip())
        id = data['id']
        resp = data['data'][0]['response'][0][0]
        ans = resp.split("\n")[-1].strip().replace("答案：", "")
        res[id] = ans
    return res

def eval(human_res, infer_res):
    count = 0
    right_count = 0
    for id in human_res.keys():
        if human_res[id] == infer_res[id]:
            right_count += 1
        # else:
        #     print (human_res[id])
        #     print (infer_res[id])
        count += 1
    print ("count: {}".format(count))
    print ("right_count: {}".format(right_count))
    print ("acc: {}".format(float(right_count)/float(count)))

if __name__ == '__main__':
    infer_res = load_finetune_res("output/from_ori6b_ape_largescale.json")
    # infer_res = load_finetune_res("output/from_sftv0.1_ape_largescale.json")
    human_res = load_finetune_res("/mnt/pfs/jinfeng_team/SFT/gaoshaojun/data/ape_280k/valid_ape_largescale.json")
    eval(human_res, infer_res)