#syl2char测试集
音节转汉字测试集
#测试集说明
text字段是输入模型的音节序列
ori_answer是音节对应的汉字标注序列
gen_answer是模型预测的结果
#测试CER指标代码
python calculate_cer.py
