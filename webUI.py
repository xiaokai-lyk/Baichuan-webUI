# -*- coding: utf-8 -*-
# @Time : 2024/1/13 19:43
# @Author : 小锴(xiaokai or XK)

from email import message
import gradio as gr
import time
import copy
import config

modelLoaded=False
if config.systemPrompt==None:
    initial_messages = [{"role": "system", "content":"尽量满足我的所有要求，用{}来回答我的问题".format(config.language) }]
else:
    initial_messages = [{"role": "system", "content":str(config.systemPrompt) }]
messages = initial_messages
botAnswer=""
tryReload=0


def predictSettingChange(choice):
    if choice == "标准":
        return gr.update(visible=False)
    elif choice == "自定义":
        return gr.update(visible=True)
    elif choice == "灵感大爆炸":
        raise gr.Error("???")
    else :
        raise gr.Error("未知参数,未知的推理设置:"+str(choice))
def UISettingChange(choice):
    if choice == "标准":
        return gr.update(height=300)
    elif choice == "禅定模式":
        return gr.update(height=600)
def UISettingChangeForRadio(choice,now):
    if choice == "禅定模式":
        return gr.update(value="标准")
    else:
        return gr.update(value=now)

def loadModel():
    global modelLoaded
    global model
    global tokenizer
    if modelLoaded==False:
        modelLoaded=True    #先锁住加载模型的按钮,防止连续点击导致问题
        gr.Info("正在加载模型,可能会耗时较久,请不要着急...")
        gr.Info("正在导入库...")
        import os
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer,GenerationConfig
        from config import model_dir,load_in_4bit
        gr.Info("正在加载模型...")
        modelPath=str(os.path.abspath('.')+model_dir)
        tokenizer = AutoTokenizer.from_pretrained(modelPath, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(modelPath, device_map="cuda:0", trust_remote_code=True, torch_dtype=torch.float16,task='text-generation', load_in_4bit=load_in_4bit,)
        model.generation_config=GenerationConfig(pad_token_id= 0,  bos_token_id= 1,  eos_token_id= 2,  user_token_id= 195,  assistant_token_id= 196)
        gr.Info("模型加载成功！")
    else:
        raise gr.Error("模型已经加载过了，不能重复加载")

def reload():
    global modelLoaded
    global model
    global tryReload
    if modelLoaded==False:
        raise gr.Error("您还没有试着加载过呢,不是所有折翼坠落的鹰，都能腾空而起，但如果不试试，那就永远碰不到天空(来源GI,侵删)")
    if tryReload<=3:
        gr.Info("为了确保您不是误触,请再次点击{}次重新加载按钮以继续".format(3-tryReload))
        tryReload+=1
        return
    else :
        tryReload=0
        gr.Info("正在强制重新加载...")
        gr.Warning("强制重新加载了模型")
        modelLoaded=False
        loadModel()

def predict(question,historyMessage,maxNewTokens,minNewTokens,mode,temperature,top_p,presencePenalty,frequencyPenalty):
    try:
        global model
        global messages
        global initial_messages
        global botAnswer
        global tokenizer
        if(len(historyMessage) == 0):
            messages=copy.deepcopy(initial_messages)
        messages.append({"role": "user", "content":question})
        from transformers import GenerationConfig
        if mode=="标准":
            generation_config=GenerationConfig(pad_token_id= 0,  bos_token_id= 1,  eos_token_id= 2,  user_token_id= 195,  assistant_token_id= 196,  max_new_tokens=2048,  temperature= 0.3,  top_p= 0.85,  repetition_penalty= 1.05,  do_sample= True)
            response = model.chat(tokenizer=tokenizer,messages=messages,generation_config=generation_config,stream=True)
        elif mode=="自定义":
            generation_config=GenerationConfig(pad_token_id= 0,  bos_token_id= 1,  eos_token_id= 2,  user_token_id= 195,  assistant_token_id= 196,  max_new_tokens=maxNewTokens,min_new_tokens= minNewTokens,  temperature= float(temperature),  top_p= 0.85,  repetition_penalty= 1.05,  do_sample= True,presence_penalty=presencePenalty,frequency_penalty=frequencyPenalty)
            response = model.chat(tokenizer=tokenizer,messages=messages,generation_config=generation_config,stream=True)
        else:
            raise gr.Error("推理设置应为“标准”或“自定义”而不是"+str(mode))
        for text in response:
            tempHis=copy.deepcopy(historyMessage)
            tempHis.extend([[question,text]])
            yield tempHis
        messages.append({"role": "assistant", "content":text})
        #print(str(response))
    except Exception as e:
        e=str(e)
        if e=="name 'model' is not defined":
            raise gr.Error("模型未加载")
        else:
            raise gr.Error("未知错误"+str(e))

def saveHis(mode,maxNewTokens,minNewTokens,predictMode,temperature,top_p,presencePenalty,frequencyPenalty):
    if mode=="保存为TXT":
        try:
            import json
            filname="saves/chatHisText{}.txt".format(str(time.strftime('%Y-%m-%d-%H%M%S', time.localtime())))
            open(filname,'w').write(json.dumps( messages,indent =4,ensure_ascii=False))
            gr.Info("已保存到{}中".format(filname))
        except Exception as e:
            raise gr.Error("保存时出错"+str(e))
    elif mode=="保存为对话记录":
        try:
            import json
            filname="saves/chatHistory{}.chatHistory".format(str(time.strftime('%Y-%m-%d-%H%M%S', time.localtime())))
            file=open(filname,'wb')
            predictSettingDict = {'maxNewTokens':maxNewTokens,
                                'minNewTokens': minNewTokens, 
                                'predictMode': predictMode, 
                                'temperature': temperature,
                                'top_p': top_p,
                                'presencePenalty': presencePenalty,
                                'frequencyPenalty': frequencyPenalty
                                }
            import hashlib
            md5Method=hashlib.md5("fatCowIsCute".encode(encoding='gbk'))
            md5Method.update(str(messages).encode(encoding='gbk'))
            md5=md5Method.hexdigest()
            data = {'version':config.version,'text':messages,'setting':predictSettingDict,'md5':md5}
            data=json.dumps(data)
            file.write(data.encode(encoding='gbk'))
            gr.Info("已保存到{}中".format(filname))
        except Exception as e:
            raise gr.Error("保存时出错"+str(e))
    else:
        raise gr.Error("无效的参数")


def loadHis(filePath):
    global messages
    import json
    f=open(filePath,'r')
    data=json.loads(f.read())
    messagesFromFile=data['text']
    targetMd5=data['md5']
    setting=data['setting']
    import hashlib
    md5Method=hashlib.md5("fatCowIsCute".encode(encoding='gbk'))
    md5Method.update(str(messages)+str(predictSettingDict).encode(encoding='gbk'))
    md5=md5Method.hexdigest()
    if str(targetMd5)=="SKIP":
        messages=messagesFromFile
        predictSetting
        gr.Info("已加载未经校验的对话记录")
        gr.Warning("已加载未经校验的对话记录")
    if str(md5)==str(targetMd5):
        message==messagesFromFile
        gr.Info("加载成功")
    else:
        gr.Info("文件校验未通过,它可能已经损坏")
        gr.Info("将文件中的“MD5”部分的值改为 SKIP 以跳过文件校验")
        gr.Info("不建议这样做,除非你相信这个文件是“好的”")
    

with gr.Blocks() as demo:
    gr.Markdown("# 百川2(Baichuan2)webUI启动器")
    with gr.Row():
        chatbot = gr.Chatbot(
            height=300,
            scale=3
        )
    with gr.Blocks():
        msg = gr.Textbox(
            lines=3,
            label="问题",
            placeholder="Enter键换行，发送点右边按钮",
            info="请不要快速发送或者在加载模型时发送,可能会出问题"
        )
        with gr.Row():
            submitButton=gr.Button(
                "发送",
                variant="primary"
            )
            clearButton=gr.ClearButton(
                components=[msg,chatbot],
                value="清除",
                variant="stop"
            )
    with gr.Row():
        save=gr.Button(
                "保存为TXT",
            )
        
        save2=gr.Button(
                "保存为对话记录",
            )

        loadButton=gr.UploadButton("加载对话记录")


    with gr.Row():
        #predictSetting = gr.Radio(["标准", "自定义", "灵感大爆炸"], label="推理参数设置", value="标准",interactive=True)
        predictSetting = gr.Radio(["标准", "自定义"], label="推理参数设置", value="标准",interactive=True)
        UISetting = gr.Radio(["标准", "禅定模式"], label="UI设置", value="标准",interactive=True)
    with gr.Row():
        maxLength=gr.Slider(0, 10240,step=1,label="最大长度",value=1024,interactive=True)
        minLength=gr.Slider(0, 10240,step=1,label="最小长度",interactive=True)
    with gr.Row():
        temperature=gr.Slider(0, 2,step=0.01,value=1,label="temperature",interactive=True,visible=False)
        top_p=gr.Slider(0, 1,step=0.01,value=0.3,label="top_p",interactive=True,visible=False)
        presencePenalty=gr.Slider(0, 2,step=0.01,value=1,label="Presence Penalty",interactive=True,visible=False)
        frequencyPenalty=gr.Slider(0, 2,step=0.01,label="Frequency Penalty",interactive=True,visible=False)
        predictSetting.change(fn=predictSettingChange, inputs=predictSetting, outputs=maxLength)
        predictSetting.change(fn=predictSettingChange, inputs=predictSetting, outputs=minLength)
        predictSetting.change(fn=predictSettingChange, inputs=predictSetting, outputs=temperature)
        predictSetting.change(fn=predictSettingChange, inputs=predictSetting, outputs=top_p)
        predictSetting.change(fn=predictSettingChange, inputs=predictSetting, outputs=presencePenalty)
        predictSetting.change(fn=predictSettingChange, inputs=predictSetting, outputs=frequencyPenalty)
        UISetting.change(fn=UISettingChange, inputs=UISetting, outputs=chatbot)
        UISetting.change(fn=UISettingChangeForRadio, inputs=[UISetting,predictSetting], outputs=predictSetting)
    with gr.Row():
        load_button=gr.Button("加载模型")
        reload_button=gr.Button("强制重新加载模型")
    load_button.click(loadModel)
    reload_button.click(reload)
    gr.Examples(examples=[
            ["CUDA是什么","标准"],
            ["f(x)为偶函数， f(1) = 3, f(2) = 4, 那么f(1) + f(-2) ^2 等于多少？ 请一步一步说明","标准"],
            ["写一篇主题为《校园生活》的文章的框架，200字左右。列出大纲和部分主要情节","标准"]
        ],
            inputs=[msg,predictSetting]
            )
    

    save.click(saveHis,[save,maxLength,minLength,predictSetting,temperature,top_p,presencePenalty,frequencyPenalty])
    save2.click(saveHis,[save2,maxLength,minLength,predictSetting,temperature,top_p,presencePenalty,frequencyPenalty])
    loadButton.upload(loadHis,loadButton)
    submitButton.click(predict, [msg,chatbot,maxLength,minLength,predictSetting,temperature,top_p,presencePenalty,frequencyPenalty], [chatbot])
    gr.Markdown("""
## **免责声明与安全警告:**
        
1.模型所有权由百川智能所有，您在使用时须遵守[《Baichuan2模型社区许可协议》](https://modelscope.cn/models/baichuan-inc/Baichuan2-7B-Base/file/view/master/Baichuan%202%E6%A8%A1%E5%9E%8B%E7%A4%BE%E5%8C%BA%E8%AE%B8%E5%8F%AF%E5%8D%8F%E8%AE%AE.pdf) 请您仔细阅读并理解该协议内容。若本条款与《Baichuan2模型社区许可协议》有冲突，以《Baichuan2模型社区许可协议》为准
        
2.本代码系开源模型工具，由于NLP模型的技术特性，模型可能会输出不正确的或有害的内容，模型生成的内容不应作为用户判断的唯一依据，用户因参考模型生成的内容造成损失的，**作者不承担任何法律责任**。

3.**若您继续使用，视为您已经完整阅读、准确理解并自愿接受以上条款、文件中附带的许可证文件(licenses.txt)及《Baichuan2模型社区许可协议》的全部内容，并保证您的使用行为遵守中华人民共和国的相关法律法规。**

4.根据许可证文件(licenses.txt)中的内容，您需要确保您的行为其规定，如**分发时一定要提供源码**，**不能收专利许可费费用**，**不能再授权**等(此段解释不具有法律效力，请以GPLv3许可证为准)

百川2(Baichuan2)webUI启动器 Copyright (C) 2024 小锴小锴(BilibiliUID:1740338174)
                """)
if __name__ == "__main__":
    while True:
        try:
            demo.queue(api_open=False,max_size=config.max_size) 
            if config.host=="auto":
                import socket
                config.host=socket.gethostbyname(socket.gethostname())
            demo.launch(show_api=False,share=config.share,server_name=config.host)
        except Exception as e:
            while True:
                print("error:"+str(e))
                cmd=input("input command")
                if cmd=="reset":
                    break
                elif cmd=="exit":
                    raise KeyboardInterrupt
                else :
                    print("Unknow cmd. It should be [reset or exit]")
