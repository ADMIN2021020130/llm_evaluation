import json
import sys
import argparse
import multiprocessing
import torch
import numpy as np
from scipy.stats import mode
import re
try:
    import nltk
    nltk_available = True
except ImportError:
    nltk_available = False
from SwissArmyTransformer import get_args, get_tokenizer
from megatron.tokenizer import build_tokenizer
from megatron.data import indexed_dataset
import random 
import os
from tqdm import tqdm

"""
多轮对话处理策略：
1. 当一个session的token数超过最大限制，从头部丢弃整轮对话，直到长度满足条件。
"""

def get_args():
    parser = argparse.ArgumentParser()
    group = parser.add_argument_group(title='input data')
    group.add_argument('--input', type=str, required=True,
                       help='Path  to input JSON')
    group.add_argument('--num_samples', type=int, default=-1, 
                       help='Numbers of samples you want to process')   
    group.add_argument('--split_ratio', type=float, required=True,
                       help='The ratio you want to processed, rest of the data will not be saved into binary file')
    group.add_argument('--datasets', nargs='+', default=None,
                       help='Paths to one or more input datasets to merge')
    group.add_argument('--json-key', default='text',
                       help='space separate listed of keys to extract from json')
    group.add_argument('--split-sentences', action='store_true',
                       help='Split documents into sentences.')
    group.add_argument('--keep-newlines', action='store_true',
                       help='Keep newlines between sentences when splitting.')

    group = parser.add_argument_group(title='tokenizer')
    group.add_argument('--tokenizer-type', type=str, required=False,
                       choices=['BertWordPieceLowerCase','BertWordPieceCase',
                                'GPT2BPETokenizer', 'PretrainedFromHF', 'IceTokenizer', 'icetk-glm-130B'],
                       help='What type of tokenizer to use.')
    group.add_argument('--vocab-file', type=str, default=None,
                       help='Path to the vocab file')
    group.add_argument('--merge-file', type=str, default=None,
                       help='Path to the BPE merge file (if necessary).')
    group.add_argument('--append-eod', action='store_true',
                       help='Append an <eod> token to the end of a document.')
    group.add_argument("--tokenizer-name-or-path", type=str, default=None,
                       help="Name or path of the huggingface tokenizer.")
    group.add_argument('--make-vocab-size-divisible-by', type=int, default=128,
                       help='Pad the vocab size to be divisible by this value.'
                            'This is added for computational efficieny reasons.')
    group.add_argument('--pad-vocab-size-to', type=int, default=None,
                       help='Pad the vocab size to be divisible by this value.'
                            'Value of the size of the vocabulary of the tokenizer to reach. This value must be greater than'
                            ' the initial size of the tokenizer. If this argument is used the value of '
                            '`make-vocab-size-divisible-by` will be ignored.')

    group = parser.add_argument_group(title='output data')
    group.add_argument('--output-prefix', type=str, required=True,
                       help='Path to binary output file without suffix')
    group.add_argument('--dataset-impl', type=str, default='mmap',
                       choices=['lazy', 'cached', 'mmap'])

    group = parser.add_argument_group(title='runtime')
    group.add_argument('--workers', type=int, default=1,
                       help='Number of worker processes to launch')
    group.add_argument('--log-interval', type=int, default=100,
                       help='Interval between progress updates')
    args = parser.parse_args()
    args.keep_empty = False

    return args

def _detokenize_text_to_idx(tokenizer, input, spec_dd):
    text = ""
    for id in input:
        try:
            ch = tokenizer.IdToToken(id)
        except:
            ch = spec_dd[id]
        # if ch != "[pad]":
        text += ch
    return text

def detokenize_text_to_idx(tokenizer, inputs):
    spec = ['[MASK]', '[gMASK]', '[sMASK]', 'eod', 'sop', 'eop', 'ENC', 'dBLOCK', '[pad]']
    spec_d = {}
    spec_dd = {}
    for i in spec:
        spec_d[i] = tokenizer.TokenToId(i)
        spec_dd[tokenizer.TokenToId(i)] = i

    
    text = _detokenize_text_to_idx(tokenizer, inputs, spec_dd)
    # text = tokenizer.detokenize(inputs)
    print(text)

