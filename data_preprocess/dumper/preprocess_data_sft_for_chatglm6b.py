import json
import sys
import argparse
import multiprocessing
import torch
import numpy as np
import re
import os
import time
from tqdm import tqdm
try:
    import nltk
    nltk_available = True
except ImportError:
    nltk_available = False
# from SwissArmyTransformer import get_args, get_tokenizer
from megatron.tokenizer import build_tokenizer
from megatron.data import indexed_dataset

__DISPLAY_DETAIL__ = False
__DISPLAY_FIRST_DATA__ = True

'''
读取部分或者全量原始数据，用于后续处理
params : 
    @json_file : [str], 数据源文件
    @test_data_num : [int], 获取数据的数目，默认-1， 会读取全量数据，也可传入其他正值

return ：
    [list[dict]] : 原始数据append 
'''
def load_json_copy_part(json_file:str, test_data_num:int, used_ratio) -> list:
    count = 0
    res = []
    print("Loading data from {}".format(json_file))
    with open(json_file, 'r') as inf:
        datas = json.load(inf)
        for line in datas:
            data = line
            res.append(data)
            count += 1
            if test_data_num!=-1 and count >= test_data_num:
                break

    dropped_idx = np.round(np.linspace(0, len(res) - 1, int(len(res) * (1-used_ratio)))).astype(int)
    res_test  = [i for idx, i in enumerate(res) if idx not in dropped_idx]
    rest_test = [i for idx, i in enumerate(res) if idx in dropped_idx]

    return res_test, rest_test
            
'''
解析原始数据，仅使用prompt和response
'''
def get_prompt_response(data_path:str) -> list:
    print("Get prompt and response from {}".format(data_path))
    all_data_list = []
    with open(data_path, 'r') as fr:
        for line in tqdm(fr.readlines()):
            data = json.loads(line.strip())["data"][0]
            _prompt, _input, _response = data['prompt'], data['input'], data['response'][0][0]
            # 预期的输入组织格式是 ： ref : https://github.com/tatsu-lab/stanford_alpaca/blob/main/train.py#36
            #    "### Instruction:\n{instruction}\n\n### Input:\n{input}\n\n### Response:"
            #if input.strip() == "":
            #    prompt = "### Instruction:\n{}\n\n### Response:\n".format(_prompt)
            #else:
            #    prompt = "### Instruction:\n{}\n\n### Input:\n{}\n\n### Response:\n".format(_prompt, _input)
            # prompt = "### Instruction:\n{}\n\n### Input:\n{}\n\n### Response:\n".format(_prompt, _input)
            prompt = "[Round {}]\n问：{}\n答：".format(0, _prompt+_input)
            response = _response
            all_data_list.append([prompt, response])
    return all_data_list


