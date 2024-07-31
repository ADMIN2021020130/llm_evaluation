import os
import re
import tqdm
import json
import argparse


def load_json(json_file):
    data = []
    with open(json_file, 'r') as jf:
        for line in jf.readlines():
            data.append(json.loads(line))
    return data


def load_jsons(json_files):
    data = []
    for json_file in json_files:
        data.extend(load_json(json_file))
    return data


def find_ans(s):
    return s.split('\n')[-1].replace('答案：', '')


def find_equ(s):
    s = s.split('\n')[0]
    s = s.replace('解：x=','')
    s = s.replace('解：','')
    return s


def remove_percent_int(s):
    '''
    75% -> 0.75
    '''
    if '%' in s:
        pattern = r'\d+%'
        # pattern = r'\d*\.\d+%'
        f1 = re.findall(pattern, s)
        for f in f1:
            num = str(float(f.split('%')[0]) / 100)
            s = s.replace(f, num)
    return s


def remove_percent_float(s):
    '''
    73.25% -> 0.7325
    '''
    if '%' in s:
        # pattern = r'\d+%'
        pattern = r'\d*\.\d+%'
        f1 = re.findall(pattern, s)
        for f in f1:
            num = str(float(f.split('%')[0]) / 100)
            s = s.replace(f, num)
    return s


def remove_mixed_num(s):
    '''
    5(1/2) -> 5.5
    '''
    pattern = r'\d+\(\d+/\d+\)'
    f1 = re.findall(pattern, s)
    for f in f1:
        pattern = r'\b\d+\b'
        nums = re.findall(pattern, f)
        nums = [int(x) for x in nums]
        res = nums[0] + nums[1] / nums[2]
        s = s.replace(f, str(res))
    return s


def remove():
    '''
    TODO:
    (80+20)% -> 100%
    (20%-(560-500*(1+10%))% ->
    '''
    pass


def cal_equ(s):
    s = find_equ(s)
    s = remove_percent_float(s)
    s = remove_percent_int(s)
    s = remove_mixed_num(s)

    try:
        res = eval(s)
    except Exception as e:
        # print('=====in cal equ=====')
        # print(e)

        res = s

    return res


def cal_ans(s):
    s = find_ans(s)
    s = remove_percent_float(s)
    s = remove_percent_int(s)
    s = remove_mixed_num(s)

    try:
        res = eval(s)
    except Exception as e:
        # print('=====in cal ans=====')
        # print(e)

        res = s

    return res


def round_f(s):
    try:
        res = round(float(s), 4)
        # print(res)
    except Exception as e:
        # print('=====in round f=====')
        # print(e)
        res = s
    return res


def is_equal(a, b):
    is_equ = False
    try:
        if abs(float(a) - float(b)) <= 1e-4:
            is_equ = True
    except:
        pass

    return is_equ


def match_num(s):
    pattern = r"-?\d+(?:\.\d+)?"
    f1 = re.findall(pattern, s)
    return f1


def match_frac(s):
    pattern = r"frac{(\d+)}{(\d+)}"
    f1 = re.findall(pattern, s)
    return f1


def cal_frac(s):
    res = None
    if match_frac(s):
        f1 = match_frac(s)[0]
        res = float(f1[0]) / int(f1[1])

    return res


def find_last_eq(s):
    pattern = r".*=(.*)"
    match = re.search(pattern, s)
    if match:
        return match.group(1)
    else:
        return None


def simple_s(s):
    s = remove_percent_float(s)
    s = remove_percent_int(s)
    s = remove_mixed_num(s)
    return s


def match_patterns(s, ps):
    for p in ps:
        match = re.search(p, s)
        if match:
            return match
    return None


def parse(pred, gt):
    '''
    按照模板匹配
    '''

    is_correct = False
    is_miss = True
    
    patterns = [r"答案\s*(.*)", r"答\s*(.*)", r"因此\s*(.*)"]

    answer = None
    match = match_patterns(pred, patterns)
    if match:
        answer = match.group(1)
    else:
        answer = find_last_eq(pred)
        # pass

    if answer:
        is_miss = False
        answer = simple_s(answer)
        if match_frac(answer):
            pred_ans = cal_frac(answer)
            if is_equal(pred_ans, cal_equ(gt)):
                is_correct = True
        
        elif match_num(answer):
            for pred_ans in match_num(answer):
                # pred_ans = float(match_num(answer)[0])
                if is_equal(pred_ans, cal_equ(gt)):
                    is_correct = True
                    break

    return is_correct, is_miss


def evaluation(data, inf_key=''):
    total_cnt = 0
    correct_cnt = 0

    miss_cnt = 0
    for d in tqdm.tqdm(data):
        # ape210k中部分'/'会被打成':'
        if 'response' in d.keys() and inf_key in d.keys():
            gt = d['response'].split('\n')[1].replace('答案：', '')
            pred = d[inf_key].replace('\n', '')
        elif 'ans' in d.keys() and 'data' in d.keys():
            gt = d['ans']
            pred = d['data'][0]['response'][0][0].replace('\n', '')
        else:
            raise KeyError

        is_correct, is_miss = parse(pred, gt)

        if is_correct:
            correct_cnt += 1
        total_cnt += 1
        if is_miss:
            miss_cnt += 1

    print('='*20)
    print('miss_cnt: {}'.format(miss_cnt))
    print('correct_cnt: {}'.format(correct_cnt))
    print('total_cnt: {}'.format(total_cnt))
    print('acc: {}'.format(correct_cnt/total_cnt))


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--inf-file", type=str, required=True)
    parser.add_argument("--inf-key", type=str, default="6b", required=False)
    args = parser.parse_args()

    # Usage: python eval_jiaoyan.py --inf-file Ape210K.jsonl --inf-key 130b

    data = load_json(args.inf_file)
    print(len(data))
    evaluation(data, args.inf_key)