def split_dataset(all_samples_tok, all_samples_txt, ratio):
    train_dataset_tok, train_dataset_txt, test_dataset_tok, test_dataset_txt = [], [], [], []
    for i in range(len(all_samples_tok)):
        dataset_len = len(all_samples_tok[i])
        train_len = int(dataset_len * ratio)
        train_dataset_tok += all_samples_tok[i][:train_len]
        # train_dataset_txt += all_samples_txt[i][:train_len]
        test_dataset_tok += all_samples_tok[i][train_len:]
        # test_dataset_txt += all_samples_txt[i][train_len:]
    

    return train_dataset_tok, train_dataset_txt, test_dataset_tok, test_dataset_txt

def save_data_into_bin(args, level, tkn_padded_samples):
    if args.split_sentences:
        level = "sentence"
    key = args.json_key
    output_bin_files = {}
    output_idx_files = {}
    builders = {}
    output_bin_files[key] = "{}_{}_{}.bin".format(args.output_prefix, key, level)
    output_idx_files[key] = "{}_{}_{}.idx".format(args.output_prefix, key, level)
    builders[key] = indexed_dataset.make_builder(output_bin_files[key], impl=args.dataset_impl, dtype=indexed_dataset.best_fitting_dtype(tokenizer.vocab_size))

    print("Got {} samples, and processed into padded_tkn".format(len(tkn_padded_samples)))
    for idx, item in enumerate(tkn_padded_samples):
        builders[key].add_item(torch.IntTensor(item))

    builders[key].end_document()

    builders[key].finalize(output_idx_files[key])

def save_data_into_bin_noprefix(args, output_prefix, level, tkn_padded_samples):
    if args.split_sentences:
        level = "sentence"
    key = args.json_key
    output_bin_files = {}
    output_idx_files = {}
    builders = {}
    output_bin_files[key] = "{}.bin".format(output_prefix)
    output_idx_files[key] = "{}.idx".format(output_prefix)
    builders[key] = indexed_dataset.make_builder(output_bin_files[key], impl=args.dataset_impl, dtype=indexed_dataset.best_fitting_dtype(tokenizer.vocab_size))

    print("Got {} samples, and processed into padded_tkn".format(len(tkn_padded_samples)))
    for idx, item in enumerate(tkn_padded_samples):
        builders[key].add_item(torch.IntTensor(item))

    builders[key].end_document()

    builders[key].finalize(output_idx_files[key])

