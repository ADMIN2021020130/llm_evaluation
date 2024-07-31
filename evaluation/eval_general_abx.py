import os
import sys
import json
import yaml
import subprocess

class Evaluator:
    def __init__(self, config):
        self.infer_type = config["Inference"]["infer_type"]
        assert self.infer_type in ["glm-130b", "glm-6b"]
        self.infer_work_dir = config["Inference"]["work_dir"]
        self.infer_script = config["Inference"]["infer_script"]
       
        self.infer_outdir = os.path.abspath(config["Inference"]["out_dir"])
        if "max_length" in config["Inference"].keys():
            self.infer_max_length = config["Inference"]["max_length"]
        if "model_path_A" in config["Inference"].keys():

            # self.infer_model_path = config["Inference"]["model_path"]
            self.infer_model_path_A = config["Inference"]["model_path_A"]
            self.infer_model_path_B = config["Inference"]["model_path_B"]
        
        if os.path.exists(self.infer_outdir):
            # raise RuntimeError("Output dir:{} exists! Need to check".format(self.infer_outdir))
            print ("Output dir:{} exists! Need to check".format(self.infer_outdir))
        else:
            os.mkdir(self.infer_outdir)
        if not "num_gpu" in config["Inference"].keys():
            self.num_gpu = 8
        else:
            self.num_gpu = config["Inference"]["num_gpu"]
        
        self.test_sets = config["TestSet"]
        
        self.config = config


    def infer_6b(self, input_file, prefix, num_beams=1, do_sample=False, top_p=0.7, temperature=0.7):
        # bash test_glm_new.sh model_path question_file max_length num_gpu temperature answer_file
        outfile = os.path.join(self.infer_outdir, prefix+ ".jsonl")
        outfile = os.path.abspath(outfile)
        assert (not os.path.exists(outfile))
        input_file = os.path.abspath(input_file)
        print ("Infering file: {} model_A_path: {}  model_B_path:{}".format(os.path.basename(input_file), self.infer_model_path_A, self.infer_model_path_B))
        cmd = ["bash", self.infer_script, self.infer_model_path_A, self.infer_model_path_B,input_file, str(self.infer_max_length), str(self.num_gpu),str(num_beams), str(do_sample), str(top_p), outfile]
        subprocess.run(cmd, cwd=self.infer_work_dir)
        return outfile
    
    def eval_6b(self, test_name, test_script, ref_file, infer_file):
        print ("Start evaluation {}, Results:****************************".format(test_name))
        cmd = "python {} --inf-file {} --inf-key 6b".format(test_script, infer_file).split()
        subprocess.run(cmd)
        print ("End evaluation: ******************************************")
    
    def infer_130b(self, input_file, prefix):
        # TODO: 目前需要手动修改config.ini中的模型路径
        input_file = os.path.abspath(input_file)
        out_file = os.path.join(self.infer_outdir, prefix+".jsonl")
        assert (not os.path.exists(out_file))
        cmd = "bash {} {} {} {}".format(self.infer_script, input_file, self.infer_outdir, prefix).split()
        subprocess.run(cmd, cwd=self.infer_work_dir)
        return out_file
    
    def eval_130b(self, test_name, test_script, infer_file):
        print ("Start evaluation {}, Results:****************************".format(test_name))
        cmd = "python {} --inf-file {} --inf-key 130b".format(test_script, infer_file).split()
        subprocess.run(cmd)
        print ("End evaluation: ******************************************")
    
    def check_test_set(self, test_set):
        if self.infer_type == "glm-130b":
            assert "130b_json_path" in test_set.keys() and "130b_test_script" in test_set.keys()
        if self.infer_type == "glm-6b":
            assert "6b_json_path" in test_set.keys() and "6b_test_script" in test_set.keys()

    def evaluate(self):
        for test_name in self.test_sets.keys():
            try:
                test_set = self.test_sets[test_name]
                self.check_test_set(test_set)
                if self.infer_type == "glm-130b":
                    infer_file = self.infer_130b(test_set["130b_json_path"], test_set["prefix"])
                    self.eval_130b(test_name, test_set["130b_test_script"], infer_file)

                elif self.infer_type == "glm-6b":

                    infer_file = self.infer_6b(test_set["6b_json_path"], test_set["prefix"], \
                        temperature=test_set.get("temperature", 0.7), do_sample=test_set.get("do_sample", False), \
                        num_beams=test_set.get("num_beams", 1), top_p=test_set.get("top_p", 0.7))
                    
                    # self.eval_6b(test_name, test_set["6b_test_script"], test_set["6b_json_path"], infer_file)
            except Exception as e:
                print ("Failed to evaluate {} due to {}".format(test_name, e))

if __name__ == '__main__':
    yaml_file = sys.argv[1]
    yaml_dict = yaml.safe_load(open(yaml_file))
    evaluator = Evaluator(yaml_dict)
    evaluator.evaluate()
