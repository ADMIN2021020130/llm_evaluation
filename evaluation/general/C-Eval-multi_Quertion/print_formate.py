import json

def load_json(jsonfile):
    lines = open(jsonfile).readlines()
    res = []
    for l in lines:
        data = json.loads(l.strip())
        res.append(data)
    return res

if __name__ == "__main__":
    data = load_json("ceval_all_no_shot_v3_middle_school_mathematics.json")
    for item in data:
        print("###############prompt#################")
        print(item["prompt"])
        print("##############response################")
        print(item["response"], "\n\n\n")
