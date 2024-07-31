export PYTHONPATH=/tal-vePFS/SFT/zhangshusheng/codes/LargeScale.lcl
# inputfile=/tal-vePFS/SFT/gaoshaojun/jiaoyan/jiaoyanyun_math/tmp.jsonl
inputfile=$1
# outprefix=/tal-vePFS/SFT/gaoshaojun/sft_data_engine/data_preprocess/dumper/tmp/tmp_1000
outprefix=$2
python dumper/preprocess_data_latex_yuanye.py --input ${inputfile}  \
    --output-prefix ${outprefix} --json-keys data --tokenizer-type IceTokenizer --store-int32 --length-per-sample 2048 --concat-sequence --encode-multitask --reserve-tokens 48