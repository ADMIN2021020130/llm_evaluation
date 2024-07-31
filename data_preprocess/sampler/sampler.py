import random as rd
import logging

class Sampler:
    def __init__(self, config):
        pass

    def sample(self, data_flow):
        if data_flow.sample_num == None:
            if data_flow.sample_ratio == None:
                sample_num = len(data_flow.ori_data)
            else:
                sample_ratio = min(1, data_flow.sample_ratio)
                sample_num = int(sample_ratio * len(data_flow.ori_data))
        else:
            sample_num = min(data_flow.sample_num, len(data_flow.ori_data))

        assert sample_num > 0 and sample_num <= len(data_flow.ori_data)

        if data_flow.shuffle_data:
            rd.shuffle(data_flow.ori_data)
        
        # TODO: 看是否需要清理ori_data内存占用
        data_flow.sampled_data = data_flow.ori_data[:sample_num]
        logging.warn("Sample from data {},  num: {}".format(data_flow.ori_data_path, sample_num))

if __name__ == '__main__':
    pass
        
