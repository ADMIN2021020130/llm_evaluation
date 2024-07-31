import sys
import json
import random
import uuid

def load_json(jsonfile):
    lines = open(jsonfile).readlines()
    res = []
    for l in lines:
        data = json.loads(l.strip())
        res.append(data)
    return res

def generate_multi_question(data, rounds, output_files):
    random.shuffle(data)
    prefix1 = ["第一题:", "第二题:", "第三题:", "第四题:", "第五题:"]
    prefix2 = ["[1]", "[2]", "[3]", "[4]", "[5]"]
    prefix3 = ["(1)", "(2)", "(3)", "(4)", "(5)"]
    prefix4 = ["1.", "2.", "3.", "4.", "5."]
    prefix = [prefix1, prefix2, prefix3, prefix4]
    res = [] 
    #分组
    group_data = [data[i:i+rounds] for i in range(0,len(data),rounds)]
    for item_data in group_data:
        dicts = {}
        prefix_ = random.choice(prefix)
        mq = ""
        count = 0
        response = []
        ori_id = []
        single_id = []
        for item in item_data:
            prompt = item["prompt"]
            response.append(item["response"])
            ori_id.append(item["ori_id"])
            single_id.append(item["id"])
            domain = item["domain"] 
            tag = item["tag"]
            choice = {}
            mq = mq + prefix_[count] + prompt + "\n"
            count += 1
        unique_id = str(uuid.uuid4())
        domain.append("Multiple_questions")
        domain.append("MQ_"+str(rounds))
        tag = tag + "-Multiple_questions"
        dicts = {"id":unique_id, "single_id":single_id, "ori_id":ori_id, "prompt":mq, "response":response, "domain":domain, "tag":tag, "choice":choice}
        res.append(dicts)
        print("############################")
        print(mq)
    fw = open(output_files, "w")
    for item in res:
        json.dump(item, fw,ensure_ascii=False)
        fw.write("\n")
if __name__ == "__main__":
   data = load_json("ceval_all_no_shot_v3_middle_school_mathematics.json")
   rounds = int(sys.argv[1])
   output_files = "ceval_all_no_shot_v3_middle_school_mathematics_MQ" + str(rounds) + ".json"
   generate_multi_question(data, rounds, output_files)
