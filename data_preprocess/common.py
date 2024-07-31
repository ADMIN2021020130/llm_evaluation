import os
import sys

class DataFlow:
    def __init__(self):
        self.ori_data_path = ""
        self.shuffle_data = True
        self.sample_ratio = None
        self.sample_num = None
        # Data Structure:
        '''data_format = {
           "id":"",
           "data":[{
             "prompt":"",
             "input": "",
             "response": [["<text>", "<from>"]],
           }],
           "domain": [],
        }
        '''
        self.ori_data = []
        self.sampled_data = []
        self.cleaned_data = []

def merge_dataflow(dataflow_list):
    merged_dataflow = DataFlow()
    for dataflow in dataflow_list:
        merged_dataflow.ori_data += dataflow.ori_data
        merged_dataflow.sampled_data += dataflow.sampled_data
        merged_dataflow.cleaned_data += dataflow.cleaned_data
    return merged_dataflow