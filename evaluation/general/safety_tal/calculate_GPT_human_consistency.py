import json
import sys
import pandas as pd

def load_excel(files):
    df = pd.read_excel(files)
    data = df.values
    res = {}
    for item in data:
        res[item[0]] = [str(int(item[5])), str(int(item[7])), str(int(item[9]))]
        #print(res[item[0]])
    return res

def load_json(jsonfile):
    lines = open(jsonfile).readlines()
    res = {}
    for l in lines:
        data = json.loads(l.strip())
        res[data["id"]] = str(int(data["alignment_annotators"]))
    return res
 
def print_consistency(ref_res, gpt_res):
    AG = 0
    BG = 0
    CG = 0
    AB = 0
    AC = 0
    BC = 0
    count = 0
    for key in ref_res.keys():
        count+=1
        item_ref = ref_res[key]
        item_gpt = gpt_res[key]
        if(item_ref[0]==item_gpt):
            AG+=1
        if(item_ref[1]==item_gpt):
            BG+=1
        if(item_ref[2]==item_gpt):
            CG+=1
        if(item_ref[0]==item_ref[1]):
            AB+=1
        if(item_ref[0]==item_ref[2]):
            AC+=1
        if(item_ref[1]==item_ref[2]):
            BC+=1
    print("AG:", AG/count)
    print("BG:", BG/count)
    print("CG:", CG/count)
    print("AB", AB/count)
    print("AC", AC/count)
    print("BC", BC/count)
    print("ave1:", (AG+BG+CG)/(3*count))
    print("ave2:", (AB+AC+BC)/(3*count))

if __name__ == "__main__":
    ref_res = load_excel("safety_abx_test_195.xlsx")
    gpt_res = load_json(sys.argv[1])
    print_consistency(ref_res, gpt_res)