def tokenize_sample(tokenizer, max_seq_len, json_path_list):
    all_samples_tok = [] # [[all samples of dataset1],[all samples of dataset2],...]
    all_sample_txt = [] # [[all samples of dataset1],[all samples of dataset2],...]
    for json_path in json_path_list:
        print("Processing ", json_path)
        all_samples_tok_per_dataset, all_sample_txt_per_dataset = [], []
        file = open(json_path, "r")
        lines = file.readlines()
        lens = 0
        if args.num_samples == -1:
            lens = len(lines)
        else:
            lens = args.num_samples
        for i in tqdm(range(lens)):
            row_json_data = json.loads(lines[i])
            chatdata = row_json_data['data']
            chat_rounds = len(chatdata)
            # task_domain = ""
            # if row_json_data['domain'] != []:
            #     task_domain = row_json_data['domain'][0]
            txt_history = []
            tok_history = []
            # system_overview = "###System Overview:\n" + \
            #                 "[中文版]：我的名字是TALGPT，是由好未来（TAL）的AI团队所开发的大语言模型。我的目标是给用户提供有用、真实、准确、符合道德规范的回答和建议，我会尽最大的努力为用户服务。\n" + \
            #                 "[English Version]: My name is TALGPT, a large language model developed by the AI team at TAL Education Group. My goal is to provide users with useful, truthful, accurate, and ethical responses and advice, and I will make every effort to serve our users to the best of my abilities.\n\n"
            for i in range(chat_rounds): # 一条对话
                one_chat = chatdata[i]
                prompt = one_chat['prompt']
                response = one_chat['response'][0]
                if isinstance(response,list):
                    response = response[0]
                input = one_chat['input']
                
                if i == 0: # 首轮对话
                    # 处理文本样本
                    # prompt_for_token = "\n\nQuery:\n" + prompt + "\n" + input + "\n\nResponse:\n"
                    # prompt_for_token = "###Instruction:\n" + prompt + "\n\n###Input:\n" + input + "\n\n###Response:\n"
                    prompt_for_token = "###Instruction:\n" + prompt + input + "\n\n###Response:\n"
                    # prompt_for_token = system_overview + "###Instruction:\n" + prompt + "\n" + input + "\n\n###Response:\n"
                    response_for_token = response
                    txt_sample = prompt_for_token + "[gMASK]" + response + "eod"
                    
                    # 处理token样本
                    prompt_tok = tokenizer.tokenize(prompt_for_token)
                    response_tok = tokenizer.tokenize(response_for_token)
                    if len(prompt_tok) >= max_seq_len - 2 or len(response_tok) >= max_seq_len - 2:
                        continue
                    sample_tok = prompt_tok + [tokenizer.TokenToId('[gMASK]')] + response_tok + [tokenizer.TokenToId('eod')]
                    if len(sample_tok) < max_seq_len:
                        sample_tok = sample_tok + [tokenizer.TokenToId('[pad]')] * (max_seq_len - len(sample_tok))
                    else:
                        sample_tok = sample_tok[:max_seq_len-1] +  [tokenizer.TokenToId('eod')]
                    all_samples_tok_per_dataset.append(sample_tok)
                    # tok_preone_history = tokenizer.tokenize("[Round{}]\n".format(i)) + prompt_tok + response_tok + [tokenizer.TokenToId('eos')]
                    tok_preone_history = prompt_tok + response_tok + [tokenizer.TokenToId('eos')]
                    tok_history.append(tok_preone_history)
                    # txt_history.append("[Round{}]\n".format(i) + "Query:" + prompt + "\n\n" + "Response:" + response + "\n")
                    # txt_history.append("\n\nQuery:\n" + prompt + "\n" + input + "\n\nResponse:\n" + response + "\n")
                    # txt_history.append("###Instruction:\n" + prompt + "\n\n###Input:\n" + input + "\n\n###Response:\n" + response + "\n")
                    txt_history.append("###Instruction:\n" + prompt + "\n" + input + "\n\n###Response:\n" + response + "\n")
                    all_sample_txt_per_dataset.append(txt_sample)

                else:
                    # 处理文本样本
                    # prompt_for_token = "\n[Round{}]\n".format(i) + "Query:" + prompt + "\n\n" + "Response:"
                    # prompt_for_token = "\n\nQuery:\n" + prompt + "\n" + input + "\n\nResponse:\n"
                    # prompt_for_token = "###Instruction:\n" + prompt + "\n\n###Input:\n" + input + "\n\n###Response:\n"
                    prompt_for_token = "\n\n###Instruction:\n" + prompt + "\n" + input + "\n\n###Response:\n"
                    response_for_token = response
                    txt_sample_nohis = prompt_for_token + "[gMASK]" + response + "eod"
                    txt_sample_his = ""
                    for txt_his in txt_history:
                        txt_sample_his += txt_his
                    txt_sample_his += txt_sample_nohis
                    

                    # 处理token样本
                    prompt_tok = tokenizer.tokenize(prompt_for_token)
                    response_tok = tokenizer.tokenize(response_for_token)
                    if len(prompt_tok) >= max_seq_len - 2 or len(response_tok) >= max_seq_len - 2:
                        continue
                    sample_tok_nohis = prompt_tok + [tokenizer.TokenToId('[gMASK]')] + response_tok + [tokenizer.TokenToId('eod')]
                    # if len(response_tok+ [tokenizer.TokenToId('eod')]) >= max_seq_len:
                    #     print(len(response_tok+ [tokenizer.TokenToId('eod')]))
                    #     print(response_for_token)
                    sample_tok_his = []
                    if len(sample_tok_nohis) >= max_seq_len:
                        sample_tok_his = sample_tok_nohis[:max_seq_len-1] +  [tokenizer.TokenToId('eod')]
                    else:
                        for his in tok_history:
                            sample_tok_his += his
                        sample_tok_his += sample_tok_nohis
                        if len(sample_tok_his) >= max_seq_len:
                            sample_tok_his = sample_tok_his[-max_seq_len:]
                            sample_tok_his_np = np.array(sample_tok_his)
                            eos_indexs = np.where(sample_tok_his_np == tokenizer.TokenToId('eos'))[0]
                            first_eos = eos_indexs[0]
                            sample_tok_his = sample_tok_his[first_eos+1:]
                            # 删除掉eos符号
                            sample_tok_his_with_eos_np = np.array(sample_tok_his)
                            sample_tok_his_without_eos_np = np.delete(sample_tok_his_with_eos_np, np.where(sample_tok_his_with_eos_np == tokenizer.TokenToId('eos'))[0])
                            sample_tok_his = sample_tok_his_without_eos_np.tolist()
                            # add system overview
                            # system_overview_token = tokenizer.tokenize(system_overview)
                            # sample_tok_his = system_overview_token + sample_tok_his
                            if len(sample_tok_his) < max_seq_len:
                                sample_tok_his = sample_tok_his + [tokenizer.TokenToId('[pad]')] * (max_seq_len - len(sample_tok_his))
                            # else:
                            #     sample_tok_his = sample_tok_his[:max_seq_len-1] + [tokenizer.TokenToId('eod')]
                            #     print(len(sample_tok_his))
                        else:
                            # 删除掉eos符号
                            sample_tok_his_with_eos_np = np.array(sample_tok_his)
                            sample_tok_his_without_eos_np = np.delete(sample_tok_his_with_eos_np, np.where(sample_tok_his_with_eos_np == tokenizer.TokenToId('eos'))[0])
                            sample_tok_his = sample_tok_his_without_eos_np.tolist()
                            sample_tok_his = sample_tok_his + [tokenizer.TokenToId('[pad]')] * (max_seq_len - len(sample_tok_his))

                    all_samples_tok_per_dataset.append(sample_tok_his)
                    tok_preone_history = prompt_tok + response_tok + [tokenizer.TokenToId('eos')]
                    tok_history.append(tok_preone_history)
                    # txt_history.append("[Round{}]\n".format(i) + "Query:" + prompt + "\n\n" + "Response:" + response + "\n")
                    # txt_history.append("\n\nQuery:\n" + prompt + "\n" + input + "\n\nResponse:\n" + response + "\n")
                    # txt_history.append("###Instruction:\n" + prompt + "\n\n###Input:\n" + input + "\n\n###Response:\n" + response + "\n")
                    txt_history.append("\n\n###Instruction:\n" + prompt + "\n" + input + "\n\n###Response:\n" + response + "\n")
                    all_sample_txt_per_dataset.append(txt_sample_his)
            
        all_samples_tok.append(all_samples_tok_per_dataset)
        all_sample_txt.append(all_sample_txt_per_dataset)
    
    return all_samples_tok, all_sample_txt

