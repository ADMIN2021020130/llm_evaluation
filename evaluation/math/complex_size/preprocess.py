import os
import json

input_file = r"./test_ape_cot_from_train.json"
output_file = r"./test_ape_cot_from_train_fix.json"

with open(input_file, 'r') as fr, open(output_file, 'w') as fw:
    for idx, line in enumerate(fr.readlines()):
        line = json.loads(line.strip())
        id = line['id']
        ans = line['ans']
        prompt = line['data'][0]['prompt']
        domain = ["math401_plus", "ape_cot", "混合四则"]
        tag = "math401_plus"
        choice = ""
        try:
            
            if "%" in ans:
                response = float(ans.replace("%", ""))/100
            elif "(" in ans:
                n = ans.split("(")[0]
                s = ["(" + ss for ss in ans.split("(")[1:]]
                ss = "".join(s)
                sss = f"{n} + {ss}"
                response = round(eval(sss), 4)
                # print(ans, response)
            else:
                response = eval(ans)
        except:
            print(idx, prompt, ans)

        data = {
            "id": id,
            "prompt": prompt,
            "response": str(response),
            "domain": domain,
            "tag": tag,
            "choice": choice
        }

        fw.write(json.dumps(data, ensure_ascii=False)+"\n")
