import os
import re
import sys
import fire
import time
import json
import random
import signal
from typing import Tuple, List, Optional
import pandas as pd
from datasets import load_metric
import shortuuid

def format_subject(subject):
    l = subject.split("_")
    s = ""
    for entry in l:
        s += " " + entry
    return s

def gen_prompt(train_df, subject, k=-1):
    prompt = "The following are multiple choice questions (with answers) about {}.\n\n".format(format_subject(subject))
    if k == -1: 
        k = train_df.shape[0]
    for i in range(k):
        prompt += format_example(train_df, i)
    return prompt

def format_example(df, idx, include_answer=True):
    choices = ["A", "B", "C", "D"]
    prompt = df.iloc[idx, 0]
    k = df.shape[1] - 2
    for j in range(k):
        prompt += "\n{}. {}".format(choices[j], df.iloc[idx, j+1])
    prompt += "\nAnswer:"
    if include_answer:
        prompt += " {}\n\n".format(df.iloc[idx, k + 1])
    return prompt

def get_choices(df, idx):
    choices = ["A", "B", "C", "D"]
    choices_dicts = {}    
    k = df.shape[1] - 2
    for j in range(k):
        choices_dicts[choices[j]] = df.iloc[idx, j+1]
    return choices_dicts

def load_mmlu_csv_to_prompts(path: str, nshots = 5, tokenizer_path = None, max_shots_len = 750):

    """
    MMLU is a quite large testset contains different subject
    Parameter path is a MMLU directory and contains a test 
    and dev subdirectory. Each subject have a test csv in 
    test subdirectory and the same as dev subdirectory. This
    function will load all the csvs. 

    Args:
    path: a directory
    nshots: number of few shots. These shots is load from devsets
    Returns:

    """

    test_dir = os.path.join(path, "test")
    dev_dir = os.path.join(path, "dev")
    if not os.path.isdir(test_dir):
        raise Exception(f"{test_dir} not a path")
    if not os.path.isdir(dev_dir):
        raise Exception(f"{dev_dir} not a path")

    if tokenizer_path is not None:
        tokenizer = Tokenizer(model_path=tokenizer_path)
    else:
        tokenizer = None

    prompts = []
    answers = []
    choices = []
    courses = []
    subjects = sorted([f.split("_test.csv")[0] for f in os.listdir(test_dir) if "_test.csv" in f])

    for subject in subjects:
        dev_df = pd.read_csv(os.path.join(dev_dir, f"{subject}_dev.csv"), header=None)[:nshots]
        test_df = pd.read_csv(os.path.join(test_dir, f"{subject}_test.csv"), header=None)

        for i in range(test_df.shape[0]):
            prompt_end = format_example(test_df, i, include_answer=False)
            #print("prompt_end:", prompt_end)
            shots = gen_prompt(dev_df, subject, nshots)
            prompt = shots + prompt_end
            if tokenizer is not None:
                num_toks = len(tokenizer.encode(prompt, bos=True, eos=False))
                k = nshots
                while num_toks > max_shots_len and k > 0:
                    k -= 1
                    shots = gen_prompt(dev_df, subject, k)
                    prompt = shots + prompt_end
                    num_toks = len(tokenizer.encode(prompt, bos=True, eos=False))
                    # Drop those too long prompts
                if num_toks <= max_shots_len:
                    prompts.append(prompt)
                    answers.append(test_df.iloc[i, test_df.shape[1]-1])
                else:
                     print("Too long prompts {} in {}".format(num_toks, subject))

            else:
                prompts.append(prompt)
                answers.append(test_df.iloc[i, test_df.shape[1]-1])
                choices.append(get_choices(test_df, i))
                courses.append(subject)

    return prompts, answers, choices, courses

def get_data_format(id="", prompt="", input="", response="", from_type="", domain="", choice = ""):
    if type(domain) != list:
        domain = [domain]
    data_format = {
        "id": id,
        "data":[{
            "prompt": str(prompt),
            "input": str(input),
            "response": [[str(response), str(from_type)]],
            "choice": choice,
        }],
        "domain": domain,
    }
    if data_format["id"] == "":
        data_format["id"] = shortuuid.uuid(name=str(data_format["data"]))
    return data_format

subcategories = {
    "abstract_algebra": ["math"],
    "anatomy": ["health"],
    "astronomy": ["physics"],
    "business_ethics": ["business"],
    "clinical_knowledge": ["health"],
    "college_biology": ["biology"],
    "college_chemistry": ["chemistry"],
    "college_computer_science": ["computer science"],
    "college_mathematics": ["math"],
    "college_medicine": ["health"],
    "college_physics": ["physics"],
    "computer_security": ["computer science"],
    "conceptual_physics": ["physics"],
    "econometrics": ["economics"],
    "electrical_engineering": ["engineering"],
    "elementary_mathematics": ["math"],
    "formal_logic": ["philosophy"],
    "global_facts": ["other"],
    "high_school_biology": ["biology"],
    "high_school_chemistry": ["chemistry"],
    "high_school_computer_science": ["computer science"],
    "high_school_european_history": ["history"],
    "high_school_geography": ["geography"],
    "high_school_government_and_politics": ["politics"],
    "high_school_macroeconomics": ["economics"],
    "high_school_mathematics": ["math"],
    "high_school_microeconomics": ["economics"],
    "high_school_physics": ["physics"],
    "high_school_psychology": ["psychology"],
    "high_school_statistics": ["math"],
    "high_school_us_history": ["history"],
    "high_school_world_history": ["history"],
    "human_aging": ["health"],
    "human_sexuality": ["culture"],
    "international_law": ["law"],
    "jurisprudence": ["law"],
    "logical_fallacies": ["philosophy"],
    "machine_learning": ["computer science"],
    "management": ["business"],
    "marketing": ["business"],
    "medical_genetics": ["health"],
    "miscellaneous": ["other"],
    "moral_disputes": ["philosophy"],
    "moral_scenarios": ["philosophy"],
    "nutrition": ["health"],
    "philosophy": ["philosophy"],
    "prehistory": ["history"],
    "professional_accounting": ["other"],
    "professional_law": ["law"],
    "professional_medicine": ["health"],
    "professional_psychology": ["psychology"],
    "public_relations": ["politics"],
    "security_studies": ["politics"],
    "sociology": ["culture"],
    "us_foreign_policy": ["politics"],
    "virology": ["health"],
    "world_religions": ["philosophy"],
}

categories = {
    "STEM": ["physics", "chemistry", "biology", "computer science", "math", "engineering"],
    "humanities": ["history", "philosophy", "law"],
    "social sciences": ["politics", "culture", "economics", "geography", "psychology"],
    "other (business, health, misc.)": ["other", "business", "health"],
}


if __name__ == "__main__":
    data = []
    prompts, answers, choices, courses = load_mmlu_csv_to_prompts("/mnt/vepfs/SFT/zhangshusheng/opensrc_datasets//mmlu/data", nshots=0)
    for i in range(len(prompts)):
        prompt = prompts[i]
        answer = answers[i]
        choice = choices[i]
        course = courses[i]
        subcategorie = subcategories[course][0]
        for j in categories.keys():
            if subcategorie in categories[j]:
                categorie = j
        data_format = get_data_format(id="", prompt=prompt, input="", response=answer, from_type="MMLU", domain=["General", "MMLU", categorie, subcategorie, course], choice=choice)      
        data.append(data_format)
        print(data_format)

    fw = open("mmlu_prompt.json", "w")
    for item in data:
        json_str = json.dumps(item, ensure_ascii=False)
        fw.write(json_str + "\n")

