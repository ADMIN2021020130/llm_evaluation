import sys
import os
import logging
import json
import random as rd

# 考虑到Dump的方式不多，就用一个Dumper统一处理
class Dumper:
    def __init__(self, config):
        self.shuf_before_dump = config["shuf_before_dump"]
        self.format = config["format"]
        assert self.format in ["large_scale", "glm_history", "130B"]
        self.output_dir = config["output_dir"]
        self.prefix = config["prefix"]
        self.gmask_pos = config["gmask_pos"]
        assert self.gmask_pos in ["before_prompt", "before_resp"]
        if "generate_bin" in config.keys() and config["generate_bin"]:
            self.generate_bin = True
            # self.tokenize_recipe_path = config["tokenize_recipe_path"]
            self.tokenizer_type = config.get("tokenizer_type", "sft")
        else:
            self.generate_bin = False
        self.config = config
    
    def tokenize(self, data_flow):
        pass
    
    def dump(self, data_flow):
        bad_count = 0
        finished_count = 0
        out_json_file = os.path.join(self.output_dir, "{}.json".format(self.prefix))
        if self.shuf_before_dump:
            rd.shuffle(data_flow.cleaned_data)
        if self.format == "large_scale" or self.format == "130B":
            with open(out_json_file, "w", encoding="utf-8") as fw:
                for item in data_flow.cleaned_data:
                    try:
                        fw.write("{}\n".format(json.dumps(item, ensure_ascii=False)))
                        finished_count += 1
                    except:
                        bad_count += 1
            if self.format == "large_scale":
                cmd = "bash dumper/preprocess_data.sh {} {} {} {} {}".format( \
                    out_json_file, self.prefix, self.output_dir, self.tokenizer_type, \
                    self.gmask_pos)
            else:
                output_prefix = os.path.join(self.output_dir, self.prefix)
                cmd = "bash dumper/process_130B_data.sh {} {}".format(out_json_file, output_prefix)
                # cmd = "bash dumper/process_130B_data_yuanye.sh {} {}".format(out_json_file, output_prefix)
            os.system(cmd)

        elif self.format == "glm_history":
            pass
        else:
            pass

        logging.warn("Dumping {}. Finished {} samples, failed {} samples.".format(\
            out_json_file, finished_count, bad_count))
