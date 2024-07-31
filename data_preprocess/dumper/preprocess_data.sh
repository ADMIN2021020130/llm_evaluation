#!/bin/bash

# if [ $# -ne 1 ]; then
#   echo "Usage: $0 <data-file>"
#   echo "egs: $0 data/alpaca-hh-tang-zh/alpaca-hh-tang-zh.json"
#   exit 1
# fi 
data=$1
# prefix=`basename $data .json`
prefix=$2
outputdir=$3
task=$4
gmask_pos=$5
tokennizer=ChatGLMTokenizer

mkdir -p $outputdir

if [ $task = "sft" ]; then
  # python tools/preprocess_data_sft.py \
  python dumper/preprocess_data_sft_for_chatglm6b.py \
       --input ${data} \
       --gmask-pos ${gmask_pos} \
       --output-prefix ${outputdir}/${prefix} \
       --tokenizer-type ${tokennizer} 
elif [ $task = "pretrain" ]; then
  python dumper/preprocess_data_pretrain.py \
       --input ${data} \
       --output-prefix ${outputdir}/my-chatglm \
       --tokenizer-type ${tokennizer} 
else
  echo "Unvalid task name"
fi 
