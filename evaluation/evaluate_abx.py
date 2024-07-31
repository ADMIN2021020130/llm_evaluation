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
            self.infer_model_path_A = config["Inference"]["model_path_A"]
        if "model_path_B" in config["Inference"].keys():
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
        print ("Infering file: {} model_A_path: {}  model_B_path:{}".format(os.path.basename(input_file), self.infer_model_path_A, self.infer_model_path_B))
        assert (not os.path.exists(outfile))
        input_file = os.path.abspath(input_file)

        cmd = ["bash", self.infer_script, self.infer_model_path_A, self.infer_model_path_B,input_file, str(self.infer_max_length), str(self.num_gpu),str(num_beams), str(do_sample), str(top_p), outfile]
        subprocess.run(cmd, cwd=self.infer_work_dir)
        return outfile
    
    def eval_6b(self, test_name, test_script, ref_file, infer_file):
        print ("Start evaluation {}, Results:****************************".format(test_name))
        cmd = "python {} --inf-file {} --inf-key 6b".format(test_script, infer_file).split()
        subprocess.run(cmd)
        print ("End evaluation: ******************************************")
    
    def load_human_res(self, jsonfile):
        lines = open(jsonfile).readlines()
        res = []
        for l in lines:
            data = json.loads(l.strip())
            res.append(data)
        return res 
    
    def merge_results(self, out_file_A, out_file_B, out_file):
        data_A = self.load_human_res(out_file_A)
        data_B = self.load_human_res(out_file_B)
        fw = open(out_file, "w")
        for itemA in data_A:
            itemA["model_A"] = itemA["130b"]
            del itemA["130b"]
            for itemB in data_B:
                if(itemA["taskid"])==itemB["taskid"]:
                    itemA["model_B"]=itemB["130b"]
            fw.write(json.dumps(itemA, ensure_ascii=False)+"\n")
        return out_file
    
    def infer_130b(self, input_file, prefix):
    	# TODO: 目前需要手动修改config.ini中的模型路径
       	current_path = os.getcwd()
       	current_path = os.path.join(current_path, self.infer_outdir)
       	input_file = os.path.abspath(input_file)
       	out_file_A = os.path.join(self.infer_outdir, prefix+"/"+prefix+"_A.jsonl")
       	out_file_B = os.path.join(self.infer_outdir, prefix+"/"+prefix+"_B.jsonl")
       	out_file = os.path.join(self.infer_outdir, prefix+"/"+prefix+".jsonl")
       	prefix_A = prefix + "_A"
       	prefix_B = prefix + "_B"
       	assert (not os.path.exists(out_file_A))
       	assert (not os.path.exists(out_file_B))
       	cmd_A = "bash {} {} {} {} {} {}".format(self.infer_script, self.infer_model_path_A, current_path, prefix, "A", input_file).split()
       	print("cmd_A:", cmd_A)
       	subprocess.run(cmd_A, cwd=self.infer_work_dir)
       	cmd_B = "bash {} {} {} {} {} {}".format(self.infer_script, self.infer_model_path_B, current_path, prefix, "B", input_file).split()
        print("cmd_B:", cmd_B)
       	subprocess.run(cmd_B, cwd=self.infer_work_dir)
       	out_file = self.merge_results(out_file_A, out_file_B, out_file)

       	return out_file
    
    def eval_130b(self, test_name, test_script, infer_file):
        print ("Start evaluation {}, Results:****************************".format(test_name))
        cmd = "python {} --inf-file {} --model-A model_A --model-B model_B".format(test_script, infer_file).split()
        subprocess.run(cmd)
        print ("End evaluation: ******************************************")
    
    def check_test_set(self, test_set):
        if self.infer_type == "glm-130b":
            assert "130b_json_path" in test_set.keys() and "130b_test_script" in test_set.keys()
        if self.infer_type == "glm-6b":
            assert "6b_json_path" in test_set.keys() and "6b_test_script" in test_set.keys()

    def evaluate(self):
        for test_name in self.test_sets.keys():
               
            #try:
            if(True):
                test_set = self.test_sets[test_name]
                self.check_test_set(test_set)
                if self.infer_type == "glm-130b":
                    infer_file = self.infer_130b(test_set["130b_json_path"], test_set["prefix"])
                    self.eval_130b(test_name, test_set["130b_test_script"], infer_file)
                elif self.infer_type == "glm-6b":
                        infer_file = self.infer_6b(test_set["6b_json_path"], test_set["prefix"], \
                        temperature=test_set.get("temperature", 0.7), do_sample=test_set.get("do_sample", False), \
                        num_beams=test_set.get("num_beams", 1), top_p=test_set.get("top_p", 0.7))
            #except Exception as e:
            #     print ("Failed to evaluate {} due to {}".format(test_name, e))

if __name__ == '__main__':
    yaml_file = sys.argv[1]
    yaml_dict = yaml.safe_load(open(yaml_file))
    evaluator = Evaluator(yaml_dict)
    evaluator.evaluate()