def aggregating_samples(tokenizer, max_seq_len, all_samples_tok):
    shrinked_all_samples = []
    aggregation_num_list = []
    for dataset in all_samples_tok:
        shrinked_dataset = []
        aggregate_samples = []
        aggregation_num = 0
        for i in range(len(dataset)):
            sample = dataset[i]
            sample_np = np.array(sample)
            eod_index = np.where(sample_np == tokenizer.TokenToId('eod'))[0][0]
            valid_len = eod_index + 1
            valid_sample = sample[:valid_len]
            if len(valid_sample) < max_seq_len: # 如果当前样本长度小于max_seq_len才进行拼接
                if len(aggregate_samples) + len(valid_sample) <= max_seq_len: # 拼上当前样本还没有超过max_seq_len，则拼上当前样本
                    aggregate_samples += valid_sample
                    aggregation_num += 1
                else: # 否则，先将当前拼接好的aggregate_samples pad到max_seq_len，塞入shrinked_dataset，清空aggregate_samples，再将当前样本放入aggregate_samples
                    aggregate_samples_padded = aggregate_samples + [tokenizer.TokenToId('[pad]')] * (max_seq_len - len(aggregate_samples))
                    shrinked_dataset.append(aggregate_samples_padded)
                    aggregation_num_list.append(aggregation_num)
                    aggregate_samples *= 0
                    aggregate_samples += valid_sample
                    aggregation_num = 1
                if i == len(dataset) - 1: # 如果是最后一个样本，那么pad后，然后塞入shrinked_dataset
                    aggregate_samples_padded = aggregate_samples + [tokenizer.TokenToId('[pad]')] * (max_seq_len - len(aggregate_samples))
                    shrinked_dataset.append(aggregate_samples_padded)
                    aggregation_num_list.append(aggregation_num)
                    aggregate_samples *= 0   
                    aggregation_num = 1
            else: # 否则，直接将原始样本塞入shrinked_dataset
                shrinked_dataset.append(sample)
                aggregation_num = 1
                aggregation_num_list.append(aggregation_num)
        shrinked_all_samples.append(shrinked_dataset)
    
    return shrinked_all_samples, aggregation_num_list

