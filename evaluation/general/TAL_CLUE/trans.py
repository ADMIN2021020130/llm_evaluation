import json
import sys

def get_data_format(id="", prompt="", input="", response="", from_type="", domain=""):
    if type(domain) != list:
        domain = [domain]
    data_format = {
        "id": id,
        "data":[{
            "prompt": str(prompt),
            "input": str(input),
            "response": [[str(response), str(from_type)]],
        }],
        "domain": domain,
    }
    if data_format["id"] == "":
        data_format["id"] = shortuuid.uuid(name=str(data_format["data"]))
    return data_format

"""
fr = open("fewclue_bustm.json", "r")
fw = open("fewclue_bustm_s.json", "w")
data = []
for i in fr.readlines():
    item = eval(i)
    id = item["id"]
    prompt = item["data"][0]["prompt"]
    input = item["data"][0]["input"]
    response = item["data"][0]["response"][0][0]
    from_type = item["data"][0]["response"][0][1]
    domain = item["data"][0]["domain"]
    data_format = get_data_format(id=id, prompt=prompt, input=input, response=response, from_type=from_type, domain=domain)
    data.append(data_format)

for line in data:
    fw.write(json.dumps(line, ensure_ascii=False) + "\n")

"""
fr = open("tal_clue_fewclue_all.json", "r")
fw = open("tal_clue_fewclue_all_eval.json", "w")
data = []
for i in fr.readlines():
    item = eval(i)
    json_data = {}
    id = item["id"]
    prompt = item["data"][0]["prompt"]
    response = item["data"][0]["response"][0][0]
    domain = item["domain"]
    tag = "Sft-Clue-Fewclue"
    choice = {}
    json_data["id"] = id
    json_data["prompt"] = prompt
    json_data["response"] = response
    json_data["domain"] = domain
    json_data["tag"] = tag
    json_data["choice"] = choice
    json_data["data"] = item["data"]
    data.append(json_data)

for line in data:
    fw.write(json.dumps(line, ensure_ascii=False) + "\n")