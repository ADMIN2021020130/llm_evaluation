import json
import os

def convert_to_largescale(dir_name):
    f = open(os.path.join("ori_data", dir_name, "task.json"), 'r')
    items = json.load(f)
    res = list()
    for idx, item in enumerate(items):
        tmp_data = dict()
        tmp_data['id'] = "{}-{}".format(dir_name, idx)
        tmp_data['data'] = list()
        tmp_data['data'].append({"input": "", "prompt": item["data"][0]["input"], "response": [[item["data"][0]["answer"], "big_bench"]]})
        res.append(tmp_data)
    return res

if __name__ == '__main__':
    num_list = [1, 2, 3, 4, 5]
    yunsuan_list = ["division", "multiplication", "subtraction", "addition"]
    qa_list = list()
    for num in num_list:
        for yunsuan in yunsuan_list:
            tmp_qa_list = convert_to_largescale("{}_digit_{}".format(num, yunsuan))
            qa_list += tmp_qa_list
    
    with open("big_bench_arthmetic.jsonl", "w", encoding="utf-8") as fw:
        for qa in qa_list:
            fw.write(json.dumps(qa, ensure_ascii=False) + "\n")