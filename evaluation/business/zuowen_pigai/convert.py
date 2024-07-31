import json
import sys
import os

def convert_ori_to_130b(input_file, output_file):
    with open(output_file, "w", encoding="utf-8") as fw:
        item_list = json.load(open(input_file))
        for item in item_list:
            fw.write(json.dumps(item, ensure_ascii=False) + "\n")

if __name__ == '__main__':
    convert_ori_to_130b("zuowen.json", "zuowen_1_130b.json")
    convert_ori_to_130b("zuowen2.json", "zuowen_2_130b.json")
    convert_ori_to_130b("zuowen3.json", "zuowen_3_130b.json")