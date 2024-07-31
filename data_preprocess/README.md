# 用来准备large scale或 GLM 的训练数据

可以根据config（yaml）从不同数据来源中采样样本，进行清洗，混合成训练数据。

config模版可以参考 config/demo.yaml进行修改

使用方法：python data_preprocessor.py config/demo.yaml
生成的文件在：tmp/ 中
需要注意dumper/megatron 需要软连接到large_scale里面

TODO:
1. 支持多进程large scale tokenize（重要）
2. 支持pretrain方式的tokenize（目前只支持sft）
3. 支持glm_history格式的dump