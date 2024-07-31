import os
import sys
import json
import logging
from tqdm import tqdm
from util import count_token, check_format

class BaseParser:
    def __init__(self, config):
        pass

    def parse(self, data_flow):
        pass
    
    def load_ori_jsonfiles(self, data_flow):
        lines = []
        filename_list = []
        if data_flow.ori_data_path != None:
            print ("Loading ori data: {}".format(data_flow.ori_data_path))
            lines = open(data_flow.ori_data_path).readlines()
            filename_list = [os.path.basename(data_flow.ori_data_path)] * len(lines)
        else:
            print ("Loading ori data list: {}".format(data_flow.ori_data_path_list))
            for file_path in tqdm(data_flow.ori_data_path_list):
                tmp_lines = open(file_path).readlines()
                lines += tmp_lines
                filename_list += [os.path.basename(file_path)] * len(tmp_lines)
        assert len(filename_list) == len(lines)
        return lines, filename_list

class LargescaleParser(BaseParser):
    def __init__(self, config):
        if "single_resp" in config.keys():
            self.single_resp = config["single_resp"]
        else:
            self.single_resp = False

    def parse(self, data_flow):
        bad_count = 0
        finished_count = 0
        
        lines, filename_list = self.load_ori_jsonfiles(data_flow)

        for idx, l in tqdm(enumerate(lines)):
            try:
                id = "{}_{}".format(filename_list[idx], idx)
                cur_data = json.loads(l.strip())
                cur_data["id"] = id
                if self.single_resp and (not check_format(cur_data)):
                    if type(cur_data["data"][0]["response"]) == str:
                        resp = cur_data["data"][0]["response"]
                    else:
                        resp = cur_data["data"][0]["response"][0]
                    cur_data["data"][0]["response"] = [[resp]]
                if check_format(cur_data):
                    finished_count += 1
                    data_flow.ori_data.append(cur_data)
                else:
                    bad_count += 1
            except:
                import pdb
                pdb.set_trace()
                bad_count += 1

        logging.warn("Processing {}. Finished {} samples, failed {} samples.".format(\
            data_flow.ori_data_path, finished_count, bad_count))
        
class GLMHistorParser(BaseParser):
    def __init__(self, config):
        pass
    def parse(self ,data_flow):
        bad_count = 0
        finished_count = 0
        lines, filename_list = self.load_ori_jsonfiles(data_flow)
        for idx, l in enumerate(lines):
            out_data = {
                    "id":"",
                    "data":[{
                        "prompt":"",
                        "input": "",
                        "response": [["", ""]],
                    }],
                    "domain": [],
            }
            try:
                id = "{}_{}".format(filename_list[idx], idx)
                cur_data = json.loads(l.strip())
                out_data["id"] = id
                out_data["data"][0]["prompt"] = cur_data["prompt"]
                out_data["data"][0]["input"] = " ".join(cur_data["history"])
                out_data["data"][0]["response"][0][0] = cur_data["response"]
                finished_count += 1
                data_flow.ori_data.append(out_data)
            except:
                bad_count += 1
        logging.warn("Processing {}. Finished {} samples, failed {} samples.".format(\
            data_flow.ori_data_path, finished_count, bad_count))

def get_parser(parser_name, config):
    if parser_name == "base":
        return BaseParser(config)
    elif parser_name == "glm_history":
        return GLMHistorParser(config)
    elif parser_name == "large_scale":
        return LargescaleParser(config)
    else:
        return None
    
if __name__ == '__main__':
    pass