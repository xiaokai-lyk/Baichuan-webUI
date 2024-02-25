model_dir='/models/Baichuan2-7B-Chat-4bits'   #模型文件地址(不建议修改)
load_in_4bit=True  #4-bit量化(13B模型:12G以下显存开启,7B模型：8G以下显存开启)
max_size=None #最大线程数(若<4可能会有问题)
share=False
systemPrompt="Answer step by step"
language=""#若systemPromat为None则直接嵌入到系统提示词模板中
host="127.0.0.1"

#今天你三连了吗~~



'''
下方是固定参数，不要动
'''
version='v1.0'