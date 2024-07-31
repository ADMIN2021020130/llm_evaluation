import argparse
import os
import sys
import pdb
import re
import json

import numpy as np
import pandas as pd

def compute_wer(hyp, ref, cer=False):
    # NOTE: if cannot decode, use <dummy> symbol (never match with ref)
    if len(hyp) == 0:
        hyp = ["<dummy>"]

    if cer:
        hyp = list("".join(hyp))
        ref = list("".join(ref))

    # edit distance
    d = np.zeros((len(ref) + 1) * (len(hyp) + 1), dtype=np.uint16)
    d = d.reshape((len(ref) + 1, len(hyp) + 1))
    for i in range(len(ref) + 1):
        for j in range(len(hyp) + 1):
            if i == 0:
                d[0][j] = j
            elif j == 0:
                d[i][0] = i

    for i in range(1, len(ref) + 1):
        for j in range(1, len(hyp) + 1):
            if ref[i - 1] == hyp[j - 1]:
                d[i][j] = d[i - 1][j - 1]
            else:
                sub_tmp = d[i - 1][j - 1] + 1
                ins_tmp = d[i][j - 1] + 1
                del_tmp = d[i - 1][j] + 1
                d[i][j] = min(sub_tmp, ins_tmp, del_tmp)
    dist = d[len(ref)][len(hyp)]

    # backtrack
    x = len(ref)
    y = len(hyp)
    error_list = []
    while True:
        if x == 0 and y == 0:
            break
        else:
            if x > 0 and y > 0:
                if d[x][y] == d[x - 1][y - 1] and ref[x - 1] == hyp[y - 1]:
                    error_list.append("C")
                    x = x - 1
                    y = y - 1
                elif d[x][y] == d[x][y - 1] + 1:
                    error_list.append("I")
                    y = y - 1
                elif d[x][y] == d[x - 1][y - 1] + 1:
                    error_list.append("S")
                    x = x - 1
                    y = y - 1
                else:
                    error_list.append("D")
                    x = x - 1
            elif x == 0 and y > 0:
                if d[x][y] == d[x][y - 1] + 1:
                    error_list.append("I")
                    y = y - 1
                else:
                    error_list.append("D")
                    x = x - 1
            elif y == 0 and x > 0:
                error_list.append("D")
                x = x - 1
            else:
                raise ValueError
    error_list.reverse()

    n_sub = error_list.count("S")
    n_ins = error_list.count("I")
    n_del = error_list.count("D")
    n_cor = error_list.count("C")

    assert dist == (n_sub + n_ins + n_del)
    assert n_cor == (len(ref) - n_sub - n_del)

    wer = (dist / len(ref)) * 100
    wer_dict = {
        "wer": wer,
        "n_sub": n_sub,
        "n_ins": n_ins,
        "n_del": n_del,
        "n_ref": len(ref),
        "error_list": error_list,
    }

    return wer, wer_dict

def compute_wers_df(dfhyp, dfref=None, cer=True):
    n_sub_total, n_ins_total, n_del_total, n_ref_total = 0, 0, 0, 0
    #pdb.set_trace()
    for row in dfhyp:
        hyp=row['gen_answer'].replace(' ','')
        ref=row['ori_answer'].replace(' ','')
        #pdb.set_trace()
        #print(' '.join(hyp)+'\n'+' '.join(ref)+'\n')
        if type(hyp)=='list':
            pdb.set_trace()
        

        _, wer_dict = compute_wer(hyp, ref, cer=False)

        n_sub_total += wer_dict["n_sub"]
        n_ins_total += wer_dict["n_ins"]
        n_del_total += wer_dict["n_del"]
        n_ref_total += wer_dict["n_ref"]

    wer = ((n_sub_total + n_ins_total + n_del_total) / n_ref_total) * 100
    wer_dict = {
        "wer": wer,
        "n_sub": n_sub_total,
        "n_ins": n_ins_total,
        "n_del": n_del_total,
        "n_ref": n_ref_total,
    }

    return wer, wer_dict


if __name__ == "__main__":
    text=open('/home/zhangfengrun/LLM_task/pinyinzhuanhanzi_ft.json','r',encoding='utf-8')
    json_data = json.loads(text.read())
    #file=pd.read_csv('/home/lichengfei/whisper_data/%s_librispeech_test_other.csv'%m,sep='\t',encoding='utf-8', names=["id", "text","reftext"])
    wer, wer_dict = compute_wers_df(json_data)
    print(wer)
    print(wer_dict)
    #pdb.set_trace()
    


