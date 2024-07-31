input_json_file=$1
out_path=$2
tokennizer=icetk-glm-130B
split_ratio=1.0

python dumper/process_130B_data.py --input ${input_json_file} --tokenizer-type ${tokennizer} --output-prefix ${out_path} --split_ratio ${split_ratio}