'''
获取prompt, response， 分别tokenizer, 
在中间添加 [gMASK] id
padding / cutting
'''
def preprare_binary_it_data(list_str_prmpt_resp:list, tokenizer, length_per_samples=1024, gmask_pos="before_resp"):
    print
    res = []
    for idx, (prompt, response) in tqdm(enumerate(list_str_prmpt_resp)):
        _tkn_prompt = tokenizer.tokenize(prompt)
        tkn_prompt = []
        for i in _tkn_prompt:
            tkn_id = tokenizer._convert_token_to_id(i)
            tkn_prompt.append(tkn_id)
        if len(tkn_prompt) > length_per_samples-4:
            continue
        # if len(tkn_prompt) > length_per_samples-1:
        #     continue
        # txt_itdata = prompt + '[gMASK]' + response + 'eod'
        # tkn_itdata = tokenizer.tokenize(txt_itdata)
        _tkn_respns = tokenizer.tokenize(response)
        tkn_respns = []
        for i in _tkn_respns:
            tkn_id = tokenizer._convert_token_to_id(i)
            tkn_respns.append(tkn_id)

        # _eod_id   = tokenizer.end_token if args.glm_6b else tokenizer.get_special_token("eod")
        # _mask_id  = tokenizer.mask_token if args.glm_6b else tokenizer.get_special_token("MASK")
        # _gmask_id = tokenizer.gmask_token if args.glm_6b else tokenizer.get_special_token("gMASK")
        # _sop_id   = tokenizer.bos_token if args.glm_6b else tokenizer.get_special_token("sop")
        # _eop_id   = tokenizer.eos_token if args.glm_6b else tokenizer.get_special_token("eop")
        assert gmask_pos in ["before_prompt", "before_resp"]
        if gmask_pos == "before_prompt":
            tkn_itdata = [tokenizer._convert_token_to_id(tokenizer.gmask_token), tokenizer._convert_token_to_id(tokenizer.bos_token)] + tkn_prompt \
              + tkn_respns + [tokenizer._convert_token_to_id(tokenizer.eos_token)] + [tokenizer._convert_token_to_id(tokenizer.end_token)]
        elif gmask_pos == "before_resp":
            tkn_itdata = tkn_prompt + [tokenizer._convert_token_to_id(tokenizer.gmask_token), tokenizer._convert_token_to_id(tokenizer.bos_token)] \
                + tkn_respns + [tokenizer._convert_token_to_id(tokenizer.eos_token)] + [tokenizer._convert_token_to_id(tokenizer.end_token)]
        if len(tkn_itdata) < length_per_samples:
            padded_tkn_itdata = tkn_itdata + [tokenizer._convert_token_to_id(tokenizer.pad_token)] * (length_per_samples - len(tkn_itdata))
        else:
            padded_tkn_itdata = tkn_itdata[:length_per_samples-2] + [tokenizer._convert_token_to_id(tokenizer.eos_token)] + [tokenizer._convert_token_to_id(tokenizer.end_token)]
            # padded_tkn_itdata = tkn_itdata[:length_per_samples-1] +  [tokenizer.encode(tokenizer.end_token)]
        if __DISPLAY_DETAIL__:
            print("{} : len of tkn_prompt : {}, tkn_respns : {}, tkn_itdata : {}, padded_tkn_itdata : {}".format(idx, len(tkn_prompt), len(tkn_respns), len(tkn_itdata), len(padded_tkn_itdata)))
        res.append(padded_tkn_itdata)
        # print(padded_tkn_itdata)
    max_tkn = []
    for i in res:
        max_tkn.append(max(i))
    # print(max(max_tkn))
    return res

 
def save_data_into_bin(args, level, tkn_padded_samples, tokenizer):
    print("Write processed data to bin.")
    startup_start = time.time()
    if args.split_sentences:
        level = "sentence"
    key = args.json_key
    output_bin_files = {}
    output_idx_files = {}
    builders = {}
    output_bin_files[key] = "{}_{}_{}.bin".format(args.output_prefix, key, level)
    output_idx_files[key] = "{}_{}_{}.idx".format(args.output_prefix, key, level)
    builders[key] = indexed_dataset.make_builder(output_bin_files[key], impl=args.dataset_impl, dtype=indexed_dataset.best_fitting_dtype(tokenizer.vocab_size))

    startup_end = time.time()
    proc_start = time.time()
    print("Time to startup:", startup_end - startup_start)

    print("Got {} samples, and processed into padded_tkn".format(len(tkn_padded_samples)))
    for idx, item in enumerate(tkn_padded_samples):
        if __DISPLAY_DETAIL__:
            print("saving {} item, len={}".format(idx, len(item)))
        builders[key].add_item(torch.IntTensor(item))
        if idx % 1000 == 0:
            current = time.time()
            elapsed = current - proc_start
            print(f"Processed {idx} documents",
                  f"({idx/elapsed} docs/s).",
                  file=sys.stderr)


    builders[key].end_document()

    builders[key].finalize(output_idx_files[key])


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
    # print(text)

def save_ori_data_into_json(input_list, out_json_prefix, type_set):
    filename = out_json_prefix.strip() + type_set.strip() + "_ori.json"

    with open(filename.strip(), 'w') as ouf_test:
        json.dump(input_list, ouf_test, ensure_ascii=False, indent=4)

        
