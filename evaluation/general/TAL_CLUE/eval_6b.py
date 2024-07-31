import json
import os
import sys
import difflib
import argparse

def string_similar(s1, s2):
    return difflib.SequenceMatcher(None, s1, s2).quick_ratio()

def is_right_by_domain(human_resp, infer_resp, domain):
    def get_label_by_resp_AFQMC(resp):
        if resp.find("不相近") != -1:
            return 0
        if resp.find("不相近") == -1 and resp.find("相近") != -1:
            return 1
        return -1

    def get_label_by_resp_TNEWS(resp, labels_dict):
        for key in labels_dict.keys():
            if resp.find(key) != -1:
                return labels_dict[key]
        ration = 0
        reslut_key = ""
        for key in labels_dict.keys():
            similar = string_similar(resp, labels_dict[key])
            if similar > ration:
                reslut_key = key
                ration = similar
        if reslut_key != "":
            return labels_dict[reslut_key]
        return -1 

    def get_label_by_resp_CLUEWSC2020(resp):
        if resp.find("正确") != -1 and resp.find("错误") == -1:
            return "true"
        if resp.find("正确") == -1 and resp.find("错误") != -1:
            return "false"
        return -1

    def get_label_by_resp_C3(resp, choice_dict):
        for key in choice_dict.keys():
            if resp.find(key) != -1:
                return choice_dict[key]
        ration = 0
        reslut_key = ""
        for key in choice_dict.keys():
            similar = string_similar(resp, choice_dict[key])
            if similar > ration:
                reslut_key = key
                ration = similar
        if reslut_key != "":
            return choice_dict[reslut_key]
        return -1

    def get_label_by_resp_IFLYTEK(resp, labels):
        if(resp.find("“工具”") != -1):
            return "工具"
        for label in labels:
            if resp.find(label) != -1:
                return label
        ration = 0
        reslut_label = ""
        for label in labels:
            similar = string_similar(resp, label)
            if similar > ration:
                reslut_label = label
                ration = similar
        if reslut_label != "":
            return reslut_label
        return -1

    def get_label_by_resp_OCNLI(resp):
        if resp.find("蕴涵") != -1 and resp.find("无关") == -1 and resp.find("矛盾") == -1:
            return "entailment"
        if resp.find("蕴涵") == -1 and resp.find("无关") != -1 and resp.find("矛盾") == -1:
            return "neutral"
        if resp.find("蕴涵") == -1 and resp.find("无关") == -1 and resp.find("矛盾") != -1:
            return "contradiction"
        return -1

    def get_label_by_resp_CSL(resp):
        if resp.find("正确") != -1 and resp.find("错误") == -1:
            return 0
        if resp.find("正确") == -1 and resp.find("错误") != -1:
            return 1
        return -1

    def get_label_by_resp_CMRC2018(resp, answers):
        answers = eval(answers)
        for i in answers:
            text = i["text"]
            if resp.find(text) != -1: #or text.find(response) != -1:
                return text
        return -1

    def get_label_by_resp_CHID(response, candidates, num):
        if response.find("答") != -1:
            response = response[response.find("答"):]
        if num <=1:
            for i in candidates:
                if response.find(i) != -1:
                    return [i]
            return ["-1"]
        lists = []
        for i in range(num):
            mark = 100000
            res = "-1"
            for j in candidates:
                if response.find(j) != -1:
                    if(response.find(j) < mark):
                        res = j
                        mark = response.find(j)
            lists.append(res)
            if(res[-1]!="-1"):
                response = response[response.find(res[-1]):]
        return lists

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
    
    assert domain in {"AFQMC", "TNEWS", "CLUEWSC2020", "C3", "IFLYTEK", "OCNLI", "CSL", "CMRC2018", "CHID", "General_fewclue_eprstmt_test_public", "General_fewclue_bustm_test_public"}
    
    if domain == "AFQMC": 
        predict = get_label_by_resp_AFQMC(infer_resp)
        label = human_resp["data"][0]["response"][0][0]
        if(predict == int(label)):
            return 1
        else: 
            return 0

    if domain == "TNEWS":
        labels_dict = {"故事":"news_story", "文化":"news_culture", "娱乐":"news_entertainment", "体育":"news_sports", "财经":"news_finance", "房屋":"news_house", "汽车":"news_car", "教育":"news_edu", "科技":"news_tech", "军事":"news_military", "旅游":"news_travel", "世界":"news_world", "股票":"news_stock", "农业":"news_agriculture", "游戏":"news_game"}
        predict = get_label_by_resp_TNEWS(infer_resp, labels_dict)
        label = human_resp["data"][0]["response"][0][0]
        if(predict == label):
            return 1
        else:
            return 0

    if domain == "CLUEWSC2020":
        predict = get_label_by_resp_CLUEWSC2020(infer_resp)
        label = human_resp["data"][0]["response"][0][0]
        if(predict == label):
            return 1
        else:
            return 0

    if domain == "C3":
        choice_dict = human_resp["data"][0]["choice_dict"]
        predict = get_label_by_resp_C3(infer_resp, choice_dict)
        label = human_resp["data"][0]["response"][0][0] 
        if(predict == label):
            return 1
        else:
            return 0
    if domain == "IFLYTEK":
        labels = human_resp["data"][0]["labels"]
        predict = get_label_by_resp_IFLYTEK(infer_resp, labels)
        label_des = human_resp["data"][0]["response"][0][0]
        if(predict == label_des):
            return 1
        else:
            return 0
    if domain == "OCNLI":
        predict = get_label_by_resp_OCNLI(infer_resp)
        label = human_resp["data"][0]["response"][0][0]
        if(predict == label):
            return 1
        else:
            return 0

    if domain == "CSL":
        predict = get_label_by_resp_CSL(infer_resp)
        #print("predict:", predict)
        label = human_resp["data"][0]["response"][0][0]
        #print("label:", label)
        if(predict == int(label)):
            return 1
        else:
            return 0

    if domain == "CMRC2018":
        answers = human_resp["data"][0]["response"][0][0]
        predict = get_label_by_resp_CMRC2018(infer_resp, answers)
        if predict != -1:
            return 1
        else:
            return 0

    if domain == "CHID":
        candidates = human_resp["data"][0]["candidates"]
        num = human_resp["data"][0]["num"]
        predict = get_label_by_resp_CHID(infer_resp, candidates, num)
        labels =  eval(human_resp["data"][0]["response"][0][0])
        items = []
        for i in labels.keys():
            items.append(i) 
        right = 0
        for k in range(len(items)):
            if (candidates[labels[items[k]]]==predict[k]):
                right += 1
        return right

    if domain == "General_fewclue_bustm_test_public":
        human_resp = human_resp["data"][0]["response"][0][0] 
        human_label = get_label_by_resp_bustm(human_resp)
        infer_label = get_label_by_resp_bustm(infer_resp)
        if human_label == infer_label:
            return 1
        else:
            return 0

    elif domain == "General_fewclue_eprstmt_test_public":
        human_resp = human_resp["data"][0]["response"][0][0]
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

