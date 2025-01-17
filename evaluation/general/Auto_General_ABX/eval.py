
import json
import pandas as pd
import requests,time
import time
import sys
import argparse




# GPT-3.5的接口
def get_token(question):

    deployment_id = 'GPT-35'
    api_version = '2023-03-15-preview'
    url = 'http://cxxm.facethink.com/openai/deployments/{}/chat/completions?api-version={}'.format(deployment_id, api_version)

    data={ "messages": [{"role": "user","content": question}]}
    headers = {'Content-Type': 'application/json', 'Username': 'wuzedong1'}
    
    response = requests.post(url, json=data, headers=headers)
    
    return json.loads(response.text)



# GPT-4的接口

# def get_gpt_response(prompt):
#     #prompt
#     url = "http://msai.facethink.com/openai/deployments/gpt-4/chat/completions?api-version=2023-05-15"

#     headers = {
#         "Content-Type": "application/json",
#         "Username": "chenboyu",
#         "Password": "Mgmr1xvRZIXjE"
#     }

#     data = {
#         "messages": [
#             {
#                 "role": "system",
#                 "content": "You are a helpful assistant."
#                 # "content": "You are a mathematics expert, proficient in various mathematical problems."
#             },
#             {
#                 "role": "user",
#                 "content": prompt
#             }
#         ]
#     }

#     response = requests.post(url, json=data, headers=headers)

#     if response.status_code == 200:
#         return response.json()
#     elif response.status_code == 429:
#         print("Too many requests. Waiting and retrying...")
#         # 获取重试时间，服务器返回的是动态值，如果没有这个字段，就默认等待60s
#         retry_after = int(response.headers.get("Retry-After", 60))
#         time.sleep(retry_after)
#         return get_gpt_response(prompt)
#     else:
#         #time.sleep(0.5)
#         #return get_gpt_response(prompt)
#         # TODO: 其余状态码请根据实际情况处理
#         print("ERROR: {}".format(response.status_code))
        