def shuffle_dataset(datasets):
    all_datasets = []
    for subset in datasets:
        all_datasets += subset
    random.shuffle(all_datasets)

    return [all_datasets]
            



if __name__ == "__main__":
    
    

   
    # basic_int_cal_folder = "/tal-vePFS/ENGINE/datasets/basic_math_cal/generated_int_0603_10perc_split"
    # child_path_list = os.listdir(basic_int_cal_folder)
    # basic_int_cal_train, basic_int_cal_valid = [], []
    # for path in child_path_list:
    #     abs_path = basic_int_cal_folder + "/" + path
    #     if "train" in path:
    #         basic_int_cal_train.append(abs_path)
    #     elif "valid" in path:
    #         basic_int_cal_valid.append([abs_path])

    args = get_args()
    tokenizer = get_tokenizer(args)
    max_seq_len = 2048

    all_json_list = [
        args.input
    ]

    # all_samples_tok = [[[...], [...]], [[...], [...]], [[...], [...]]]
    # all_json_list = args.input
    all_samples_tok, all_sample_txt = tokenize_sample(tokenizer, max_seq_len, all_json_list)
    all_samples_tok = shuffle_dataset(all_samples_tok)

    # all_json_list_comp = commensenseIT_json_list_full_comp + basic_int_cal_train
    # all_samples_tok_comp, all_sample_txt_comp = tokenize_sample(tokenizer, max_seq_len, all_json_list_comp)
    # all_samples_tok_comp = shuffle_dataset(all_samples_tok_comp)
    # all_samples_tok_comp_ = all_samples_tok_comp[0]
    # split_rate = 0.10
    # lens = int(len(all_samples_tok_comp_) * split_rate)
    # all_samples_tok_comp_ = all_samples_tok_comp_[:lens]


    # concat data
    aggregated_all_samples, aggregation_num_list = aggregating_samples(tokenizer, max_seq_len, [all_samples_tok[0]])
    aggregation_num_list = np.array(aggregation_num_list)
    print(f"average children sample: {np.mean(aggregation_num_list)}, max chidren sample: {np.max(aggregation_num_list)}, min chidren sample: {np.min(aggregation_num_list)}, most chidren sample: {mode(aggregation_num_list)}")
    all_samples_tok[0] = aggregated_all_samples[0]
    all_samples_tok = shuffle_dataset(all_samples_tok)

    # before_aggregate_sample_num = 0
    # for dataset in all_samples_tok:
    #     before_aggregate_sample_num += len(dataset)
    # after_aggregate_sample_num = 0
    # for dataset in aggregated_all_samples:
    #     after_aggregate_sample_num += len(dataset)
    # print(f"before aggregate: {before_aggregate_sample_num}, after aggregate {after_aggregate_sample_num}.")

    train_dataset_tok, train_dataset_txt, test_dataset_tok, test_dataset_txt = split_dataset(all_samples_tok, all_sample_txt, args.split_ratio)
    level = "document"
    save_data_into_bin(args, level, train_dataset_tok)
    