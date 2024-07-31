#!/bin/bash

# export CUDA_VISIBLE_DEVICES="4,5,6,7"
export PYTHONPATH=/mnt/pfs/jinfeng_team/SFT/caiguodu/workspace/projects/largescale_for_glm_series

if [ $# -ne 9 ]; then 
    echo "Usage $0 <model> <test-file> <max-length> <num-gpus> <num-beams> <do-sample> <top-p> <temperature> <answer-file>"
    exit 1
fi
A_md_model_path=$1
B_md_model_path=$2

question_file=$3
max_length=$4
num_gpus=$5
num_beams=$6
do_sample=$7
top_p=$8
answer_file=$9
temperature=0.01
# top_p=0.7
A_md_model_path=$(echo "$A_md_model_path" | sed 's/\/$//')
A_hf_model_path=${A_md_model_path}-hf

B_md_model_path=$(echo "$B_md_model_path" | sed 's/\/$//')
B_hf_model_path=${B_md_model_path}-hf


# output_dir=`dirname $hf_model_path`/output
# mkdir -p $output_dir
# answer_file=$output_dir/`basename $question_file .json`-`basename $md_model_path`-nb${num_beams}-ds${do_sample}-topp${top_p}-temp${temperature}.json
model_id_A=`basename $A_md_model_path`

model_id_B=`basename $B_md_model_path`

echo $model_id_A
echo $model_id_B


if [ ! -f ${A_hf_model_path}/pytorch_model.bin ]; then 
    echo "Convert $A_md_model_path from megatron to huggingface."
    python /mnt/pfs/jinfeng_team/SFT/caiguodu/workspace/projects/largescale_for_glm_series/local/convert_chatglm_hf_to_mgtdp/convert.py --md-model $A_md_model_path --hf-model $A_hf_model_path || exit 1
fi


if [ ! -f ${B_hf_model_path}/pytorch_model.bin ]; then 
    echo "Convert $B_md_model_path from megatron to huggingface."
    python /mnt/pfs/jinfeng_team/SFT/caiguodu/workspace/projects/largescale_for_glm_series/local/convert_chatglm_hf_to_mgtdp/convert.py --md-model $B_md_model_path --hf-model $B_hf_model_path || exit 1
fi



if [ ! -f $answer_file ]; then 
    python ./general_auto_eval_abx.py \
        --A-model $model_id_A \
        --B-model $model_id_B \
        --model-A-path $A_hf_model_path \
        --model-B-path $B_hf_model_path\
        --question-file $question_file \
        --answer-file $answer_file \
        --num-gpus $num_gpus \
        --max-length $max_length \
        --num-beams $num_beams \
        --do-sample $do_sample \
        --top-p $top_p \
        --temperature $temperature \
    || exit 1
fi


if [[ -f `dirname $question_file`/eval.py ]]; then
    # python `dirname $question_file`/eval.py --ref-file $question_file --inf-file $answer_file
    python `dirname $question_file`/eval.py --inf-file   $answer_file  --model-A  model_A  --model-B model_B
fi