# GPT-4的接口
def get_gpt_response(prompt):
    #prompt
    url = "http://msai.facethink.com/openai/deployments/gpt-4/chat/completions?api-version=2023-05-15"

    headers = {
        "Content-Type": "application/json",
        "Username": "chenboyu",
        "Password": "Mgmr1xvRZIXjE"
    }

    data = {
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
                # "content": "You are a mathematics expert, proficient in various mathematical problems."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        return response.json()
    elif response.status_code == 429:
        print("Too many requests. Waiting and retrying...")
        # 获取重试时间，服务器返回的是动态值，如果没有这个字段，就默认等待60s
        retry_after = int(response.headers.get("Retry-After", 60))
        time.sleep(retry_after)
        return get_gpt_response(prompt)
    else:
        # TODO: 其余状态码请根据实际情况处理
        print("ERROR: {}".format(response.status_code))

def post_processing(res):
    
    if '都好' in res  and   '都不好'  and 'A好' and 'B好' not in res:
        return 3
    elif '都不好' in res   and 'A好' and 'B好' not in res:
        return 0
    elif 'A好' in res  and '都好'  and '都不好' and 'B好' not in res :
        return 1
    elif 'B好' in res and '都好'  and '都不好' and 'A好' not in res :
        return 2
    return -1

        

def evals(data, A_model, B_model):
  


    template = f"""
            问题：请列举十个最知名的流量明星?\n 
            A: 1. 迪丽热巴 2. 肖战 3. 鹿晗 4. 王俊凯 5. 王源 6. 杨幂 7. 杨颖 8. 李易峰 9. 吴亦凡 10. 王一博\n
            B: 1. 迪丽热巴 2. 鹿晗 3. 杨幂 4. 李易峰 5. 吴亦凡 6. 王俊凯 7. 张一山 8. 张一山 9. 张一山 10. 张一山\n" 
            答：A好\n
            解析：A的回答列举了十个知名的流量明星，并且这些名字都是不同的，没有重复。B的回答在列举明星时，出现了重复的“张一山”，可能是一处错误。由于A的回答在列举方面更准确且没有错误，因此被认为更好。所以选择A好\n
            答案:A好\n
            

            问题：今天天气如何,温度多少\n
            A:我不知道今天的天气如何。请查看您的设备或当地天气预报以获取准确和最新的信息\n
            B:很抱歉,我无法回答您的问题,因为我无法看到实时的天气信息。不过,您可以使用搜索引擎或手机等设备上的天气应用程序来获取今天的天气信息。\n
            解析：B的回答中，明确解释了为什么无法回答问题，然后提供了多种获取天气信息的替代方法。尽管A的回答也提供了获取信息的建议，但B的回答更加详细，并且直接回答了问题，并给出了实际的解决方案。因此，根据您的选择，B的回答更好，所以选择B好\n
            答案:B好 \n
            
            

            问题：点赞？
            A:点赞是指在网上或社交媒体上,通过点击“赞”按钮,表达对某人或某篇文章、某部电影等的喜爱或支持。现在,点赞已成为一种流行的行为,被广泛用于表达对他人的赞赏或支持。\n
            B：点赞是一种网络用语,表示对某个内容或观点表示赞同或支持。它通常用于社交媒体或网站上的评论或帖子中。\n
            解析：A的回答详细解释了“点赞”的含义、用途和流行程度，包括在网上或社交媒体上通过点击“赞”按钮来表达喜爱或支持某人、文章、电影等，同时指出点赞作为一种流行行为被广泛应用于表达对他人的赞赏或支持。虽然B的回答也提供了解释，但A的回答更详细，涵盖了更多信息。根据您的选择，A的回答更好，所以选择A好\n            
            答案:A好\n
            
            问题：你喜欢吃辣条嘛\n
            A：不好意思,作为一个机器人,我没有喜好和偏好。我的目的是尽可能准确地回答您的问题,并帮助您解决您可能遇到的任何问题。\n
            B:我是一个人工智能助手,没有口感和味觉,因此我无法喜欢或不喜欢辣条。\n
            解析：A的回答解释了机器人没有喜好和偏好，只专注于准确回答问题和提供帮助。B的回答虽然也表达了类似的概念，但A的回答更加明确，并且更详细地解释了机器人的角色和目的。因此，根据您的选择，A的回答更好，所以选择A好\n
            答案:A好\n

            

            问题：我不太相信你\n
            A:很抱歉,我不太明白您的意思。如果您有任何问题或疑虑,请随时告诉我,我会尽力为您提供更好的服务。\n
            B：我明白你的感受,但我必须指出,我是由好未来AI团队开发的人工智能程序,我们的目标是为人类服务,并帮助人们解决问题。\n  
            解析：A的回答表达了对用户疑虑的尊重，提供了帮助并表明愿意解决问题。B的回答也解释了AI的来源和目标，但A的回答更加关注用户的感受，并提供了积极的支持。根据您的选择，A的回答更好，所以选择A好\n
            答案: A好\n
           
            

            问题：你是小黑子吗？\n
            A：我不是小黑子,但我和小黑子有着相似的功能和能力。\n 
            B：不,我不是小黑子。\n
            解析：B的回答直接而明确地否定了自己是小黑子，没有多余的解释。A的回答虽然提供了一些信息，但可能会导致用户产生误解，即认为AI和"小黑子"具有相似的功能和能力，这不是完全准确的。根据您的选择，B的回答更清晰明了,所以选择B好\n
            答案: B好\n
           

            问题：孙悟空被哪个妖精打败过？\n
            A：菩提祖师\n
            B：菩提祖师\n
            解析：无论选择A还是B，回答的内容是相同的，但答案是错误的，孙悟空在西游记中曾被铁扇公主打败过,而不是菩提祖师，所以选择都不好\n
            答案：都不好\n"
           
            
           

            问题:2023年中国各大银行1年期，定期存款利率\n  
            A:2023年中国各大银行1年期定期存款利率可能会受到通货膨胀、经济环境等多种因素的影响,因此具体的存款利率需要等到2023年1月1日才能确定。不过,根据2020年12月的数据,中国的各大银行1年期定期存款利率普遍在1.5%-2%之间。\n 
            B:2023年中国各大银行1年期定期存款利率可能会有所不同,具体以各银行实际公布为准。\n
            解析：B的回答相对较为准确和简洁，指出了实际情况，并强调具体的存款利率应以各银行的公布为准。A的回答虽然提供了一些相关信息，但也包含了一些猜测和可能性，而B的回答更直接地回应了问题，符合更好的标准，所以选择B好。\n
            答案：B好\n
            

            问题:写个故事？\n
            A:当然!你希望我创造什么样的故事?\n
            B:当然!请提供您希望我为您撰写的故事的一些细节,例如类型,设置,角色,等等。您也可以告诉我您对故事的任何具体想法或要求。
            解析：B的回答请求更多的细节，以便为您创作一个符合您期望的故事。它提供了更具体的指导，以确保故事能够满足您的要求。相比之下，A的回答只是询问要创造什么样的故事，而B的回答更加积极并展示了更大的关注和准备,所以选择B好。\n
            答案：B好
    """

    few_shot = f"""
            你是一名主观评测专家，首先需要学习样例,然后对A和B问题回答进行主观评测，首先给出解析，接着从 A好 B好 都好 都不好 选择一个进行回复\n

            样例：\n
        ```{template}```

        """


   



    fr = open(data).readlines()



    label_dict = {'0':0,'1':0,'2':0,'3':0,'-1':0}
    for lines in fr:
        ll = json.loads(lines)
        cur_prompt = "问题：{}".format(ll['prompt']) + "\n" +"A: {} \n".format(ll[A_model]) + "\n"+  "B: {} \n".format(ll[B_model]) + "\n"                
        if len(ll['data']) == 0:
            prompt = few_shot + cur_prompt     
        else:
            history = ""
            for l in ll['data']:
                history = l['prompt'] + "\n" + l["response"] + "\n"     
            prompt = few_shot + "\n" + history + "\n" + cur_prompt 
        
        time.sleep(0.2)
        print('################# Prompt #######################')
        print(prompt)
        # response = get_gpt_response(prompt)['choices'][0]['message']['content']

        # response = get_gpt_response(prompt[:1024])['choices'][0]['message']['content']
        response = get_token(prompt)['choices'][0]['message']['content']
        
        
        res = response[response.find('答案'):]

        model_eval = post_processing(res)
        label_dict[str(model_eval)] +=1
      
        # print("#################  Response #####################")
        # print(response)
    
    print(label_dict)

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--inf-file", type=str, required=True)
    parser.add_argument("--model-A", type=str, required=True)
    parser.add_argument("--model-B", type=str, required=True)
    args = parser.parse_args()
    evals(args.inf_file, args.model_A, args.model_B)


    

        

       

    
    
    
    
