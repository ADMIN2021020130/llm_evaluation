from common import DataFlow, merge_dataflow
from parser.parser import *
from sampler.sampler import *
from cleaner.cleaner import *
from dumper.dumper import *
import yaml
import sys
from util import count_token

class DataPreprocessor:
    def __init__(self, yaml_dict):
        self.sampler = Sampler(yaml_dict)
        self.dumper = Dumper(yaml_dict["DataDump"])

    def process_one_flow(self, data_id, yaml_data):
        data_flow = DataFlow()
        assert ("file_path" in yaml_data.keys()) or ("file_path_list" in yaml_data.keys())
        if "file_path" in yaml_data.keys():
            data_flow.ori_data_path = yaml_data["file_path"]
        elif "file_path_list" in yaml_data.keys():
            # If file_path_list exists, skip file_path:
            data_flow.ori_data_path = None
            data_flow.ori_data_path_list = yaml_data["file_path_list"]
        config = dict()
        if "single_resp" in yaml_data.keys():
            config["single_resp"] = yaml_data["single_resp"]
        parser = get_parser(yaml_data["parser"], config)
        parser.parse(data_flow)
        token_count, token_count_bill = count_token(data_flow.ori_data)
        print ("Data ID: {}, Tokens {}B".format(data_id, token_count_bill))

        if "sample_num" in yaml_data.keys():
            data_flow.sample_num = yaml_data["sample_num"]
        if "sample_ratio" in yaml_data.keys():
            data_flow.sample_ratio = yaml_data["sample_ratio"]
        self.sampler.sample(data_flow)
        cleaner = get_cleaner(yaml_data["cleaner"], config)
        cleaner.clean(data_flow)
        return data_flow

    def process(self, yaml_dict):
        data_flow_list = list()
        for data_id in yaml_dict["DataSource"]:
            data_flow = self.process_one_flow(data_id, yaml_dict["DataSource"][data_id])
            data_flow_list.append(data_flow)
        
        merged_dataflow = merge_dataflow(data_flow_list)
        self.dumper.dump(merged_dataflow)
        
if __name__ == '__main__':
    yaml_file = sys.argv[1]
    yaml_dict = yaml.safe_load(open(yaml_file))
    data_preprocessor = DataPreprocessor(yaml_dict)
    data_preprocessor.process(yaml_dict)


        

        