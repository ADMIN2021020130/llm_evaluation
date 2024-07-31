import json
import os
import sys
import argparse

def is_right_by_domain(human_resp, infer_resp, domain):
    def get_label_by_resp_bustm(resp):
        if resp.find("不相近") != -1 and resp.find("相近") == -1:
                return 0
        if resp.find("不相近") == -1 and resp.find("相近") != -1:
                return 1
        return -1
    
    def get_label_by_resp_eprstmt(resp):
        if "消极" in resp and (not "积极" in resp):
                return 0
        if "积极" in resp and (not "消极" in resp):
                return 1
        return -1
    assert domain in {"General_fewclue_bustm_test_public", "General_fewclue_eprstmt_test_public"}

    if domain == "General_fewclue_bustm_test_public":
        human_label = get_label_by_resp_bustm(human_resp)
        infer_label = get_label_by_resp_bustm(infer_resp)
        if human_label == infer_label:
            return 1
        else:
            return 0
    
    elif domain == "General_fewclue_eprstmt_test_public":
        human_label = get_label_by_resp_eprstmt(human_resp)
        infer_label = get_label_by_resp_eprstmt(infer_resp)
        if human_label == infer_label:
            return 1
        else:
            return 0

def load_infer_res_largescale(jsonfile):
    lines = open(jsonfile).readlines()
    res = dict()
    for l in lines:
        data = json.loads(l.strip())
        id = data["id"]
        res[id] = data["data"][0]["response"][0][0]
    return res

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

def eval(human_res, infer_res):
    domain_count = {"General_fewclue_eprstmt_test_public": 0, "General_fewclue_bustm_test_public": 0}
    domain_rightcount = {"General_fewclue_eprstmt_test_public": 0, "General_fewclue_bustm_test_public": 0}

    for item in human_res:
        id = item['id']
        if id in infer_res.keys():
            infer_resp = infer_res[id]
        domain = item['data'][0]['domain'][0]
        domain_count[domain] += 1
        human_resp = item['data'][0]['response'][0][0]
        domain_rightcount[domain] += is_right_by_domain(human_resp, infer_resp, domain)
    
    all_count = 0
    all_rightcount = 0
    for k in domain_count.keys():
        count = domain_count[k]
        all_count += count
        right_count = domain_rightcount[k]
        all_rightcount += right_count
        acc = float(right_count) / float(count)
        print ("Doamin : {}  Count: {}  RightCount: {}  ACC: {}".format(k, count, right_count, acc))
    
    print ("FewCLUE Overall********")
    acc = float(all_rightcount) / float(all_count)
    print ("Count: {}  RightCount: {} Acc: {}".format(all_count, all_rightcount, acc))
    print ("***********************")
        


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--ref-file", type=str, required=True)
    parser.add_argument("--inf-file", type=str, required=True)
    human_res = load_human_res_largescale(args.ref_file)
    infer_res = load_infer_res_130b(args.inf_file, key="130b")
    eval(human_res, infer_res)