def save_data_into_json(input_list, out_json_prefix, type_set):
    filename = out_json_prefix.strip() + type_set.strip() + ".json"
    print("Saving processed data to json: {}".format(filename))
    with open(filename.strip(), 'w') as ouf_test:
        for prompt, response in tqdm(input_list):
            new_text = "{}[gMASK]{}".format(prompt, response).strip()
            ouf_test.write(json.dumps(new_text, ensure_ascii=False, indent=4)+"\n")


def display_generated_text(list_str_prmpt_resp, part_test_data):
    for i, j  in zip(list_str_prmpt_resp, part_test_data):
        print(j['data'][0])
        print("-----" * 30)
        print("[gMASK]".join(i))
        print("=====" * 30)


def get_args():
    parser = argparse.ArgumentParser()
    group = parser.add_argument_group(title='input data')
    group.add_argument('--input', type=str, required=True,
                       help='Path  to input JSON')
    group.add_argument('--gmask-pos', type=str, required=True,
                        help='GMASK pos: before_prompt, before_resp')
    group.add_argument('--num_samples', type=int, default=-1, 
                       help='Numbers of samples you want to process')   
    group.add_argument('--used_ratio', type=float, required=False,
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
                                'GPT2BPETokenizer', 'PretrainedFromHF', 'IceTokenizer', 'icetk-glm-130B', 'ChatGLMTokenizer'],
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
    group.add_argument('--rank', type=int, default=0, help='Interval between progress updates')
    group.add_argument('--tensor_model_parallel_size', type=int, default=1, help='Interval between progress updates')
    args = parser.parse_args()
    args.keep_empty = False

    return args




def main():
    args = get_args()
    # tokenizer = get_tokenizer(args)
    tokenizer = build_tokenizer(args)

    data_path = args.input
    test_data_num = args.num_samples
    used_ratio = args.used_ratio

    all_data_list = get_prompt_response(data_path)

    out_json_prefix = args.output_prefix.strip() + "_"
    save_data_into_json(all_data_list, out_json_prefix, "data")

    #对数据添加[gMASK], 做tokenizer， padding/cutting
    tkn_padded_samples = preprare_binary_it_data(all_data_list, tokenizer, gmask_pos="before_prompt")
    if __DISPLAY_FIRST_DATA__:
        print(len(tkn_padded_samples[0]), tkn_padded_samples[0])

    # 保存至bin文件
    level = "document"
    save_data_into_bin(args, level, tkn_padded_samples, tokenizer)
    

def unit_test():
    args = get_args()
    args.tokenizer_type = "ChatGLMTokenizer"
    tokenizer = build_tokenizer(args)
    list_str_prmpt_resp = [["你是谁", "我是MathGPT"]]
    list_str_prmpt_resp = [["作为AI语言模型，我没有感官，无法对物体进行观察，也就不具备对老年人开车速度的评估能力。但是有些老年人因为身体机能、身体素质、驾龄等的限制。","_"]]
    for idx, (prompt, response) in tqdm(enumerate(list_str_prmpt_resp)):
        _tkn_prompt = tokenizer.tokenize(prompt)
        print(prompt, _tkn_prompt)
        tkn_prompt = []
        s = time.time()
        for i in _tkn_prompt:
            tkn_id = tokenizer._convert_token_to_id(i)
            tkn_prompt.append(tkn_id)
        print("runtime1: ", time.time()-s)
        print("tkn_prompt:" ,tkn_prompt)
        s = time.time()
        token_prompt = tokenizer(prompt)['input_ids'][:-2]
        print("runtime2: ", time.time()-s)
        print("token_prompt", token_prompt)
        _tkn_respns = tokenizer.tokenize(response)
        print(response, _tkn_respns)
        tkn_respns = []
        for i in _tkn_respns:
            tkn_id = tokenizer._convert_token_to_id(i)
            tkn_respns.append(tkn_id)


if __name__ == "__main__":
    main()
    # unit_test()
