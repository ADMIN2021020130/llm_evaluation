#!/bin/bash

# export CUDA_VISIBLE_DEVICES="4,5,6,7"
export PYTHONPATH=/mnt/pfs/jinfeng_team/SFT/caiguodu/workspace/projects/largescale_for_glm_series

if [ $# -ne 9 ]; then 
    echo "Usage $0 <model> <test-file> <max-length> <num-gpus> <num-beams> <do-sample> <top-p> <temperature> <answer-file>"
    exit 1
fi
md_model_path=$1
question_file=$2
max_length=$3
num_gpus=$4
num_beams=$5
do_sample=$6
top_p=$7
temperature=$8
answer_file=$9


# top_p=0.7

md_model_path=$(echo "$md_model_path" | sed 's/\/$//')
hf_model_path=${md_model_path}-hf
# output_dir=`dirname $hf_model_path`/output
# mkdir -p $output_dir
# answer_file=$output_dir/`basename $question_file .json`-`basename $md_model_path`-nb${num_beams}-ds${do_sample}-topp${top_p}-temp${temperature}.json
model_id=`basename $md_model_path`


if [ ! -f ${hf_model_path}/pytorch_model.bin ]; then 
    echo "Convert $md_model_path from megatron to huggingface."
    python /mnt/pfs/jinfeng_team/SFT/caiguodu/workspace/projects/largescale_for_glm_series/local/convert_chatglm_hf_to_mgtdp/convert.py --md-model $md_model_path --hf-model $hf_model_path || exit 1
fi

if [ ! -f $answer_file ]; then 
    python ./test_glm6b.py \
        --model-id $model_id \
        --model-path $hf_model_path \
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
    python `dirname $question_file`/eval.py --inf-file $answer_file
fi