def load_human_res(jsonfile):
    lines = open(jsonfile).readlines()
    res = []
    for l in lines:
        data = json.loads(l.strip())
        res.append(data)
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

def evals(infer_res, human_res):
    domain_count = {"AFQMC": 0, "TNEWS": 0, "CLUEWSC2020": 0, "C3": 0, "IFLYTEK": 0, "OCNLI": 0, "CSL": 0, "CMRC2018": 0, "CHID": 0, "General_fewclue_eprstmt_test_public": 0, "General_fewclue_bustm_test_public": 0}
    domain_rightcount = {"AFQMC": 0, "TNEWS": 0, "CLUEWSC2020": 0, "C3": 0, "IFLYTEK": 0, "OCNLI": 0, "CSL": 0 , "CMRC2018": 0, "CHID": 0, "General_fewclue_eprstmt_test_public": 0, "General_fewclue_bustm_test_public": 0}

    for item in human_res:
        id = item['id']
        if id in infer_res.keys():
            infer_resp = infer_res[id]
        else:
            infer_resp = ""
        domain = item['domain'][-1]
        if domain == "CHID":
            human_resp = item
            domain_count[domain] += human_resp["data"][0]["num"]
            domain_rightcount[domain] += is_right_by_domain(human_resp, infer_resp, domain)
        else:
            domain_count[domain] += 1
            human_resp = item
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

    print ("TAL_CLUE Overall********")
    print ("Count: {}  RightCount: {} Acc: {}".format(all_count, all_rightcount, all_rightcount/all_count))
    print ("***********************")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--ref-file", type=str, required=True)
    parser.add_argument("--inf-file", type=str, required=True)
    args = parser.parse_args()
    human_res = load_human_res_largescale(args.ref_file)
    infer_res = load_infer_res_largescale(args.inf_file)
    evals(infer_res, human_res)

