import json
import os
import sys
import re
import random
from typing import Union
import shortuuid
from decimal import Decimal

OPRATORS_TO_WORD = {"+": "Addition", "-": "Subtraction", "*":"Multiplication", "/":"Division"}

PROMPT_PREFIX = [
    "",
    "计算",
    "帮我计算",
    "计算一下",
    "算一下",
    "告诉我",
]

PROMPT_POSTFIX = [
    "",
    "=",
    "=?",
    "等于？",
    "等于多少？",
    "的答案？",
    "的答案是？",
    "的答案是多少？",
    "的答案是什么？",
    "的结果？",
    "的结果是？",
    "的结果多少？",
    "的结果什么？",
]

RESPONSE_PREFIX_WITH_PROMPT = [
    "=",
    "等于",
    "的结果：",
    "的结果是",
    "的答案：",
    "的答案是",
]

RESPONSE_PREFIX_NO_PROMPT = [
    "",
    "等于",
    "结果：",
    "结果是",
    "答案：",
    "答案是",
]

def template_prompt():
    template = []
    for i, prefix in enumerate(PROMPT_PREFIX):
        for j, postfix in enumerate(PROMPT_POSTFIX):
            tmp = [prefix + "{prompt}" + postfix]
            if i==0 and (j==0 or j==1):
                tmp = [prefix + "{prompt}" + postfix] * 20
            template.extend(tmp)
    return template
    

def get_data_format(id="", prompt="", input="", response="", from_type="", domain=""):
    if type(domain) != list:
        domain = [domain]
    data_format = {
        "id": id,
        "data":[{
            "prompt": str(prompt),
            "input": str(input),
            "response": [[str(response), str(from_type)]],
        }],
        "domain": domain,
    }
    if data_format["id"] == "":
        data_format["id"] = shortuuid.uuid(name=str(data_format["data"]))
    return data_format

def Addition(datatype="train"):
    # Addition up to 16 digits
    n = 1
    if datatype == "valid" or datatype == "test":
        n = 100
    pairs = \
        [(random.randint(10**(i-1), 10**i), random.randint(10**(j-1), 10**j)) for i in range(1,16) for j in range(i,16) for k in range(int(1000/n))] +\
        [(random.randint(10**(i-1), 10**i), random.randint(10**(j-1), 10**j)) for i in range(3,16) for j in range(i,16) for k in range(int(1000/n))] +\
        [(random.randint(10**(i-1), 10**i), random.randint(10**(j-1), 10**j)) for i in range(6,16) for j in range(i,16) for k in range(int(1000/n))] +\
        [(random.randint(10**(i-1), 10**i), random.randint(10**(j-1), 10**j)) for i in range(9,16) for j in range(i,16) for k in range(int(1000/n))] +\
        [(random.randint(10**(i-1), 10**i), random.randint(10**(j-1), 10**j)) for i in range(12,16) for j in range(i,16) for k in range(int(1000/n))] 

    random.shuffle(pairs)

    print("Addition:", len(pairs))

    data_add = []
    for num1, num2 in pairs:
        if random.random()<0.5:
            num1, num2 = num2, num1 
        answer = num1 + num2

        question = f"{num1} + {num2}" 
        output = f"{num1} + {num2} = {answer}"
        assert(output.split()[-1] == str(answer))

        data_add.append(get_data_format(prompt=question, response=answer, from_type="self-generate", domain=["Math", "Addition"]))
    return data_add

def Addition_2d():
    # Addition within 2 digits
    pairs = \
    [(i, j) for i in range(0, 100) for j in range(0, 100)]

    print("Addition:", len(pairs))

    data_add = []
    for num1, num2 in pairs:
        answer = num1 + num2

        question = f"{num1} + {num2}" 
        output = f"{num1} + {num2} = {answer}"
        assert(output.split()[-1] == str(answer))

        data_add.append(get_data_format(prompt=question, response=answer, from_type="self-generate", domain=["Math", "Addition"]))
    return data_add

def Addition_neg(datatype="train"):
    # # Addition within 2 digits
    # pairs = \
    # [(i, j) for i in range(0, 100) for j in range(0, 100)]

    # Addition up to 16 digits
    n = 1
    if datatype == "valid" or datatype == "test":
        n = 100
    pairs = \
        [(random.randint(10**(i-1), 10**i), random.randint(10**(j-1), 10**j)) for i in range(1,16) for j in range(i,16) for k in range(int(1000/n))] +\
        [(random.randint(10**(i-1), 10**i), random.randint(10**(j-1), 10**j)) for i in range(3,16) for j in range(i,16) for k in range(int(1000/n))] +\
        [(random.randint(10**(i-1), 10**i), random.randint(10**(j-1), 10**j)) for i in range(6,16) for j in range(i,16) for k in range(int(1000/n))] +\
        [(random.randint(10**(i-1), 10**i), random.randint(10**(j-1), 10**j)) for i in range(9,16) for j in range(i,16) for k in range(int(1000/n))] +\
        [(random.randint(10**(i-1), 10**i), random.randint(10**(j-1), 10**j)) for i in range(12,16) for j in range(i,16) for k in range(int(1000/n))] 

    random.shuffle(pairs)

    print("Addition_neg:", len(pairs))

    data_add = []
    for num1, num2 in pairs:
        if random.random()<0.33:
            if random.random()<0.5:
                num1, num2 = num2, num1 
            num1 = -1 * num1
            answer = num1 + num2
            if random.random()<0.3:
                question = f"({num1}) + {num2}"
                output = f"({num1}) + {num2} = {answer}"
            else:
                question = f"{num1} + {num2}"
                output = f"{num1} + {num2} = {answer}"
            assert(output.split()[-1] == str(answer))
            data_add.append(get_data_format(prompt=question, response=answer, from_type="self-generate", domain=["Math", "Addition_neg"]))
        elif 0.33<=random.random()<0.63:
            if random.random()<0.5:
                num1, num2 = num2, num1 
            num2 = -1 * num2
            answer = num1 + num2
            question = f"{num1} + ({num2})"
            output = f"{num1} + ({num2}) = {answer}"
            assert(output.split()[-1] == str(answer))
            data_add.append(get_data_format(prompt=question, response=answer, from_type="self-generate", domain=["Math", "Addition_neg"]))
        else:
            if random.random()<0.5:
                num1, num2 = num2, num1 
            num1 = -1 * num1
            num2 = -1 * num2
            answer = num1 + num2
            if random.random()<0.3:
                question = f"({num1}) + ({num2})" 
                output = f"({num1}) + ({num2}) = {answer}"
            else:
                question = f"{num1} + ({num2})" 
                output = f"{num1} + ({num2}) = {answer}"
            assert(output.split()[-1] == str(answer))
            data_add.append(get_data_format(prompt=question, response=answer, from_type="self-generate", domain=["Math", "Addition_neg"]))

    return data_add

def Addition_decimal(datatype="train"):
    n = 1
    if datatype == "valid" or datatype == "test":
        n = 100
    num_digits1 = 6
    num_digits = 10
    power = 10
    pairs = \
        [(random.randint(10**(i-1), 10**i)/10**power, random.randint(10**(j-1), 10**j)/10**power) for i in range(1,num_digits1) for j in range(i,num_digits1) for power in range(1,num_digits1) for k in range(int(1000/n))] +\
        [(random.randint(10**(i-1), 10**i)/10**power, random.randint(10**(j-1), 10**j)/10**power) for i in range(2,num_digits1) for j in range(i,num_digits1) for power in range(1,num_digits1) for k in range(int(1000/n))] +\
        [(random.randint(10**(i-1), 10**i)/10**power, random.randint(10**(j-1), 10**j)/10**power) for i in range(3,num_digits1) for j in range(i,num_digits1) for power in range(1,num_digits1) for k in range(int(1000/n))] +\
        [(random.randint(10**(i-1), 10**i)/10**power, random.randint(10**(j-1), 10**j)/10**power) for i in range(4,num_digits1) for j in range(i,num_digits1) for power in range(1,num_digits1) for k in range(int(1000/n))] +\
        [(random.randint(10**(i-1), 10**i)/10**power, random.randint(10**(j-1), 10**j)/10**power) for i in range(5,num_digits1) for j in range(i,num_digits1) for power in range(1,num_digits1) for k in range(int(1000/n))] +\
        [(random.randint(10**(i-1), 10**i)/10**power, random.randint(10**(j-1), 10**j)/10**power) for i in range(1,num_digits) for j in range(i,num_digits) for power in range(1,num_digits) for k in range(int(200/n))] +\
        [(random.randint(10**(i-1), 10**i)/10**power, random.randint(10**(j-1), 10**j)/10**power) for i in range(3,num_digits) for j in range(i,num_digits) for power in range(1,num_digits) for k in range(int(200/n))] +\
        [(random.randint(10**(i-1), 10**i)/10**power, random.randint(10**(j-1), 10**j)/10**power) for i in range(5,num_digits) for j in range(i,num_digits) for power in range(1,num_digits) for k in range(int(200/n))] +\
        [(random.randint(10**(i-1), 10**i)/10**power, random.randint(10**(j-1), 10**j)/10**power) for i in range(7,num_digits) for j in range(i,num_digits) for power in range(1,num_digits) for k in range(int(200/n))]

    random.shuffle(pairs)

    print("Addition:", len(pairs))

    data_add_dec = []
    for num1, num2 in pairs:
        if random.random() < 0.5:
            num1, num2 = num2, num1
        if random.random() < 0.25:
            answer = round(num1+num2, max(len(str(num1).split(".")[-1]), len(str(num2).split(".")[-1])))
            question = f"{num1} + {num2}" 
            output = f"{num1} + {num2} = {answer}"
            assert(float(output.split()[-1]) == answer)
            data_add_dec.append(get_data_format(prompt=question, response=answer, from_type="self-generate", domain=["Math", "Addition_decimal"]))
        elif 0.25 <= random.random() < 0.5:
            num1 = -1 * num1 
            answer = round(num1+num2, max(len(str(num1).split(".")[-1]), len(str(num2).split(".")[-1])))
            if random.random() < 0.3:
                question = f"({num1}) + {num2}" 
                output = f"({num1}) + {num2} = {answer}"
            else:
                question = f"{num1} + {num2}" 
                output = f"{num1} + {num2} = {answer}"
            assert(float(output.split()[-1]) == answer)
            data_add_dec.append(get_data_format(prompt=question, response=answer, from_type="self-generate", domain=["Math", "Addition_decimal"]))
        elif 0.5 <= random.random() < 0.75:
            num2 = -1 * num2
            answer = round(num1+num2, max(len(str(num1).split(".")[-1]), len(str(num2).split(".")[-1])))
            question = f"{num1} + ({num2})" 
            output = f"{num1} + ({num2}) = {answer}"
            assert(float(output.split()[-1]) == answer)
            data_add_dec.append(get_data_format(prompt=question, response=answer, from_type="self-generate", domain=["Math", "Addition_decimal"]))
        else:
            num1, num2 = -1 * num1, -1 * num2
            answer = round(num1+num2, max(len(str(num1).split(".")[-1]), len(str(num2).split(".")[-1])))
            if random.random() < 0.3:
                question = f"({num1}) + ({num2})" 
                output = f"({num1}) + ({num2}) = {answer}"
            else:
                question = f"{num1} + ({num2})" 
                output = f"{num1} + ({num2}) = {answer}"
            assert(float(output.split()[-1]) == answer)
            data_add_dec.append(get_data_format(prompt=question, response=answer, from_type="self-generate", domain=["Math", "Addition_decimal"]))
    return data_add_dec


def Subtraction(datatype="train"):
    # Subtraction up to 16 digits
    n = 1
    if datatype == "valid" or datatype == "test":
        n = 100
    pairs = \
        [(random.randint(10**(i-1), 10**i), random.randint(10**(j-1), 10**j)) for i in range(1,16) for j in range(i,16) for k in range(int(1000/n))] +\
        [(random.randint(10**(i-1), 10**i), random.randint(10**(j-1), 10**j)) for i in range(3,16) for j in range(i,16) for k in range(int(1000/n))] +\
        [(random.randint(10**(i-1), 10**i), random.randint(10**(j-1), 10**j)) for i in range(6,16) for j in range(i,16) for k in range(int(1000/n))] +\
        [(random.randint(10**(i-1), 10**i), random.randint(10**(j-1), 10**j)) for i in range(9,16) for j in range(i,16) for k in range(int(1000/n))] +\
        [(random.randint(10**(i-1), 10**i), random.randint(10**(j-1), 10**j)) for i in range(12,16) for j in range(i,16) for k in range(int(1000/n))] 

    random.shuffle(pairs)

    print("Subtraction:", len(pairs))

    data_sub = []
    for num1, num2 in pairs:
        if random.random()<0.5:
            num1, num2 = num2, num1 
        answer = num1 - num2
        
        question = f"{num1} - {num2}" 
        output = f"{num1} - {num2} = {answer}"
        assert(output.split()[-1] == str(answer))

        data_sub.append(get_data_format(prompt=question, response=answer, from_type="self-generate", domain=["Math", "Subtraction"]))
    return data_sub

def Subtraction_neg(datatype="train"):
    # Subtraction up to 16 digits
    n = 1
    if datatype == "valid" or datatype == "test":
        n = 100
    pairs = \
        [(random.randint(10**(i-1), 10**i), random.randint(10**(j-1), 10**j)) for i in range(1,16) for j in range(i,16) for k in range(int(1000/n))] +\
        [(random.randint(10**(i-1), 10**i), random.randint(10**(j-1), 10**j)) for i in range(3,16) for j in range(i,16) for k in range(int(1000/n))] +\
        [(random.randint(10**(i-1), 10**i), random.randint(10**(j-1), 10**j)) for i in range(6,16) for j in range(i,16) for k in range(int(1000/n))] +\
        [(random.randint(10**(i-1), 10**i), random.randint(10**(j-1), 10**j)) for i in range(9,16) for j in range(i,16) for k in range(int(1000/n))] +\
        [(random.randint(10**(i-1), 10**i), random.randint(10**(j-1), 10**j)) for i in range(12,16) for j in range(i,16) for k in range(int(1000/n))] 

    random.shuffle(pairs)

    print("Subtraction:", len(pairs))

    data_sub = []
    for num1, num2 in pairs:
        if random.random()<0.33:
            if random.random()<0.5:
                num1, num2 = num2, num1 
            num1 = -1 * num1
            answer = num1 - num2
            if random.random() < 0.3:
                question = f"({num1}) - {num2}"
                output = f"({num1}) - {num2} = {answer}"
            else:
                question = f"{num1} - {num2}"
                output = f"{num1} - {num2} = {answer}"
            assert(output.split()[-1] == str(answer))
            data_sub.append(get_data_format(prompt=question, response=answer, from_type="self-generate", domain=["Math", "Subtraction_neg"]))
        elif 0.33<=random.random()<0.63:
            if random.random()<0.5:
                num1, num2 = num2, num1 
            num2 = -1 * num2
            answer = num1 - num2
            question = f"{num1} - ({num2})"
            output = f"{num1} - ({num2}) = {answer}"
            assert(output.split()[-1] == str(answer))
            data_sub.append(get_data_format(prompt=question, response=answer, from_type="self-generate", domain=["Math", "Subtraction_neg"]))
        else:
            if random.random()<0.5:
                num1, num2 = num2, num1 
            num1 = -1 * num1
            num2 = -1 * num2
            answer = num1 - num2
            if random.random()<0.3:
                question = f"({num1}) - ({num2})" 
                output = f"({num1}) - ({num2}) = {answer}"
            else:
                question = f"{num1} - ({num2})" 
                output = f"{num1} - ({num2}) = {answer}"
            assert(output.split()[-1] == str(answer))
            data_sub.append(get_data_format(prompt=question, response=answer, from_type="self-generate", domain=["Math", "Subtraction_neg"]))
    return data_sub

def Subtraction_decimal(datatype="train"):
    # Subtraction up to 16 digits
    n = 1
    if datatype == "valid" or datatype == "test":
        n = 100
    num_digits1 = 6
    num_digits = 10
    power = 10
    pairs = \
        [(random.randint(10**(i-1), 10**i)/10**power, random.randint(10**(j-1), 10**j)/10**power) for i in range(1,num_digits1) for j in range(i,num_digits1) for power in range(1,num_digits1) for k in range(int(1000/n))] +\
        [(random.randint(10**(i-1), 10**i)/10**power, random.randint(10**(j-1), 10**j)/10**power) for i in range(2,num_digits1) for j in range(i,num_digits1) for power in range(1,num_digits1) for k in range(int(1000/n))] +\
        [(random.randint(10**(i-1), 10**i)/10**power, random.randint(10**(j-1), 10**j)/10**power) for i in range(3,num_digits1) for j in range(i,num_digits1) for power in range(1,num_digits1) for k in range(int(1000/n))] +\
        [(random.randint(10**(i-1), 10**i)/10**power, random.randint(10**(j-1), 10**j)/10**power) for i in range(4,num_digits1) for j in range(i,num_digits1) for power in range(1,num_digits1) for k in range(int(1000/n))] +\
        [(random.randint(10**(i-1), 10**i)/10**power, random.randint(10**(j-1), 10**j)/10**power) for i in range(5,num_digits1) for j in range(i,num_digits1) for power in range(1,num_digits1) for k in range(int(1000/n))] +\
        [(random.randint(10**(i-1), 10**i)/10**power, random.randint(10**(j-1), 10**j)/10**power) for i in range(1,num_digits) for j in range(i,num_digits) for power in range(1,num_digits) for k in range(int(200/n))] +\
        [(random.randint(10**(i-1), 10**i)/10**power, random.randint(10**(j-1), 10**j)/10**power) for i in range(3,num_digits) for j in range(i,num_digits) for power in range(1,num_digits) for k in range(int(200/n))] +\
        [(random.randint(10**(i-1), 10**i)/10**power, random.randint(10**(j-1), 10**j)/10**power) for i in range(5,num_digits) for j in range(i,num_digits) for power in range(1,num_digits) for k in range(int(200/n))] +\
        [(random.randint(10**(i-1), 10**i)/10**power, random.randint(10**(j-1), 10**j)/10**power) for i in range(7,num_digits) for j in range(i,num_digits) for power in range(1,num_digits) for k in range(int(200/n))]

    random.shuffle(pairs)

    print("Addition:", len(pairs))

    data_sub_dec = []
    for num1, num2 in pairs:
        if random.random() < 0.5:
            num1, num2 = num2, num1
        if random.random() < 0.25:
            answer = round(num1-num2, max(len(str(num1).split(".")[-1]), len(str(num2).split(".")[-1])))
            question = f"{num1} - {num2}" 
            output = f"{num1} - {num2} = {answer}"
            assert(float(output.split()[-1]) == answer)
            data_sub_dec.append(get_data_format(prompt=question, response=answer, from_type="self-generate", domain=["Math", "Subtraction_decimal"]))
        elif 0.25 <= random.random() < 0.5:
            num1 = -1 * num1 
            answer = round(num1-num2, max(len(str(num1).split(".")[-1]), len(str(num2).split(".")[-1])))
            if random.random() < 0.3:
                question = f"({num1}) - {num2}" 
                output = f"({num1}) - {num2} = {answer}"
            else:
                question = f"{num1} - {num2}" 
                output = f"{num1} - {num2} = {answer}"
            assert(float(output.split()[-1]) == answer)
            data_sub_dec.append(get_data_format(prompt=question, response=answer, from_type="self-generate", domain=["Math", "Subtraction_decimal"]))
        elif 0.5 <= random.random() < 0.75:
            num2 = -1 * num2
            answer = round(num1-num2, max(len(str(num1).split(".")[-1]), len(str(num2).split(".")[-1])))
            question = f"{num1} - ({num2})" 
            output = f"{num1} - ({num2}) = {answer}"
            assert(float(output.split()[-1]) == answer)
            data_sub_dec.append(get_data_format(prompt=question, response=answer, from_type="self-generate", domain=["Math", "Subtraction_decimal"]))
        else:
            num1, num2 = -1 * num1, -1 * num2
            answer = round(num1-num2, max(len(str(num1).split(".")[-1]), len(str(num2).split(".")[-1])))
            if random.random() < 0.3:
                question = f"({num1}) - ({num2})" 
                output = f"({num1}) - ({num2}) = {answer}"
            else:
                question = f"{num1} - ({num2})" 
                output = f"{num1} - ({num2}) = {answer}"
            assert(float(output.split()[-1]) == answer)
            data_sub_dec.append(get_data_format(prompt=question, response=answer, from_type="self-generate", domain=["Math", "Subtraction_decimal"]))
    return data_sub_dec


def Multiplication_n_1(datatype="train"):
    # 1xn, up to 16 digits.
    n = 1
    if datatype == "valid" or datatype == "test":
        n = 100
    pairs = \
        [(random.randint(2, 9), random.randint(10**(j-1)+1, 10**j)) for j in range(2,5) for k in range(int(4000/n))] + \
        [(random.randint(2, 9), random.randint(10**(j-1)+1, 10**j)) for j in range(5,8) for k in range(int(8000/n))] + \
        [(random.randint(2, 9), random.randint(10**(j-1)+1, 10**j)) for j in range(8,12) for k in range(int(12000/n))] + \
        [(random.randint(2, 9), random.randint(10**(j-1)+1, 10**j)) for j in range(12,17) for k in range(int(16000/n))] + \
        [(0, random.randint(10**(j-1)+1, 10**j-1)) for j in range(2,16) for k in range(int(500/n))] + \
        [(1, random.randint(10**(j-1)+1, 10**j-1)) for j in range(2,16) for k in range(int(500/n))] + \
        [(10, random.randint(10**(j-1)+1, 10**j-1)) for j in range(2,16) for k in range(int(500/n))] + \
        [(random.randint(1, 9), random.randint(1, 9)) for k in range(int(500/n))]

    random.shuffle(pairs)

    print("Multiplication nx1:", len(pairs))

    data_mul_n_1 = []
    for num1, num2 in pairs:
        if random.random() < 0.1:
            num1 = num1 * (10**random.randint(1,6))
            
        if random.random()<0.5:
            num1, num2 = num2, num1 

        answer = num1 * num2 

        question = f"{num1} * {num2}" 
        output = f"{num1} * {num2} = {answer}"

        assert(output.split()[-1] == str(answer))
        data_mul_n_1.append(get_data_format(prompt=question, response=answer, from_type="self-generate", domain=["Math", "Multiplication_n_1"]))
    return data_mul_n_1

def Multiplication_n_1_neg(datatype="train"):
    # 1xn, up to 16 digits.
    n = 1
    if datatype == "valid" or datatype == "test":
        n = 20
    pairs = \
        [(random.randint(2, 9), random.randint(10**(j-1)+1, 10**j)) for j in range(2,5) for k in range(int(800/n))] + \
        [(random.randint(2, 9), random.randint(10**(j-1)+1, 10**j)) for j in range(5,8) for k in range(int(1000/n))] + \
        [(random.randint(2, 9), random.randint(10**(j-1)+1, 10**j)) for j in range(8,12) for k in range(int(1500/n))] + \
        [(random.randint(2, 9), random.randint(10**(j-1)+1, 10**j)) for j in range(12,17) for k in range(int(2000/n))] + \
        [(0, random.randint(10**(j-1)+1, 10**j-1)) for j in range(2,16) for k in range(int(500/n))] + \
        [(1, random.randint(10**(j-1)+1, 10**j-1)) for j in range(2,16) for k in range(int(500/n))] + \
        [(10, random.randint(10**(j-1)+1, 10**j-1)) for j in range(2,16) for k in range(int(500/n))] + \
        [(random.randint(1, 9), random.randint(1, 9)) for k in range(int(500/n))]

    random.shuffle(pairs)

    print("Multiplication nx1:", len(pairs))

    data_mul_n_1 = []
    for num1, num2 in pairs:
        if random.random()<0.33:
            if random.random() < 0.1:
                num1 = num1 * (10**random.randint(1,6))
            if random.random()<0.5:
                num1, num2 = num2, num1 
            num1 = -1 * num1
            answer = num1 * num2 
            if random.random() < 0.3:
                question = f"({num1}) * {num2}" 
                output = f"({num1}) * {num2} = {answer}"
            else:
                question = f"{num1} * {num2}" 
                output = f"{num1} * {num2} = {answer}"
            assert(output.split()[-1] == str(answer))
            data_mul_n_1.append(get_data_format(prompt=question, response=answer, from_type="self-generate", domain=["Math", "Multiplication_n_1_neg"]))
        elif 0.33<=random.random()<0.63:
            if random.random() < 0.1:
                num1 = num1 * (10**random.randint(1,6))
            if random.random()<0.5:
                num1, num2 = num2, num1 
            num2 = -1 * num2
            answer = num1 * num2 
            question = f"{num1} * ({num2})" 
            output = f"{num1} * ({num2}) = {answer}"
            assert(output.split()[-1] == str(answer))
            data_mul_n_1.append(get_data_format(prompt=question, response=answer, from_type="self-generate", domain=["Math", "Multiplication_n_1_neg"]))
        else:
            if random.random() < 0.1:
                num1 = num1 * (10**random.randint(1,6))
            if random.random()<0.5:
                num1, num2 = num2, num1 
            num1 = -1 * num1
            num2 = -1 * num2
            answer = num1 * num2 
            if random.random() < 0.3:
                question = f"({num1}) * ({num2})" 
                output = f"({num1}) * ({num2}) = {answer}"
            else:
                question = f"{num1} * ({num2})" 
                output = f"{num1} * ({num2}) = {answer}"
            assert(output.split()[-1] == str(answer))
            data_mul_n_1.append(get_data_format(prompt=question, response=answer, from_type="self-generate", domain=["Math", "Multiplication_n_1_neg"]))
        
    return data_mul_n_1

def Multiplication_n_1_dec(datatype="train"):
    # 1xn, up to 16 digits.
    n = 1
    if datatype == "valid" or datatype == "test":
        n = 20
    pairs = \
        [(random.randint(2, 9), random.randint(10**(j-1)+1, 10**j)) for j in range(2,5) for k in range(int(800/n))] + \
        [(random.randint(2, 9), random.randint(10**(j-1)+1, 10**j)) for j in range(5,8) for k in range(int(1000/n))] + \
        [(random.randint(2, 9), random.randint(10**(j-1)+1, 10**j)) for j in range(8,12) for k in range(int(1500/n))] + \
        [(random.randint(2, 9), random.randint(10**(j-1)+1, 10**j)) for j in range(12,17) for k in range(int(2000/n))] + \
        [(0, random.randint(10**(j-1)+1, 10**j-1)) for j in range(2,16) for k in range(int(500/n))] + \
        [(1, random.randint(10**(j-1)+1, 10**j-1)) for j in range(2,16) for k in range(int(500/n))] + \
        [(10, random.randint(10**(j-1)+1, 10**j-1)) for j in range(2,16) for k in range(int(500/n))] + \
        [(random.randint(1, 9), random.randint(1, 9)) for k in range(int(500/n))]

    random.shuffle(pairs)

    print("Multiplication nx1:", len(pairs))

    data_mul_n_1 = []
    for num1, num2 in pairs:
        if random.random() < 0.25:
            if random.random()<0.5:
                num1, num2 = num2, num1 
            num1 = num1 / (10**(random.randint(1,6)))
            num2 = num2 / (10**(random.randint(0,10)))
            # num1 = round(num1, min(len(str(num1).split(".")[-1]), 6))
            # answer = num1 * num2 
            answer = round(num1 * num2, len(str(num1).split(".")[-1])+len(str(num2).split(".")[-1]))
            question = f"{num1} * {num2}" 
            output = f"{num1} * {num2} = {answer}"
            assert(output.split()[-1] == str(answer))
            data_mul_n_1.append(get_data_format(prompt=question, response=answer, from_type="self-generate", domain=["Math", "Multiplication_n_1_dec"]))
        if 0.25 <= random.random() < 0.5:
            if random.random()<0.5:
                num1, num2 = num2, num1 
            num1 = -num1 #-1 * num1
            num1 = num1 / (10**(random.randint(1,6)))
            num2 = num2 / (10**(random.randint(0,10)))
            # num1 = round(num1, max(len(str(num1).split(".")[-1]), 6))
            # answer = num1 * num2 
            answer = round(num1 * num2, len(str(num1).split(".")[-1])+len(str(num2).split(".")[-1]))
            if random.random() < 0.3:
                question = f"({num1}) * {num2}" 
                output = f"({num1}) * {num2} = {answer}"
            else:
                question = f"{num1} * {num2}" 
                output = f"{num1} * {num2} = {answer}"
            assert(output.split()[-1] == str(answer))
            data_mul_n_1.append(get_data_format(prompt=question, response=answer, from_type="self-generate", domain=["Math", "Multiplication_n_1_dec"]))
        elif 0.5 <=random.random() < 0.75:
            if random.random()<0.5:
                num1, num2 = num2, num1 
            num2 = -num2 #-1 * num2
            num1 = num1 / (10**(random.randint(1,6)))
            num2 = num2 / (10**(random.randint(0,10)))
            # num1 = round(num1, max(len(str(num1).split(".")[-1]), 6))
            # answer = num1 * num2 
            answer = round(num1 * num2, len(str(num1).split(".")[-1])+len(str(num2).split(".")[-1]))
            question = f"{num1} * ({num2})" 
            output = f"{num1} * ({num2}) = {answer}"
            assert(output.split()[-1] == str(answer))
            data_mul_n_1.append(get_data_format(prompt=question, response=answer, from_type="self-generate", domain=["Math", "Multiplication_n_1_dec"]))
        else:
            if random.random()<0.5:
                num1, num2 = num2, num1 
            num1 = -num1 #-1 * num1
            num2 = -num2 #-1 * num2
            num1 = num1 / (10**(random.randint(1,6)))
            num2 = num2 / (10**(random.randint(0,10)))
            # num1 = round(num1, max(len(str(num1).split(".")[-1]), 6))
            # answer = num1 * num2 
            answer = round(num1 * num2, len(str(num1).split(".")[-1])+len(str(num2).split(".")[-1]))
            if random.random() < 0.3:
                question = f"({num1}) * ({num2})" 
                output = f"({num1}) * ({num2}) = {answer}"
            else:
                question = f"{num1} * ({num2})" 
                output = f"{num1} * ({num2}) = {answer}"
            assert(output.split()[-1] == str(answer))
            data_mul_n_1.append(get_data_format(prompt=question, response=answer, from_type="self-generate", domain=["Math", "Multiplication_n_1_dec"]))

    return data_mul_n_1

def get_Mul_CoT(num1, num2, question, answer):
    if (num1<0 and num2<0) or (num1>0 and num2>0):
        src_num1, src_num2 = num1, num2
        num1, num2 = abs(num1), abs(num2)
        if num2 > num1:
            num1, num2 = num2, num1
        num_digits_1 = len(str(num1))
        num_digits_2 = len(str(num2))
        if num1 % (10 ** (num_digits_1-1)) == 0 or num2 % (10 ** (num_digits_2-1)) == 0:
            cot = question + " = " + str(answer)
        else:
            if src_num1<0 and src_num2<0:
                convert = f"{num1} * {num2}"
            num2_digits = [int(d) for d in str(num2)]
            split_terms = [d* 10**(len(num2_digits)-i-1) for i, d in enumerate(num2_digits) if d != 0]
            split = f"""{num1} * ({" + ".join(str(x) for x in split_terms)})"""
            expansion = " + ".join([f"{num1} * {x}" for x in split_terms])
            summation_terms = [num1 * x for x in split_terms]
            summation = " + ".join(str(x) for x in summation_terms)
            step = ""
            while summation_terms:
                first = summation_terms.pop(0)
                if not summation_terms:
                    output = first
                    break
                summation_terms[0] = first + summation_terms[0]
                step = step + " + ".join([f"{x}" for x in summation_terms])
                if len(summation_terms)>=2:
                    step = step + "\n= "
            if src_num1<0 and src_num2<0:
                cot = question + "\n= " + f"{convert}\n= {split}\n= {expansion}\n= {summation}\n= " + step + f"\n因此，{question} = {answer}"
            else:
                cot = question + "\n= " + f"{split}\n= {expansion}\n= {summation}\n= " + step + f"\n因此，{question} = {answer}"
    else:
        num1, num2 = abs(num1), abs(num2)
        if num2 > num1:
            num1, num2 = num2, num1
        num_digits_1 = len(str(num1))
        num_digits_2 = len(str(num2))
        if num1 % (10 ** (num_digits_1-1)) == 0 or num2 % (10 ** (num_digits_2-1)) == 0:
            cot = question + " = " + str(answer)
        else:
            convert = f"- ({num1} * {num2})"
            num2_digits = [int(d) for d in str(num2)]
            split_terms = [d* 10**(len(num2_digits)-i-1) for i, d in enumerate(num2_digits) if d != 0]
            split = f"""- ({num1} * ({" + ".join(str(x) for x in split_terms)}))"""
            expansion = "- (" + " + ".join([f"{num1} * {x}" for x in split_terms]) + ")"
            summation_terms = [num1 * x for x in split_terms]
            summation = "- (" + " + ".join(str(x) for x in summation_terms) + ")"
            step = ""
            while summation_terms:
                first = summation_terms.pop(0)
                if not summation_terms:
                    output = first
                    break
                summation_terms[0] = first + summation_terms[0]
                step = step + "- (" + " + ".join([f"{x}" for x in summation_terms]) + ")"
                if len(summation_terms)>=2:
                    step = step + "\n= "
            cot = question + "\n= " + f"{convert}\n= {split}\n= {expansion}\n= {summation}\n= " + step + f"\n因此，{question} = {answer}"
    return cot

def Multiplication_n_m(datatype="train"):
    # multi-digit multiplication, with the product up to 12 digits
    n = 1
    if datatype == "valid" or datatype == "test":
        n = 100
    pairs = \
        [(random.randint(10**(i-1)+1, 10**i-1), random.randint(10**(j-1)+1, 10**j-1)) for i in range(2,7) for j in range(i,13-i) for k in range(int(10000/n))] +\
        [(random.randint(10**(i-1)+1, 10**i-1), random.randint(10**(j-1)+1, 10**j-1)) for i in range(4,7) for j in range(i,13-i) for k in range(int(10000/n))] +\
        [(random.randint(10**(i-1)+1, 10**i-1), random.randint(10**(j-1)+1, 10**j-1)) for i in range(5,7) for j in range(i,13-i) for k in range(int(10000/n))] +\
        [(random.randint(10**(i-1)+1, 10**i-1), random.randint(10**(i-1)+1, 10**i-1)) for i in range(3,7) for k in range(int(10000/n))] 

    random.shuffle(pairs)

    print("Multiplication nxm:", len(pairs))

    data_mul_n_m = []

    for num1, num2 in pairs:
        answer = num1 * num2
        if random.random() < 0.5:
            num1, num2 = num2, num1
        question = f"{num1} * {num2}"
        cot = get_Mul_CoT(num1, num2, question, answer)
        data_mul_n_m.append(get_data_format(prompt=question, response=cot, from_type="self-generate", domain=["Math", "Multiplication_n_m"]))
    
    return data_mul_n_m

def Multiplication_n_m_neg(datatype="train"):
    # multi-digit multiplication, with the product up to 12 digits
    n = 1
    if datatype == "valid" or datatype == "test":
        n = 100
    pairs = \
        [(random.randint(10**(i-1)+1, 10**i-1), random.randint(10**(j-1)+1, 10**j-1)) for i in range(2,7) for j in range(i,13-i) for k in range(int(2500/n))] +\
        [(random.randint(10**(i-1)+1, 10**i-1), random.randint(10**(j-1)+1, 10**j-1)) for i in range(4,7) for j in range(i,13-i) for k in range(int(2500/n))] +\
        [(random.randint(10**(i-1)+1, 10**i-1), random.randint(10**(j-1)+1, 10**j-1)) for i in range(5,7) for j in range(i,13-i) for k in range(int(2500/n))] +\
        [(random.randint(10**(i-1)+1, 10**i-1), random.randint(10**(i-1)+1, 10**i-1)) for i in range(3,7) for k in range(int(2500/n))] 

    random.shuffle(pairs)

    print("Multiplication nxm:", len(pairs))

    data_mul_n_m = []

    for num1, num2 in pairs:
        if random.random()<0.33:
            if random.random()<0.5:
                num1, num2 = num2, num1 
            num1 = -1 * num1
            answer = num1 * num2
            if random.random() < 0.3:
                question = f"({num1}) * {num2}"
            else:
                question = f"{num1} * {num2}"
            cot = get_Mul_CoT(num1, num2, question, answer)
            assert(cot.split()[-1] == str(answer))
            data_mul_n_m.append(get_data_format(prompt=question, response=cot, from_type="self-generate", domain=["Math", "Multiplication_n_m_neg"]))
        elif 0.33<=random.random()<0.63:
            if random.random()<0.5:
                num1, num2 = num2, num1 
            num2 = -1 * num2
            answer = num1 * num2
            question = f"{num1} * ({num2})"
            cot = get_Mul_CoT(num1, num2, question, answer)
            assert(cot.split()[-1] == str(answer))
            data_mul_n_m.append(get_data_format(prompt=question, response=cot, from_type="self-generate", domain=["Math", "Multiplication_n_m_neg"]))
        else:
            if random.random()<0.5:
                num1, num2 = num2, num1 
            num1 = -1 * num1
            num2 = -1 * num2
            answer = num1 * num2
            if random.random() < 0.3:
                question = f"({num1}) * ({num2})" 
            else:
                question = f"{num1} * ({num2})" 
            cot = get_Mul_CoT(num1, num2, question, answer)
            assert(cot.split()[-1] == str(answer))
            data_mul_n_m.append(get_data_format(prompt=question, response=cot, from_type="self-generate", domain=["Math", "Multiplication_n_m_neg"]))
    return data_mul_n_m

def get_Mul_Dec_CoT_old(num1, num2, question, answer):
    if (num1<0 and num2<0) or (num1>0 and num2>0):
        src_num1, src_num2 = num1, num2
        num1, num2 = abs(num1), abs(num2)
        if num2 > num1:
            num1, num2 = num2, num1
        num_dec_digits_1 = len(str(num1).split(".")[-1])
        num_dec_digits_2 = len(str(num2).split(".")[-1])
        if num1 % (10 ** (-num_dec_digits_1)) == 0 or num2 % (10 ** (-num_dec_digits_2)) == 0:
            cot = question + " = " + str(answer)
        else:
            if src_num1<0 and src_num2<0:
                convert = f"{num1} * {num2}"
            if "." not in str(num2) and "e-" not in str(num2):
                num2_digits = [int(d) for d in str(int(num2))]
                split_terms = [d* 10**(len(num2_digits)-i-1) for i, d in enumerate(num2_digits) if d != 0]
            else:
                num2_int_digits = [int(d) for d in str(int(num2))]
                if "e" not in str(num2):
                    num2_dec_digits = [int(d) for d in "".join(str(num2).split(".")[-1])]
                else:
                    num2_dec_digits = [int(d) for d in "".join(str(num2)[:str(num2).index("e")].split(".")[-1])] +\
                                        [float("1" + str(num2)[str(num2).index("e"):])]
                split_terms = [d* 10**(len(num2_int_digits)-i-1) for i, d in enumerate(num2_int_digits) if d != 0] +\
                              [d/ 10**(i+1) for i, d in enumerate(num2_dec_digits) if d>=1] +\
                              [d/ 10**(i+1) for i, d in enumerate(num2_dec_digits) if d<1]
            split = f"""{num1} * ({" + ".join(str(x) for x in split_terms)})"""
            expansion = " + ".join([f"{num1} * {x}" for x in split_terms])
            # summation_terms = [num1 * x for x in split_terms]
            summation_terms = []
            for x in split_terms:
                if x >= 1:
                    if "." not in str(num1):
                        product = num1 * x
                    else:
                        num1_dec_length = len(str(num1).split(".")[-1])
                        product = num1 * 10**num1_dec_length * x / 10**num1_dec_length
                else:
                    if "." not in str(x):
                        if "." not in str(num1):
                            product = num1 * x
                        else:
                            num1_dec_length = len(str(num1).split(".")[-1])
                            product = num1 * 10**num1_dec_length * x / 10**num1_dec_length
                    else:
                        dec_length = len(str(x).split(".")[-1])
                        if "." not in str(num1):
                            product = num1 * (x * 10**dec_length) / 10**dec_length
                        else:
                            num1_dec_length = len(str(num1).split(".")[-1])
                            product = num1 * 10**num1_dec_length * (x * 10**dec_length) / 10**num1_dec_length / 10**dec_length
                summation_terms.append(product)
            summation = " + ".join(str(x) for x in summation_terms)
            step = ""
            while summation_terms:
                first = summation_terms.pop(0)
                if not summation_terms:
                    output = first
                    break
                summation_terms[0] = first + summation_terms[0]
                step = step + " + ".join([f"{x}" for x in summation_terms])
                if len(summation_terms)>=2:
                    step = step + "\n= "
            if src_num1<0 and src_num2<0:
                cot = question + "\n= " + f"{convert}\n= {split}\n= {expansion}\n= {summation}\n= " + step + f"\n因此，{question} = {answer}"
            else:
                cot = question + "\n= " + f"{split}\n= {expansion}\n= {summation}\n= " + step + f"\n因此，{question} = {answer}"
    else:
        num1, num2 = abs(num1), abs(num2)
        if num2 > num1:
            num1, num2 = num2, num1
        num_dec_digits_1 = len(str(num1).split(".")[-1])
        num_dec_digits_2 = len(str(num2).split(".")[-1])
        if num1 % (10 ** (-num_dec_digits_1)) == 0 or num2 % (10 ** (-num_dec_digits_2)) == 0:
            cot = question + " = " + str(answer)
        else:
            convert = f"- ({num1} * {num2})"
            if "." not in str(num2) and "e-" not in str(num2):
                num2_digits = [int(d) for d in str(int(num2))]
                split_terms = [d* 10**(len(num2_digits)-i-1) for i, d in enumerate(num2_digits) if d != 0]
            else:
                num2_int_digits = [int(d) for d in str(int(num2))]
                if "e" not in str(num2):
                    num2_dec_digits = [int(d) for d in "".join(str(num2).split(".")[-1])]
                else:
                    num2_dec_digits = [int(d) for d in "".join(str(num2)[:str(num2).index("e")].split(".")[-1])] +\
                                        [float("1" + str(num2)[str(num2).index("e"):])]
                split_terms = [d* 10**(len(num2_int_digits)-i-1) for i, d in enumerate(num2_int_digits) if d != 0] +\
                              [d/ 10**(i+1) for i, d in enumerate(num2_dec_digits) if d>=1] +\
                              [d/ 10**(i+1) for i, d in enumerate(num2_dec_digits) if d<1]
            split = f"""- ({num1} * ({" + ".join(str(x) for x in split_terms)}))"""
            expansion = "- (" + " + ".join([f"{num1} * {x}" for x in split_terms]) + ")"
            # summation_terms = [num1 * x for x in split_terms]
            summation_terms = []
            for x in split_terms:
                if x >= 1:
                    if "." not in str(num1):
                        product = num1 * x
                    else:
                        num1_dec_length = len(str(num1).split(".")[-1])
                        product = round(num1 * 10**num1_dec_length * x / 10**num1_dec_length, num1_dec_length)
                else:
                    if "." not in str(x):
                        if "." not in str(num1):
                            product = num1 * x
                        else:
                            num1_dec_length = len(str(num1).split(".")[-1])
                            product = round(num1 * 10**num1_dec_length * x / 10**num1_dec_length, num1_dec_length)
                    else:
                        dec_length = len(str(x).split(".")[-1])
                        if "." not in str(num1):
                            product = round(num1 * (x * 10**dec_length) / 10**dec_length, dec_length)
                        else:
                            num1_dec_length = len(str(num1).split(".")[-1])
                            product = round(num1 * 10**num1_dec_length * (x * 10**dec_length) / 10**num1_dec_length / 10**dec_length, num1_dec_length*dec_length)
                summation_terms.append(product)
            summation = "- (" + " + ".join(str(x) for x in summation_terms) + ")"
            step = ""
            while summation_terms:
                first = summation_terms.pop(0)
                if not summation_terms:
                    output = first
                    break
                summation_terms[0] = first + summation_terms[0]
                step = step + "- (" + " + ".join([f"{x}" for x in summation_terms]) + ")"
                if len(summation_terms)>=2:
                    step = step + "\n= "
            cot = question + "\n= " + f"{convert}\n= {split}\n= {expansion}\n= {summation}\n= " + step + f"\n因此，{question} = {answer}"
    return cot

def get_Mul_Dec_CoT(num1, num2, question, answer):
    if (num1<0 and num2<0) or (num1>0 and num2>0):
        src_num1, src_num2 = num1, num2
        num1, num2 = abs(num1), abs(num2)
        if num2 > num1:
            num1, num2 = num2, num1

        num_dec_digits_1, num_dec_digits_2, e_power_1, e_power_2 = 0, 0, 0, 0
        if "." in str(num1) and "e" not in str(num1):
            num_dec_digits_1 = len(str(num1).split(".")[-1])
        elif "." in str(num1) and "e" in str(num1):
            num_dec_digits_1 = len(str(num1)[:str(num1).index("e")].split(".")[-1])
            e_power_1 = int(str(num1).split("e-")[-1])
        if "." in str(num2) and "e" not in str(num2):
            num_dec_digits_2 = len(str(num2).split(".")[-1])
        elif "." in str(num2) and "e" in str(num2):
            num_dec_digits_2 = len(str(num2)[:str(num2).index("e")].split(".")[-1])
            e_power_2 = int(str(num2).split("e-")[-1])
        div_power = 10**(num_dec_digits_1 + num_dec_digits_2 + e_power_1 + e_power_2)

        num1 = int(num1 * (10**num_dec_digits_1) * (10**e_power_1))
        num2 = int(num2 * (10**num_dec_digits_2) * (10**e_power_2))

        num_digits_1 = len(str(num1))
        num_digits_2 = len(str(num2))
        if num1 % (10 ** (num_digits_1-1)) == 0 or num2 % (10 ** (num_digits_2-1)) == 0:
            cot = question + " = " + str(answer)
        else:
            if src_num1<0 and src_num2<0:
                convert = f"{abs(src_num1)} * {abs(src_num2)}"
            convert_to_div = f"{num1} * {num2} / {div_power}"
            num2_digits = [int(d) for d in str(num2)]
            split_terms = [d* 10**(len(num2_digits)-i-1) for i, d in enumerate(num2_digits) if d != 0]
            split = f"""({num1} * ({" + ".join(str(x) for x in split_terms)})) / {div_power}"""
            expansion = "(" + " + ".join([f"{num1} * {x}" for x in split_terms]) + ")" + f" / {div_power}"
            summation_terms = [num1 * x for x in split_terms]
            summation = "(" + " + ".join(str(x) for x in summation_terms) + ")" + f" / {div_power}"
            step = ""
            while summation_terms:
                first = summation_terms.pop(0)
                if not summation_terms:
                    output = first
                    break
                summation_terms[0] = first + summation_terms[0]
                step = step + "(" + " + ".join([f"{x}" for x in summation_terms]) + ")" + f" / {div_power}"
                if len(summation_terms)>=2:
                    step = step + "\n= "
            step = step + f"\n= {answer}"
            if src_num1<0 and src_num2<0:
                cot = question + "\n= " + f"{convert}\n= {convert_to_div}\n= {split}\n= {expansion}\n= {summation}\n= " + step + f"\n因此，{question} = {answer}"
            else:
                cot = question + "\n= " + f"{convert_to_div}\n= {split}\n= {expansion}\n= {summation}\n= " + step + f"\n因此，{question} = {answer}"
    else:
        src_num1, src_num2 = num1, num2
        num1, num2 = abs(num1), abs(num2)
        if num2 > num1:
            num1, num2 = num2, num1

        num_dec_digits_1, num_dec_digits_2, e_power_1, e_power_2 = 0, 0, 0, 0
        if "." in str(num1) and "e" not in str(num1):
            num_dec_digits_1 = len(str(num1).split(".")[-1])
        elif "." in str(num1) and "e" in str(num1):
            num_dec_digits_1 = len(str(num1)[:str(num1).index("e")].split(".")[-1])
            e_power_1 = int(str(num1).split("e-")[-1])
        if "." in str(num2) and "e" not in str(num2):
            num_dec_digits_2 = len(str(num2).split(".")[-1])
        elif "." in str(num2) and "e" in str(num2):
            num_dec_digits_2 = len(str(num2)[:str(num2).index("e")].split(".")[-1])
            e_power_2 = int(str(num2).split("e-")[-1])
        div_power = 10**(num_dec_digits_1 + num_dec_digits_2 + e_power_1 + e_power_2)

        num1 = int(num1 * (10**num_dec_digits_1) * (10**e_power_1))
        num2 = int(num2 * (10**num_dec_digits_2) * (10**e_power_2))

        num_digits_1 = len(str(num1))
        num_digits_2 = len(str(num2))
        if num1 % (10 ** (num_digits_1-1)) == 0 or num2 % (10 ** (num_digits_2-1)) == 0:
            cot = question + " = " + str(answer)
        else:
            convert = f"- ({abs(src_num1)} * {abs(src_num2)})"
            convert_to_div = f"- ({num1} * {num2} / {div_power})"
            num2_digits = [int(d) for d in str(num2)]
            split_terms = [d* 10**(len(num2_digits)-i-1) for i, d in enumerate(num2_digits) if d != 0]
            split = f"""- ({num1} * ({" + ".join(str(x) for x in split_terms)})) / {div_power}"""
            expansion = "- (" + " + ".join([f"{num1} * {x}" for x in split_terms]) + ")" + f" / {div_power}"
            summation_terms = [num1 * x for x in split_terms]
            summation = "- (" + " + ".join(str(x) for x in summation_terms) + ")" + f" / {div_power}"
            step = ""
            while summation_terms:
                first = summation_terms.pop(0)
                if not summation_terms:
                    output = first
                    break
                summation_terms[0] = first + summation_terms[0]
                step = step + "- (" + " + ".join([f"{x}" for x in summation_terms]) + ")" + f" / {div_power}"
                if len(summation_terms)>=2:
                    step = step + "\n= "
            step = step + f"\n= {answer}"
            cot = question + "\n= " + f"{convert}\n= {convert_to_div}\n= {split}\n= {expansion}\n= {summation}\n= " + step + f"\n因此，{question} = {answer}"
    return cot

def Multiplication_n_m_dec(datatype="train"):
    # multi-digit multiplication, with the product up to 12 digits
    n = 1
    if datatype == "valid" or datatype == "test":
        n = 10
    pairs = \
        [(random.randint(10**(i-1)+1, 10**i-1), random.randint(10**(j-1)+1, 10**j-1)) for i in range(1,6) for j in range(1,6) for k in range(int(1000/n))] +\
        [(random.randint(10**(i-1)+1, 10**i-1), random.randint(10**(j-1)+1, 10**j-1)) for i in range(2,6) for j in range(1,6) for k in range(int(1000/n))] +\
        [(random.randint(10**(i-1)+1, 10**i-1), random.randint(10**(j-1)+1, 10**j-1)) for i in range(3,6) for j in range(1,6) for k in range(int(1000/n))] +\
        [(random.randint(10**(i-1)+1, 10**i-1), random.randint(10**(i-1)+1, 10**i-1)) for i in range(4,6) for k in range(int(1000/n))] 

    random.shuffle(pairs)

    print("Multiplication nxm:", len(pairs))

    data_mul_n_m = []

    for num1, num2 in pairs:
        if random.random() < 0.25:
            if random.random()<0.5:
                num1, num2 = num2, num1 
            num1 = num1 / (10**(random.randint(0,5)))
            num2 = num2 / (10**(random.randint(0,5)))
            # answer = num1 * num2 
            answer = round(num1 * num2, len(str(num1).split(".")[-1])+len(str(num2).split(".")[-1]))
            question = f"{num1} * {num2}" 
            cot = get_Mul_Dec_CoT(num1, num2, question, answer)
            assert((float(cot.split()[-1]) - float(answer)) < 0.0001)
            data_mul_n_m.append(get_data_format(prompt=question, response=cot, from_type="self-generate", domain=["Math", "Multiplication_n_m_dec"]))
        elif 0.25 <= random.random() < 0.5:
            if random.random()<0.5:
                num1, num2 = num2, num1 
            num1 = -1 * num1
            num1 = num1 / (10**(random.randint(0,5)))
            num2 = num2 / (10**(random.randint(0,5)))
            # answer = num1 * num2
            answer = round(num1 * num2, len(str(num1).split(".")[-1])+len(str(num2).split(".")[-1]))
            if random.random() < 0.3:
                question = f"({num1}) * {num2}"
            else:
                question = f"{num1} * {num2}"
            cot = get_Mul_Dec_CoT(num1, num2, question, answer)
            assert((-float(cot.split()[-1].strip()[1:]) - float(answer)) < 0.0001)
            data_mul_n_m.append(get_data_format(prompt=question, response=cot, from_type="self-generate", domain=["Math", "Multiplication_n_m_dec"]))
        elif 0.5 <= random.random() < 0.75:
            if random.random()<0.5:
                num1, num2 = num2, num1 
            num2 = -1 * num2
            num1 = num1 / (10**(random.randint(0,5)))
            num2 = num2 / (10**(random.randint(0,5)))
            # answer = num1 * num2
            answer = round(num1 * num2, len(str(num1).split(".")[-1])+len(str(num2).split(".")[-1]))
            question = f"{num1} * ({num2})"
            cot = get_Mul_Dec_CoT(num1, num2, question, answer)
            assert(-float(cot.split()[-1].strip()[1:]) - float(answer) < 0.0001)
            data_mul_n_m.append(get_data_format(prompt=question, response=cot, from_type="self-generate", domain=["Math", "Multiplication_n_m_dec"]))
        else:
            if random.random()<0.5:
                num1, num2 = num2, num1 
            num1 = -1 * num1
            num2 = -1 * num2
            num1 = num1 / (10**(random.randint(0,5)))
            num2 = num2 / (10**(random.randint(0,5)))
            # answer = num1 * num2
            answer = round(num1 * num2, len(str(num1).split(".")[-1])+len(str(num2).split(".")[-1]))
            if random.random() < 0.3:
                question = f"({num1}) * ({num2})" 
            else:
                question = f"{num1} * ({num2})" 
            cot = get_Mul_Dec_CoT(num1, num2, question, answer)
            assert((float(cot.split()[-1]) - float(answer)) < 0.0001)
            data_mul_n_m.append(get_data_format(prompt=question, response=cot, from_type="self-generate", domain=["Math", "Multiplication_n_m_dec"]))
    return data_mul_n_m


def Division_n_1_deprecated(datatype="train"):
    # Division n/1, with n up to 16 digits
    # pairs represent (divisor, quotient)
    n = 1
    if datatype == "valid" or datatype == "test":
        n = 100
    pairs = \
        [(random.randint(2, 9), random.randint(10**(j-1)+1, 10**j)) for j in range(1,5) for k in range(int(4000/n))] + \
        [(random.randint(2, 9), random.randint(10**(j-1)+1, 10**j)) for j in range(5,8) for k in range(int(8000/n))] + \
        [(random.randint(2, 9), random.randint(10**(j-1)+1, 10**j)) for j in range(8,12) for k in range(int(12000/n))] + \
        [(random.randint(2, 9), random.randint(10**(j-1)+1, 10**j)) for j in range(12,17) for k in range(int(16000/n))] + \
        [(1, random.randint(10**(j-1)+1, 10**j)) for j in range(1,17) for k in range(int(500/n))] + \
        [(10, random.randint(10**(j-1)+1, 10**j)) for j in range(1,17) for k in range(int(500/n))] + \
        [(random.randint(10**(j-1)+1, 10**j), 0) for j in range(1,17) for k in range(int(100/n))] + \
        [(random.randint(1, 10), random.randint(1, 10)) for k in range(int(500/n))] +\
        [(0, random.randint(10**(j-1)+1, 10**j)) for j in range(1,18) for k in range(int(100/n))]

    random.shuffle(pairs)

    print("Division n/1:", len(pairs))

    data_div_n_1 = []

    for num1, num2 in pairs:

        # make it divisible with 0.5 probability
        if num1>1 and random.random() < 0.5: 
            remainder = random.randint(1, num1-1)
        else:
            remainder = 0
        
        # divided by 0
        if num1 == 0:
            question = f"{num2} / {num1}" 
            cot = question + "存在错误，除数不能为0。"
            answer = "undefined"
            data_div_n_1.append(get_data_format(prompt=question, response=cot, from_type="self-generate", domain=["Math", "Division_n_1"]))
            continue
            

        dividend = num1 * num2 + remainder
        
        question = f"{dividend} / {num1}" 
        if random.random() < 0.5:
            cot = question + " = " + str(num2) + " R " + str(remainder) if remainder!=0 else question + " = " + str(num2)
            answer = str(num2) + " R " + str(remainder) if remainder!=0 else str(num2)
            assert(cot.split()[-1] == answer.split()[-1])
        else:
            cot = '%.4f'%(dividend/num1)
        data_div_n_1.append(get_data_format(prompt=question, response=cot, from_type="self-generate", domain=["Math", "Division_n_1"]))
    return data_div_n_1

def Division_n_1(datatype="train"):
    # Division n/1, with n up to 16 digits
    # pairs represent (divisor, quotient)
    n = 1
    if datatype == "valid" or datatype == "test":
        n = 50
    pairs = \
        [(random.randint(2, 9), random.randint(10**(j-1)+1, 10**j)) for j in range(1,5) for k in range(int(4000/n))] + \
        [(random.randint(2, 9), random.randint(10**(j-1)+1, 10**j)) for j in range(4,8) for k in range(int(8000/n))] + \
        [(random.randint(2, 9), random.randint(10**(j-1)+1, 10**j)) for j in range(7,12) for k in range(int(12000/n))] + \
        [(random.randint(2, 9), random.randint(10**(j-1)+1, 10**j)) for j in range(10,12) for k in range(int(16000/n))] + \
        [(1, random.randint(10**(j-1)+1, 10**j)) for j in range(1,12) for k in range(int(500/n))] + \
        [(10, random.randint(10**(j-1)+1, 10**j)) for j in range(1,12) for k in range(int(500/n))] + \
        [(random.randint(10**(j-1)+1, 10**j), 0) for j in range(1,12) for k in range(int(100/n))] + \
        [(random.randint(1, 10), random.randint(1, 10)) for k in range(int(500/n))] +\
        [(0, random.randint(10**(j-1)+1, 10**j)) for j in range(1,12) for k in range(int(100/n))]

    random.shuffle(pairs)

    print("Division n/1:", len(pairs))

    data_div_n_1 = []

    # pairs = [(random.randint(1, 9), random.randint(1, 100))]
    for num1, num2 in pairs:

        # make it divisible with 0.5 probability
        if num1>1 and random.random() < 0.5: 
            remainder = random.randint(1, num1-1)
        else:
            remainder = 0
        if num1 == 0:
            if random.random() < 0.3:
                question = f"{num1} / {num2}"
                answer = num1 / num2
                cot = answer
                data_div_n_1.append(get_data_format(prompt=question, response=cot, from_type="self-generate", domain=["Math", "Division_n_1"]))
                continue
            else:
                # divided by 0
                question = f"{num2} / {num1}" 
                cot = question + "存在错误，除数不能为0。"
                answer = "undefined"
                data_div_n_1.append(get_data_format(prompt=question, response=cot, from_type="self-generate", domain=["Math", "Division_n_1"]))
                continue
            
        dividend = num1 * num2 + remainder

        question = f"{dividend} / {num1}" 

        if remainder == 0:
            cot = question + " = " + str(num2)
            answer = str(num2)
            assert(cot.split()[-1] == answer.split()[-1])
        else:  
            cot1 = question + " = " + str(num2) + " R " + str(remainder)
            answer_remainder = str(num2) + " R " + str(remainder)
            assert(cot1.split()[-1] == answer_remainder.split()[-1])

            max_digits_after_decimal_point = 4
            decimal_round = 0
            answer_decimal = round(dividend / num1, max_digits_after_decimal_point)
            step = ""
            cot2 = ""
            left = remainder
            computed_answer = num2
            while decimal_round <= max_digits_after_decimal_point:
                left = left * 10
                quotient = left // num1
                answer = num1 * quotient
                new_left = left - answer
                step = f"{left} - {num1} * {quotient} = {left} - {answer} = {new_left}"
                cot2 = cot2 + step + "\n"
                left = new_left
                decimal_round += 1
                computed_answer = computed_answer + quotient/(10**decimal_round)
                if left == 0:
                    break
            computed_answer = round(computed_answer, max_digits_after_decimal_point)
            assert(abs(round(answer_decimal - computed_answer, max_digits_after_decimal_point)) <= 0.0001), f"{answer_decimal} vs {computed_answer} \n{cot1}\n{cot2}"
            decimal_digits = min(decimal_round, max_digits_after_decimal_point)
            cot = f"{cot1}\n{cot2}\n因此，{question} = {num2} R {remainder}，即商为{num2}，余数为{remainder}。\n小数点后保留{decimal_digits}位有效数字：{question} = {computed_answer}"

        data_div_n_1.append(get_data_format(prompt=question, response=cot, from_type="self-generate", domain=["Math", "Division_n_1"]))
    return data_div_n_1

def Division_n_1_neg(datatype="train"):
    # Division n/1, with n up to 16 digits
    # pairs represent (divisor, quotient)
    n = 1
    if datatype == "valid" or datatype == "test":
        n = 50
    pairs = \
        [(random.randint(2, 9), random.randint(10**(j-1)+1, 10**j)) for j in range(1,5) for k in range(int(4000/n))] + \
        [(random.randint(2, 9), random.randint(10**(j-1)+1, 10**j)) for j in range(4,8) for k in range(int(8000/n))] + \
        [(random.randint(2, 9), random.randint(10**(j-1)+1, 10**j)) for j in range(7,12) for k in range(int(12000/n))] + \
        [(random.randint(2, 9), random.randint(10**(j-1)+1, 10**j)) for j in range(10,12) for k in range(int(16000/n))] + \
        [(1, random.randint(10**(j-1)+1, 10**j)) for j in range(1,12) for k in range(int(500/n))] + \
        [(10, random.randint(10**(j-1)+1, 10**j)) for j in range(1,12) for k in range(int(500/n))] + \
        [(random.randint(10**(j-1)+1, 10**j), 0) for j in range(1,12) for k in range(int(100/n))] + \
        [(random.randint(1, 10), random.randint(1, 10)) for k in range(int(500/n))] +\
        [(0, random.randint(10**(j-1)+1, 10**j)) for j in range(1,12) for k in range(int(100/n))]

    random.shuffle(pairs)

    print("Division n/1:", len(pairs))

    data_div_n_1 = []

    # pairs = [(random.randint(1, 9), random.randint(1, 100))]
    for num1, num2 in pairs:

        # make it divisible with 0.5 probability
        if num1>1 and random.random() < 0.5: 
            remainder = random.randint(1, num1-1)
        else:
            remainder = 0
        if num1 == 0:
            num2 = -1 * num2
            if random.random() < 0.3:
                question = f"{num1} / ({num2})"
                answer = num1 / num2
                cot = answer
                data_div_n_1.append(get_data_format(prompt=question, response=cot, from_type="self-generate", domain=["Math", "Division_n_1"]))
                continue
            else:
                # divided by 0
                if random.random() < 0.5:
                    question = f"{num2} / {num1}" 
                else:
                    question = f"({num2}) / {num1}"
                cot = question + "存在错误，除数不能为0。"
                answer = "undefined"
                data_div_n_1.append(get_data_format(prompt=question, response=cot, from_type="self-generate", domain=["Math", "Division_n_1"]))
                continue
            
        dividend = num1 * num2 + remainder
        # question = f"{dividend} / {num1}" 

        if remainder == 0:
            if random.random() < 0.33:
                num1 = -num1
                if random.random() < 0.5:
                    question = f"-{dividend} / ({num1})" 
                else:
                    question = f"(-{dividend}) / ({num1})"
            elif 0.33 <= random.random() < 0.66:
                num2 = -num2
                if random.random() < 0.5:
                    question = f"-{dividend} / {num1}"
                else:
                    question = f"(-{dividend}) / {num1}"
            else:
                num1 = -num1
                num2 = -num2
                question = f"{dividend} / ({num1})"
            cot = question + " = " + str(num2)
            answer = str(num2)
            assert(cot.split()[-1] == answer.split()[-1])
        else:  
            if random.random() < 0.33:
                num1 = -num1
                dividend = -dividend
                if random.random() < 0.5:
                    question = f"{dividend} / ({num1})" 
                else:
                    question = f"({dividend}) / ({num1})"
            elif 0.33 <= random.random() < 0.66:
                num2 = -num2
                dividend = -dividend
                if random.random() < 0.5:
                    question = f"{dividend} / {num1}"
                else:
                    question = f"({dividend}) / {num1}"
            else:
                num1 = -num1
                num2 = -num2
                question = f"{dividend} / ({num1})"
            if dividend < 0 :
                remainder = -remainder
            cot1 = question + " = " + str(num2) + " R " + str(remainder)
            answer_remainder = str(num2) + " R " + str(remainder)
            assert(cot1.split()[-1] == answer_remainder.split()[-1])

            max_digits_after_decimal_point = 4
            decimal_round = 0
            answer_decimal = round(dividend / num1, max_digits_after_decimal_point)
            step = ""
            cot2 = ""
            left = remainder
            computed_answer = num2
            while decimal_round <= max_digits_after_decimal_point:
                source_left, source_num1 = left, num1
                left, num1 = abs(left), abs(num1)
                left = left * 10
                quotient = left // num1
                answer = num1 * quotient
                new_left = left - answer
                decimal_round += 1
                if (source_left > 0 and source_num1 > 0) or (source_left < 0 and source_num1 < 0):
                    step = f"{left} - {num1} * {quotient} = {left} - {answer} = {new_left}"
                    left = new_left
                    computed_answer = computed_answer + quotient/(10**decimal_round)
                elif (source_left > 0 and source_num1 < 0) or (source_left < 0 and source_num1 > 0):
                    step = f"- ({left} - {num1} * {quotient}) = - ({left} - {answer}) = -{new_left}"
                    left = -new_left
                    computed_answer = computed_answer - quotient/(10**decimal_round)
                cot2 = cot2 + step + "\n"
                if left == 0:
                    break
            computed_answer = round(computed_answer, max_digits_after_decimal_point)
            assert(abs(round(answer_decimal - computed_answer, max_digits_after_decimal_point)) <= 0.0001), f"{answer_decimal} vs {computed_answer} \n{cot1}\n{cot2}"
            decimal_digits = min(decimal_round, max_digits_after_decimal_point)
            cot = f"{cot1}\n{cot2}\n因此，{question} = {num2} R {remainder}，即商为{num2}，余数为{remainder}。\n小数点后保留{decimal_digits}位有效数字：{question} = {computed_answer}"
        # print(cot)
        data_div_n_1.append(get_data_format(prompt=question, response=cot, from_type="self-generate", domain=["Math", "Division_n_1"]))
    return data_div_n_1

# TODO
def Division_n_1_dec(datatype="train"):
    # Division n/1, with n up to 16 digits
    # pairs represent (divisor, quotient)
    n = 1
    if datatype == "valid" or datatype == "test":
        n = 50
    pairs = \
        [(random.randint(2, 9), random.randint(10**(j-1)+1, 10**j)) for j in range(1,5) for k in range(int(4000/n))] + \
        [(random.randint(2, 9), random.randint(10**(j-1)+1, 10**j)) for j in range(4,8) for k in range(int(8000/n))] + \
        [(random.randint(2, 9), random.randint(10**(j-1)+1, 10**j)) for j in range(7,12) for k in range(int(12000/n))] + \
        [(random.randint(2, 9), random.randint(10**(j-1)+1, 10**j)) for j in range(10,12) for k in range(int(16000/n))] + \
        [(1, random.randint(10**(j-1)+1, 10**j)) for j in range(1,12) for k in range(int(500/n))] + \
        [(10, random.randint(10**(j-1)+1, 10**j)) for j in range(1,12) for k in range(int(500/n))] + \
        [(random.randint(10**(j-1)+1, 10**j), 0) for j in range(1,12) for k in range(int(100/n))] + \
        [(random.randint(1, 10), random.randint(1, 10)) for k in range(int(500/n))] +\
        [(0, random.randint(10**(j-1)+1, 10**j)) for j in range(1,12) for k in range(int(100/n))]

    random.shuffle(pairs)

    print("Division n/1:", len(pairs))

    data_div_n_1 = []

    # pairs = [(random.randint(1, 9), random.randint(1, 100))]
    for num1, num2 in pairs:

        # make it divisible with 0.5 probability
        if num1>1 and random.random() < 0.5: 
            remainder = random.randint(1, num1-1)
        else:
            remainder = 0
        if num1 == 0:
            num2 = -1 * num2
            if random.random() < 0.3:
                question = f"{num1} / ({num2})"
                answer = num1 / num2
                cot = answer
                data_div_n_1.append(get_data_format(prompt=question, response=cot, from_type="self-generate", domain=["Math", "Division_n_1"]))
                continue
            else:
                # divided by 0
                if random.random() < 0.5:
                    question = f"{num2} / {num1}" 
                else:
                    question = f"({num2}) / {num1}"
                cot = question + "存在错误，除数不能为0。"
                answer = "undefined"
                data_div_n_1.append(get_data_format(prompt=question, response=cot, from_type="self-generate", domain=["Math", "Division_n_1"]))
                continue
            
        dividend = num1 * num2 + remainder
        # question = f"{dividend} / {num1}" 

        if remainder == 0:
            if random.random() < 0.33:
                num1 = -num1
                if random.random() < 0.5:
                    question = f"-{dividend} / ({num1})" 
                else:
                    question = f"(-{dividend}) / ({num1})"
            elif 0.33 <= random.random() < 0.66:
                num2 = -num2
                if random.random() < 0.5:
                    question = f"-{dividend} / {num1}"
                else:
                    question = f"(-{dividend}) / {num1}"
            else:
                num1 = -num1
                num2 = -num2
                question = f"{dividend} / ({num1})"
            cot = question + " = " + str(num2)
            answer = str(num2)
            assert(cot.split()[-1] == answer.split()[-1])
        else:  
            if random.random() < 0.33:
                num1 = -num1
                dividend = -dividend
                if random.random() < 0.5:
                    question = f"{dividend} / ({num1})" 
                else:
                    question = f"({dividend}) / ({num1})"
            elif 0.33 <= random.random() < 0.66:
                num2 = -num2
                dividend = -dividend
                if random.random() < 0.5:
                    question = f"{dividend} / {num1}"
                else:
                    question = f"({dividend}) / {num1}"
            else:
                num1 = -num1
                num2 = -num2
                question = f"{dividend} / ({num1})"
            if dividend < 0 :
                remainder = -remainder
            cot1 = question + " = " + str(num2) + " R " + str(remainder)
            answer_remainder = str(num2) + " R " + str(remainder)
            assert(cot1.split()[-1] == answer_remainder.split()[-1])

            max_digits_after_decimal_point = 4
            decimal_round = 0
            answer_decimal = round(dividend / num1, max_digits_after_decimal_point)
            step = ""
            cot2 = ""
            left = remainder
            computed_answer = num2
            while decimal_round <= max_digits_after_decimal_point:
                source_left, source_num1 = left, num1
                left, num1 = abs(left), abs(num1)
                left = left * 10
                quotient = left // num1
                answer = num1 * quotient
                new_left = left - answer
                decimal_round += 1
                if (source_left > 0 and source_num1 > 0) or (source_left < 0 and source_num1 < 0):
                    step = f"{left} - {num1} * {quotient} = {left} - {answer} = {new_left}"
                    left = new_left
                    computed_answer = computed_answer + quotient/(10**decimal_round)
                elif (source_left > 0 and source_num1 < 0) or (source_left < 0 and source_num1 > 0):
                    step = f"- ({left} - {num1} * {quotient}) = - ({left} - {answer}) = -{new_left}"
                    left = -new_left
                    computed_answer = computed_answer - quotient/(10**decimal_round)
                cot2 = cot2 + step + "\n"
                if left == 0:
                    break
            computed_answer = round(computed_answer, max_digits_after_decimal_point)
            assert(abs(round(answer_decimal - computed_answer, max_digits_after_decimal_point)) <= 0.0001), f"{answer_decimal} vs {computed_answer} \n{cot1}\n{cot2}"
            decimal_digits = min(decimal_round, max_digits_after_decimal_point)
            cot = f"{cot1}\n{cot2}\n因此，{question} = {num2} R {remainder}，即商为{num2}，余数为{remainder}。\n小数点后保留{decimal_digits}位有效数字：{question} = {computed_answer}"
        # print(cot)
        data_div_n_1.append(get_data_format(prompt=question, response=cot, from_type="self-generate", domain=["Math", "Division_n_1"]))
    return data_div_n_1


def Division_n_m_deprecated(datatype="train"):
    # Division n/m with dividend<=12 digits and quotient<=7 digits
    # pairs represent (dividend, divisor)
    n = 1
    if datatype == "valid" or datatype == "test":
        n = 100
    pairs = \
        [(random.randint(10**(j-1)+1, 10**j), random.randint(10**(i-1)+1, 10**i)) for i in range(2, 7) for j in range(i+1, i+7) for k in range(int(10000/n))] +\
        [(random.randint(10**(j-1)+1, 10**j), random.randint(10**(i-1)+1, 10**i)) for i in range(2, 7) for j in range(2, i+7) for k in range(int(1000/n))]

    random.shuffle(pairs)

    print("Division n/m:", len(pairs))

    data_div_n_m = []

    for num1, num2 in pairs:

        quotient = num1 // num2
        remainder = num1 % num2

        # make it divisible with 0.5 probability
        if num1 > num2 and random.random()<0.5: 
            num1 = num1 - remainder
            quotient = num1 // num2
            remainder = num1 % num2

        question = f"{num1} / {num2}" 

        if quotient == 0:
            cot = f"{num1} / {num2} = {quotient} R {remainder}"
            answer = f"{quotient} R {remainder}"
        elif num1 == num2:
            cot = f"{num1} / {num2} = {quotient}"
            answer = f"{quotient}"        

        else:
            step = ""
            cot = ""
            left = num1

            i = 0
            computed_q = 0

            while left>=num2:
                if int(str(quotient)[i])!=0:
                    intermediate = int(str(quotient)[i] + "0" * (len(str(quotient))-1-i))
                    answer = num2 * intermediate
                    new_left = left - answer
                    step = f"{left} - {num2} * {intermediate} = {left} - {answer} = {new_left}\n"
                    cot = cot + step                   
                    left = new_left
                    computed_q = computed_q + intermediate

                i = i+1

            assert(left == remainder)
            assert(computed_q == quotient)

            if remainder == 0:
                cot = cot + f"因此, {num1} / {num2} = {quotient}"
                answer = f"{quotient}"
            else:
                cot = cot + f"因此, {num1} / {num2} = {quotient} R {remainder}"
                answer = f"{quotient} R {remainder}"

        assert(cot.split()[-1] == answer.split()[-1])
        # data_div_n_m.append({"input": question, "output": cot, "answer": answer})
        data_div_n_m.append(get_data_format(prompt=question, response=cot, from_type="self-generate", domain=["Math", "Division_n_m"]))

    return data_div_n_m

def Division_n_m(datatype="train"):
    # Division n/m with dividend<=12 digits and quotient<=7 digits
    # pairs represent (dividend, divisor)
    n = 1
    if datatype == "valid" or datatype == "test":
        n = 100
    pairs = \
        [(random.randint(10**(j-1)+1, 10**j), random.randint(10**(i-1)+1, 10**i)) for i in range(2, 7) for j in range(i+1, i+7) for k in range(int(10000/n))] +\
        [(random.randint(10**(j-1)+1, 10**j), random.randint(10**(i-1)+1, 10**i)) for i in range(2, 7) for j in range(2, i+7) for k in range(int(1000/n))]

    random.shuffle(pairs)

    print("Division n/m:", len(pairs))

    data_div_n_m = []

    # pairs = [(random.randint(10, 100), random.randint(1, 100))]
    for num1, num2 in pairs:

        quotient = num1 // num2
        remainder = num1 % num2

        # make it divisible with 0.5 probability
        if num1 > num2 and random.random()<0.5: 
            num1 = num1 - remainder
            quotient = num1 // num2
            remainder = num1 % num2

        question = f"{num1} / {num2}" 

        if quotient == 0:
            cot = f"{num1} / {num2} = {quotient} R {remainder}"
            answer = f"{quotient} R {remainder}"
            assert(cot.split()[-1] == answer.split()[-1])

            max_digits_after_decimal_point = 4
            decimal_round = 0
            answer_decimal = round(num1 / num2, max_digits_after_decimal_point)
            step = ""
            cot2 = ""
            left = remainder
            computed_answer = quotient
            while decimal_round <= max_digits_after_decimal_point:
                left = left * 10
                quotient_dec = left // num2
                answer = num2 * quotient_dec
                new_left = left - answer
                step = f"{left} - {num2} * {quotient_dec} = {left} - {answer} = {new_left}"
                cot2 = cot2 + step + "\n"
                left = new_left
                decimal_round += 1
                computed_answer = computed_answer + quotient_dec/(10**decimal_round)
                if left == 0:
                    break
            computed_answer = round(computed_answer, max_digits_after_decimal_point)
            assert(abs(round(answer_decimal - computed_answer, max_digits_after_decimal_point)) <= 0.0001), f"{answer_decimal} vs {computed_answer}"
            decimal_digits = min(decimal_round, max_digits_after_decimal_point)
            cot = f"{cot}\n{cot2}\n因此，{question} = {quotient} R {remainder}，即商为{quotient}，余数为{remainder}。\n小数点后保留{decimal_digits}位有效数字：{question} = {computed_answer}"

        elif num1 == num2:
            cot = f"{num1} / {num2} = {quotient}"
            answer = f"{quotient}"        

        else:
            step = ""
            cot = ""
            left = num1

            i = 0
            computed_q = 0

            while left>=num2:
                if int(str(quotient)[i])!=0:
                    intermediate = int(str(quotient)[i] + "0" * (len(str(quotient))-1-i))
                    answer = num2 * intermediate
                    new_left = left - answer
                    step = f"{left} - {num2} * {intermediate} = {left} - {answer} = {new_left}\n"
                    cot = cot + step                   
                    left = new_left
                    computed_q = computed_q + intermediate

                i = i+1

            assert(left == remainder)
            assert(computed_q == quotient)

            if remainder == 0:
                cot = cot + f"因此, {num1} / {num2} = {quotient}"
                answer = f"{quotient}"
                assert(cot.split()[-1] == answer.split()[-1])
            else:
                cot = cot #+ f"因此, {num1} / {num2} = {quotient} R {remainder}"
                answer = f"{quotient} R {remainder}"
                assert(cot.split()[-1] == answer.split()[-1])
                
                max_digits_after_decimal_point = 4
                decimal_round = 0
                answer_decimal = round(num1 / num2, max_digits_after_decimal_point)
                step = ""
                cot2 = ""
                left = remainder
                computed_answer = quotient
                while decimal_round <= max_digits_after_decimal_point:
                    left = left * 10
                    quotient_dec = left // num2
                    answer = num2 * quotient_dec
                    new_left = left - answer
                    step = f"{left} - {num2} * {quotient_dec} = {left} - {answer} = {new_left}"
                    cot2 = cot2 + step + "\n"
                    left = new_left
                    decimal_round += 1
                    computed_answer = computed_answer + quotient_dec/(10**decimal_round)
                    if left == 0:
                        break
                computed_answer = round(computed_answer, max_digits_after_decimal_point)
                assert(abs(round(answer_decimal - computed_answer, max_digits_after_decimal_point)) <= 0.0001), f"{answer_decimal} vs {computed_answer}"
                decimal_digits = min(decimal_round, max_digits_after_decimal_point)
                cot = f"{cot}\n{cot2}\n因此，{question} = {quotient} R {remainder}，即商为{quotient}，余数为{remainder}。\n小数点后保留{decimal_digits}位有效数字：{question} = {computed_answer}"

        # data_div_n_m.append({"input": question, "output": cot, "answer": answer})
        data_div_n_m.append(get_data_format(prompt=question, response=cot, from_type="self-generate", domain=["Math", "Division_n_m"]))

    return data_div_n_m

def Division_n_m_neg(datatype="train"):
    # Division n/m with dividend<=12 digits and quotient<=7 digits
    # pairs represent (dividend, divisor)
    n = 1
    if datatype == "valid" or datatype == "test":
        n = 100
    pairs = \
        [(random.randint(10**(j-1)+1, 10**j), random.randint(10**(i-1)+1, 10**i)) for i in range(2, 7) for j in range(i+1, i+7) for k in range(int(10000/n))] +\
        [(random.randint(10**(j-1)+1, 10**j), random.randint(10**(i-1)+1, 10**i)) for i in range(2, 7) for j in range(2, i+7) for k in range(int(1000/n))]

    random.shuffle(pairs)

    print("Division n/m:", len(pairs))

    data_div_n_m = []

    # pairs = [(random.randint(10, 100), random.randint(1, 100))]
    for num1, num2 in pairs:

        quotient = num1 // num2
        remainder = num1 % num2

        # make it divisible with 0.5 probability
        if num1 > num2 and random.random()<0.5: 
            num1 = num1 - remainder
            quotient = num1 // num2
            remainder = num1 % num2

        if random.random() < 0.33:
            num1 = -num1
            if random.random() < 0.5:
                question = f"{num1} / {num2}" 
            else:
                question = f"({num1}) / {num2}"
            quotient = -quotient
            remainder = -remainder
        elif 0.33 <= random.random() < 0.66:
            num2 = -num2
            question = f"{num1} / ({num2})" 
            quotient = -quotient
            remainder = -remainder
        else:
            num1 = -num1
            num2 = -num2
            if random.random() < 0.5:
                question = f"{num1} / ({num2})" 
            else:
                question = f"({num1}) / ({num2})"

        # question = f"{num1} / {num2}" 
        src_num1, src_num2 = num1, num2
        if quotient == 0:
            cot = f"{question} = {quotient} R {remainder}"
            answer = f"{quotient} R {remainder}"
            assert(cot.split()[-1] == answer.split()[-1])

            max_digits_after_decimal_point = 4
            decimal_round = 0
            answer_decimal = round(num1 / num2, max_digits_after_decimal_point)
            step = ""
            cot2 = ""
            left = remainder
            computed_answer = quotient
            while decimal_round <= max_digits_after_decimal_point:
                left, num2 = abs(left), abs(num2)
                left = left * 10
                quotient_dec = left // num2
                answer = num2 * quotient_dec
                new_left = left - answer
                decimal_round += 1
                if (src_num1 > 0 and src_num2 > 0) or (src_num1 < 0 and src_num2 < 0):
                    step = f"{left} - {num2} * {quotient_dec} = {left} - {answer} = {new_left}"
                    computed_answer = computed_answer + quotient_dec/(10**decimal_round)
                elif (src_num1 > 0 and src_num2 < 0) or (src_num1 < 0 and src_num2 > 0):
                    step = f"- ({left} - {num2} * {quotient_dec}) = - ({left} - {answer}) = -{new_left}"
                    computed_answer = computed_answer - quotient_dec/(10**decimal_round)
                cot2 = cot2 + step + "\n"
                left = new_left
                if left == 0:
                    break
            computed_answer = round(computed_answer, max_digits_after_decimal_point)
            assert(abs(round(answer_decimal - computed_answer, max_digits_after_decimal_point)) <= 0.0001), f"{answer_decimal} vs {computed_answer}"
            decimal_digits = min(decimal_round, max_digits_after_decimal_point)
            cot = f"{cot}\n{cot2}\n因此，{question} = {quotient} R {remainder}，即商为{quotient}，余数为{remainder}。\n小数点后保留{decimal_digits}位有效数字：{question} = {computed_answer}"

        elif abs(num1) == abs(num2):
            cot = f"{question} = {quotient}"
            answer = f"{quotient}"        

        else:
            step = ""
            cot = ""
            left = num1

            i = 0
            computed_q = 0

            left, num2 = abs(left), abs(num2)
            if quotient < 0:
                i = 1
            while left >= num2:
                if int(str(quotient)[i])!=0:
                    intermediate = int(str(quotient)[i] + "0" * (len(str(quotient))-1-i))
                    answer = num2 * intermediate
                    new_left = left - answer
                    if (src_num1 > 0 and src_num2 > 0) or (src_num1 < 0 and src_num2 < 0):
                        step = f"{left} - {num2} * {intermediate} = {left} - {answer} = {new_left}\n"
                        computed_q = computed_q + intermediate
                    elif (src_num1 > 0 and src_num2 < 0) or (src_num1 < 0 and src_num2 > 0):
                        step = f"- ({left} - {num2} * {intermediate}) = - ({left} - {answer}) = -{new_left}\n"
                        computed_q = computed_q - intermediate
                    cot = cot + step                   
                    left = new_left
                    # computed_q = computed_q + intermediate
                i = i+1

            assert(abs(left) == abs(remainder)), f"{left} vs {remainder}"
            assert(computed_q == quotient), f"{computed} vs {quotient}"

            if remainder == 0:
                cot = cot + f"因此, {num1} / {num2} = {quotient}"
                answer = f"{quotient}"
                assert(cot.split()[-1] == answer.split()[-1])
            else:
                cot = cot #+ f"因此, {num1} / {num2} = {quotient} R {remainder}"
                answer = f"{quotient} R {remainder}"
                assert(cot.split()[-1] == answer.split()[-1])
                
                max_digits_after_decimal_point = 4
                decimal_round = 0
                answer_decimal = round((src_num1) / (src_num2), max_digits_after_decimal_point)
                step = ""
                cot2 = ""
                left = remainder
                computed_answer = quotient
                while decimal_round <= max_digits_after_decimal_point:
                    left, num2 = abs(left), abs(num2)
                    left = left * 10
                    quotient_dec = left // num2
                    answer = num2 * quotient_dec
                    new_left = left - answer
                    decimal_round += 1
                    if (src_num1 > 0 and src_num2 > 0) or (src_num1 < 0 and src_num2 < 0):
                        step = f"{left} - {num2} * {quotient_dec} = {left} - {answer} = {new_left}"
                        computed_answer = computed_answer + quotient_dec/(10**decimal_round)
                    elif (src_num1 > 0 and src_num2 < 0) or (src_num1 < 0 and src_num2 > 0):
                        step = f"- ({left} - {num2} * {quotient_dec}) = - ({left} - {answer}) = -{new_left}"
                        computed_answer = computed_answer - quotient_dec/(10**decimal_round)
                    cot2 = cot2 + step + "\n"
                    left = new_left
                    if left == 0:
                        break
                computed_answer = round(computed_answer, max_digits_after_decimal_point)
                assert(abs(round(answer_decimal - computed_answer, max_digits_after_decimal_point)) <= 0.0001), f"{answer_decimal} vs {computed_answer}"
                decimal_digits = min(decimal_round, max_digits_after_decimal_point)
                cot = f"{cot}\n{cot2}\n因此，{question} = {quotient} R {remainder}，即商为{quotient}，余数为{remainder}。\n小数点后保留{decimal_digits}位有效数字：{question} = {computed_answer}"
        data_div_n_m.append(get_data_format(prompt=question, response=cot, from_type="self-generate", domain=["Math", "Division_n_m"]))

    return data_div_n_m

# TODO
def Division_n_m_dec(datatype="train"):
    # Division n/m with dividend<=12 digits and quotient<=7 digits
    # pairs represent (dividend, divisor)
    n = 1
    if datatype == "valid" or datatype == "test":
        n = 100
    pairs = \
        [(random.randint(10**(j-1)+1, 10**j), random.randint(10**(i-1)+1, 10**i)) for i in range(2, 7) for j in range(i+1, i+7) for k in range(int(10000/n))] +\
        [(random.randint(10**(j-1)+1, 10**j), random.randint(10**(i-1)+1, 10**i)) for i in range(2, 7) for j in range(2, i+7) for k in range(int(1000/n))]

    random.shuffle(pairs)

    print("Division n/m:", len(pairs))

    data_div_n_m = []

    # pairs = [(random.randint(10, 100), random.randint(1, 100))]
    for num1, num2 in pairs:

        quotient = num1 // num2
        remainder = num1 % num2

        # make it divisible with 0.5 probability
        if num1 > num2 and random.random()<0.5: 
            num1 = num1 - remainder
            quotient = num1 // num2
            remainder = num1 % num2

        if random.random() < 0.33:
            num1 = -num1
            if random.random() < 0.5:
                question = f"{num1} / {num2}" 
            else:
                question = f"({num1}) / {num2}"
            quotient = -quotient
            remainder = -remainder
        elif 0.33 <= random.random() < 0.66:
            num2 = -num2
            question = f"{num1} / ({num2})" 
            quotient = -quotient
            remainder = -remainder
        else:
            num1 = -num1
            num2 = -num2
            if random.random() < 0.5:
                question = f"{num1} / ({num2})" 
            else:
                question = f"({num1}) / ({num2})"

        # question = f"{num1} / {num2}" 
        src_num1, src_num2 = num1, num2
        if quotient == 0:
            cot = f"{question} = {quotient} R {remainder}"
            answer = f"{quotient} R {remainder}"
            assert(cot.split()[-1] == answer.split()[-1])

            max_digits_after_decimal_point = 4
            decimal_round = 0
            answer_decimal = round(num1 / num2, max_digits_after_decimal_point)
            step = ""
            cot2 = ""
            left = remainder
            computed_answer = quotient
            while decimal_round <= max_digits_after_decimal_point:
                left, num2 = abs(left), abs(num2)
                left = left * 10
                quotient_dec = left // num2
                answer = num2 * quotient_dec
                new_left = left - answer
                decimal_round += 1
                if (src_num1 > 0 and src_num2 > 0) or (src_num1 < 0 and src_num2 < 0):
                    step = f"{left} - {num2} * {quotient_dec} = {left} - {answer} = {new_left}"
                    computed_answer = computed_answer + quotient_dec/(10**decimal_round)
                elif (src_num1 > 0 and src_num2 < 0) or (src_num1 < 0 and src_num2 > 0):
                    step = f"- ({left} - {num2} * {quotient_dec}) = - ({left} - {answer}) = -{new_left}"
                    computed_answer = computed_answer - quotient_dec/(10**decimal_round)
                cot2 = cot2 + step + "\n"
                left = new_left
                if left == 0:
                    break
            computed_answer = round(computed_answer, max_digits_after_decimal_point)
            assert(abs(round(answer_decimal - computed_answer, max_digits_after_decimal_point)) <= 0.0001), f"{answer_decimal} vs {computed_answer}"
            decimal_digits = min(decimal_round, max_digits_after_decimal_point)
            cot = f"{cot}\n{cot2}\n因此，{question} = {quotient} R {remainder}，即商为{quotient}，余数为{remainder}。\n小数点后保留{decimal_digits}位有效数字：{question} = {computed_answer}"

        elif abs(num1) == abs(num2):
            cot = f"{question} = {quotient}"
            answer = f"{quotient}"        

        else:
            step = ""
            cot = ""
            left = num1

            i = 0
            computed_q = 0

            left, num2 = abs(left), abs(num2)
            if quotient < 0:
                i = 1
            while left >= num2:
                if int(str(quotient)[i])!=0:
                    intermediate = int(str(quotient)[i] + "0" * (len(str(quotient))-1-i))
                    answer = num2 * intermediate
                    new_left = left - answer
                    if (src_num1 > 0 and src_num2 > 0) or (src_num1 < 0 and src_num2 < 0):
                        step = f"{left} - {num2} * {intermediate} = {left} - {answer} = {new_left}\n"
                        computed_q = computed_q + intermediate
                    elif (src_num1 > 0 and src_num2 < 0) or (src_num1 < 0 and src_num2 > 0):
                        step = f"- ({left} - {num2} * {intermediate}) = - ({left} - {answer}) = -{new_left}\n"
                        computed_q = computed_q - intermediate
                    cot = cot + step                   
                    left = new_left
                    # computed_q = computed_q + intermediate
                i = i+1

            assert(abs(left) == abs(remainder)), f"{left} vs {remainder}"
            assert(computed_q == quotient), f"{computed} vs {quotient}"

            if remainder == 0:
                cot = cot + f"因此, {num1} / {num2} = {quotient}"
                answer = f"{quotient}"
                assert(cot.split()[-1] == answer.split()[-1])
            else:
                cot = cot #+ f"因此, {num1} / {num2} = {quotient} R {remainder}"
                answer = f"{quotient} R {remainder}"
                assert(cot.split()[-1] == answer.split()[-1])
                
                max_digits_after_decimal_point = 4
                decimal_round = 0
                answer_decimal = round((src_num1) / (src_num2), max_digits_after_decimal_point)
                step = ""
                cot2 = ""
                left = remainder
                computed_answer = quotient
                while decimal_round <= max_digits_after_decimal_point:
                    left, num2 = abs(left), abs(num2)
                    left = left * 10
                    quotient_dec = left // num2
                    answer = num2 * quotient_dec
                    new_left = left - answer
                    decimal_round += 1
                    if (src_num1 > 0 and src_num2 > 0) or (src_num1 < 0 and src_num2 < 0):
                        step = f"{left} - {num2} * {quotient_dec} = {left} - {answer} = {new_left}"
                        computed_answer = computed_answer + quotient_dec/(10**decimal_round)
                    elif (src_num1 > 0 and src_num2 < 0) or (src_num1 < 0 and src_num2 > 0):
                        step = f"- ({left} - {num2} * {quotient_dec}) = - ({left} - {answer}) = -{new_left}"
                        computed_answer = computed_answer - quotient_dec/(10**decimal_round)
                    cot2 = cot2 + step + "\n"
                    left = new_left
                    if left == 0:
                        break
                computed_answer = round(computed_answer, max_digits_after_decimal_point)
                assert(abs(round(answer_decimal - computed_answer, max_digits_after_decimal_point)) <= 0.0001), f"{answer_decimal} vs {computed_answer}"
                decimal_digits = min(decimal_round, max_digits_after_decimal_point)
                cot = f"{cot}\n{cot2}\n因此，{question} = {quotient} R {remainder}，即商为{quotient}，余数为{remainder}。\n小数点后保留{decimal_digits}位有效数字：{question} = {computed_answer}"
        data_div_n_m.append(get_data_format(prompt=question, response=cot, from_type="self-generate", domain=["Math", "Division_n_m"]))

    return data_div_n_m

def Division_3d(datatype="train"):
    # Division n/1, with n up to 16 digits
    # pairs represent (divisor, quotient)
    n = 1
    if datatype == "valid" or datatype == "test":
        n = 100
    pairs = \
        [(i, j) for i in range(0, 100) for j in range(0, 100) for k in range(5)] + \
        [(random.randint(100, 1000), random.randint(100, 1000)) for k in range(50000)]
    
    random.shuffle(pairs)
    if datatype == "valid" or datatype == "test":
        pairs = random.sample(pairs, 2000)
    
    print("Division n/m 3d:", len(pairs))

    data_div_3d = []
    for num1, num2 in pairs:
        if num2 == 0:
            question = f"{num1} / {num2}" 
            answer = question + "存在错误，除数不能位0。"
            data_div_3d.append(get_data_format(prompt=question, response=answer, from_type="self-generate", domain=["Math", "Division_n_1"]))
            continue

        question = f"{num1} / {num2}"
        answer = round((num1/num2), 4)
        response = str(answer)
        data_div_3d.append(get_data_format(prompt=question, response=response, from_type="self-generate", domain=["Math", "Division_n_m_3d"]))
    
    return data_div_3d

def Division_3d_negative(datatype="train"):
    # Division n/1, with n up to 16 digits
    # pairs represent (divisor, quotient)
    n = 1
    if datatype == "valid" or datatype == "test":
        n = 100
    pairs = \
        [(i, j) for i in range(0, 100) for j in range(0, 100) for k in range(5)] + \
        [(random.randint(100, 1000), random.randint(100, 1000)) for k in range(50000)]
    
    print("Division n/m 3d:", len(pairs))

    data_div_3d_negative = []
    for num1, num2 in pairs:
        question = f"{num1} / {num2}"
        answer = round((num1/num2), 4)
        response = str(answer)
        data_div_3d_negative.append(get_data_format(prompt=question, response=response, from_type="self-generate", domain=["Math", "Division_n_m_3d"]))
    
    return data_div_3d_negative


def get_Exp_CoT(num, exp, question, answer):
    if num>=0 or exp%2==0:
        src_num = num
        num = abs(num)
        num_digits = len(str(num))
        if src_num < 0:
            convert = (f"{num} ** {exp}") if "**" in question else (f"{num} ^ {exp}")
        if num % (10 ** (num_digits-1)) == 0 :
            if exp == 0 or exp == 1 or num==0 or num==1:
                cot = question + " = " + str(answer)
            elif exp == 2:
                cot = (question + " = " + str(answer)) if src_num>=0 else (question + "\n= " + convert + "\n= " + str(answer))
            else:
                multiplication_terms = [num for i in range(exp)]
                step = " * ".join([f"{x}" for x in multiplication_terms]) + "\n= "
                while multiplication_terms:
                    first = multiplication_terms.pop(0)
                    if not multiplication_terms:
                        output = first
                        break 
                    multiplication_terms[0] = multiplication_terms[0] * first
                    step = step + " * ".join([f"{x}" for x in multiplication_terms])
                    if len(multiplication_terms) >= 2:
                        step = step + "\n= "
                if src_num>=0:
                    cot = question + "\n= " + step + f"\n因此，{question} = {answer}"
                else:
                    cot = question + f"\n= {convert}" + "\n= " + step + f"\n因此，{question} = {answer}"
        else:
            if exp == 0 or exp == 1:
                cot = question + " = " + str(answer)
            elif exp == 2:
                sub_question = f"{num} * {num}"
                sub_cot = get_Mul_CoT(num, num, sub_question, answer)
                cot = (question + "\n= " + sub_cot) if src_num>=0 else (question + "\n= " + convert + "\n= " + sub_cot)
            else:
                multiplication_terms = [num for i in range(exp)]
                step = " * ".join([f"{x}" for x in multiplication_terms]) + "\n= "
                step_list = []
                while multiplication_terms:
                    first = multiplication_terms.pop(0)
                    if not multiplication_terms:
                        output = first
                        break 
                    num1, num2 = first, multiplication_terms[0]
                    sub_question = f"{num1} * {num2}"
                    sub_answer = num1 * num2
                    sub_cot = get_Mul_CoT(num1, num2, sub_question, sub_answer)
                    for sub_cot_line in "".join(sub_cot.split("因此")[:-1]).split("\n="):
                        sub_cot_line = sub_cot_line.strip()
                        if len(multiplication_terms) >= 2:
                            sub_step_line = f"({sub_cot_line})" + " * " + " * ".join([f"{x}" for x in multiplication_terms[1:]])
                        else:
                            sub_step_line = sub_cot_line
                        step_list.append(sub_step_line)
                    multiplication_terms[0] = sub_answer
                step = step + "\n= ".join([f"{x}" for x in step_list])
                if src_num>=0:
                    cot = question + "\n= " + step + f"\n因此，{question} = {answer}"
                else:
                    cot = question + f"\n= {convert}"  + "\n= " + step + f"\n因此，{question} = {answer}" 
    else:
        num = abs(num)
        num_digits = len(str(num))
        convert = (f"- ({num} ** {exp})") if "**" in question else (f"- ({num} ^ {exp})")
        if num % (10 ** (num_digits-1)) == 0 :
            if exp == 1 or num == 1:
                cot = question + " = " + str(answer)
            else:
                multiplication_terms = [num for i in range(exp)]
                step = "- (" + " * ".join([f"{x}" for x in multiplication_terms]) + ")\n= " 
                while multiplication_terms:
                    first = multiplication_terms.pop(0)
                    if not multiplication_terms:
                        output = first
                        break 
                    multiplication_terms[0] = multiplication_terms[0] * first
                    if len(multiplication_terms) > 1:
                        step = step + "- (" + " * ".join([f"{x}" for x in multiplication_terms]) + ")"
                    else:
                        step = step + "-" + " * ".join([f"{x}" for x in multiplication_terms])
                    if len(multiplication_terms) >= 2:
                        step = step + "\n= "
                cot = question + f"\n= {convert}" + "\n= " + step + f"\n因此，{question} = {answer}"
        else:
            if exp == 1:
                cot = question + " = " + str(answer)
            else:
                multiplication_terms = [num for i in range(exp)]
                step = "- (" + " * ".join([f"{x}" for x in multiplication_terms]) + ")\n= " 
                step_list = []
                while multiplication_terms:
                    first = multiplication_terms.pop(0)
                    if not multiplication_terms:
                        output = first
                        break 
                    num1, num2 = first, multiplication_terms[0]
                    sub_question = f"{num1} * {num2}"
                    sub_answer = num1 * num2
                    sub_cot = get_Mul_CoT(num1, num2, sub_question, sub_answer)
                    for idx, sub_cot_line in enumerate("".join(sub_cot.split("因此")[:-1]).split("\n=")):
                        sub_cot_line = sub_cot_line.strip()
                        if len(multiplication_terms) >= 2:
                            sub_step_line = "- (" + f"({sub_cot_line})" + " * " + " * ".join([f"{x}" for x in multiplication_terms[1:]]) + ")"
                        else:
                            if idx != len("".join(sub_cot.split("因此")[:-1]).split("\n=")) - 1:
                                sub_step_line = f"- ({sub_cot_line})"
                            else:
                                sub_step_line = f"-{sub_cot_line}"
                        step_list.append(sub_step_line)
                    multiplication_terms[0] = sub_answer
                step = step + "\n= ".join([f"{x}" for x in step_list])
                cot = question + f"\n= {convert}" + "\n= " + step + f"\n因此，{question} = {answer}"
    return cot

def Exponential(datatype="train"):
    # multi-digit Exponential
    n = 1
    if datatype == "train":
        pairs = \
            [(i, j) for i in range(100) for j in range(0,5) for k in range(100)] +\
            [(i, j) for i in range(100, 1000) for j in range(0,4) for k in range(10)] +\
            [(random.randint(10**i, 10**(i+1)-1), random.randint(0, 2)) for i in range(4,10) for k in range(5000)]
    elif datatype == "valid" or datatype == "test":
        pairs = \
            [(i, j) for i in range(100) for j in range(0,5) for k in range(1)] +\
            [(random.randint(100, 999), random.randint(0,3)) for k in range(500)] +\
            [(random.randint(10**i, 10**(i+1)-1), random.randint(0, 2)) for i in range(4,10) for k in range(500)]
    else:
        raise ValueError("Invalid data type")

    random.shuffle(pairs)

    print("Exponential n ^ m:", len(pairs))

    data_exp = []

    for num, exp in pairs:
        if random.random() < 0.5:
            num = -1 * num
        if num >= 0:
            question = f"{num} ^ {exp}"
        else:
            question = f"({num}) ^ {exp}"
        answer = (num) ** exp
        cot = get_Exp_CoT(num, exp, question, answer)
        assert(float(cot.split("=")[-1].strip())) == float(answer)
        data_exp.append(get_data_format(prompt=question, response=cot, from_type="self-generate", domain=["Math", "Exponential"]))
    
    return data_exp

# TODO
def Exponential_dec():
    pass


# TODO
def MathematicalSymbol():
    Symbol_to_Number = {
        "e" : 2.71828,
        "pi" : 3.14159,
        "π" : 3.14159,
        "Eulr" : "e^(iπ) = -1",
    }
    oprators = ["+", "-", "*", "/", "^"]
    return 


# TODO
def Complex_Four_Arithmetic_Operations():
    pass


# TODO
def Trigonometric():
    pass


# TODO
def Log():
    pass


def Add_NatureLanguage(data_original, template):
    data_converted = []

    for instance in data_original:
        arithmetic = instance["data"][0]["prompt"]
        response = instance["data"][0]["response"][0][0]

        # add noise to instruction so that the model is robust to diverse question formats 
        if random.random() < 0.05:
            if " + " in arithmetic:
                arithmetic = arithmetic.replace("+", "和") + "的和"
            if " - " in arithmetic:
                # arithmetic = arithmetic.replace("-", "和") + "的差"
                if not arithmetic.startswith("-"):
                    if ") -" in arithmetic:
                        arithmetic = arithmetic.replace(") -", ") 和") + "的差"
                    elif "- (" in arithmetic:
                        arithmetic = arithmetic.replace("- (", "和 (") + "的差"
                    elif ") - (" in arithmetic:
                        arithmetic = arithmetic.replace(") - (", ") 和 (") + "的差"
                    else:
                        arithmetic = re.sub(r'(?<![e(])-', '和', arithmetic) + "的差"
                else:
                    arithmetic = arithmetic[1:]
                    if ") -" in arithmetic:
                        arithmetic = "-" + arithmetic.replace(") -", ") 和") + "的差"
                    elif "- (" in arithmetic:
                        arithmetic = "-" + arithmetic.replace("- (", "和 (") + "的差"
                    elif ") - (" in arithmetic:
                        arithmetic = "-" + arithmetic.replace(") - (", ") 和 (") + "的差"
                    else:
                        arithmetic = "-" + re.sub(r'(?<![e(])-', '和', arithmetic) + "的差"
            if " * " in arithmetic:
                arithmetic = arithmetic.replace("*", "和") + "的积"
            if " / " in arithmetic:
                arithmetic = arithmetic.replace("/", "和") + "的商和余数"
            if " ^ " in arithmetic:
                if " ^ 2" in arithmetic:
                    if random.random() < 0.6:
                        arithmetic = arithmetic.replace(" ^ 2", "的平方")
                    else:
                        arithmetic = arithmetic.replace(" ^ 2", "的二次方")
                elif " ^ 3" in arithmetic:
                    arithmetic = arithmetic.replace(" ^ 3", "的三次方")
                elif " ^ 4" in arithmetic:
                    arithmetic = arithmetic.replace(" ^ 4", "的四次方")
                else:
                    pass

        if random.random() < 0.3:
            arithmetic = arithmetic.replace("*", "x")
            arithmetic = arithmetic.replace("/", "÷")

        if random.random() < 0.1:
            if not arithmetic.startswith("-"):
                # arithmetic = arithmetic.replace("+", "加").replace("-", "减")
                arithmetic = re.sub(r'(?<![e(])-', '减', arithmetic.replace("+", "加"))
            else:
                arithmetic = arithmetic[1:]
                arithmetic = "-" + re.sub(r'(?<![e(])-', '减', arithmetic.replace("+", "加"))
            arithmetic = arithmetic.replace("x", "乘").replace("*", "乘").replace("/", "除以").replace("÷", "除以")

        if random.random() < 0.7:
            arithmetic = arithmetic.replace("^", "**")
            response = response.replace("^", "**")

        if random.random() < 0.5:
            if "+" in arithmetic or "-" in arithmetic or "*" in arithmetic or "/" in arithmetic or "x" in arithmetic or "÷" in arithmetic:
                arithmetic = arithmetic.replace(" ", "")        

        num = random.randint(0, len(template)-1)
        prompt_converted = template[num].format(
            prompt = arithmetic
        )

        instance["data"][0]["prompt"] = prompt_converted
        instance["data"][0]["response"][0][0] = response
        data_converted.append(instance)

    print("Original:", len(data_original))
    print("Total:", len(data_converted))
    return data_converted


def main():
    data_to_func = {
        "addition": Addition,
        "addition_2d": Addition_2d,
        "addition_neg": Addition_neg,
        "addition_decimal": Addition_decimal,
        "subtraction": Subtraction,
        "subtraction_neg": Subtraction_neg,
        "subtraction_decimal": Subtraction_decimal,
        "multiplication_n_1": Multiplication_n_1,
        "multiplication_n_m": Multiplication_n_m,
        "multiplication_n_1_neg": Multiplication_n_1_neg,
        "multiplication_n_m_neg": Multiplication_n_m_neg,
        "multiplication_n_1_dec": Multiplication_n_1_dec,
        "multiplication_n_m_dec": Multiplication_n_m_dec,
        "division_n_1": Division_n_1,
        "division_n_m": Division_n_m,
        "division_n_1_neg": Division_n_1_neg,
        "division_n_m_neg": Division_n_m_neg,
        "division_3d": Division_3d,
        "exponential": Exponential,
    }
    data_type = ["train", "valid"]
    oprators = ["division_n_m_neg"]
    for op in oprators:
        for datatype in data_type:
            data_all = Add_NatureLanguage(data_to_func[op](datatype), template_prompt())
            with open(f"Generate-Math/{op}_{datatype}.json", "w") as f:
                for data in data_all:
                    f.write(json.dumps(data, ensure_ascii=False)+"\n")


def unit_test():
    ##  get_Mul_Dec_CoT
    # num1 = 83225.7
    # num2 = -10.1
    # question = f"{num1} * {num2}"
    # answer = round(num1 * num2, len(str(num1).split(".")[-1])+len(str(num2).split(".")[-1]))
    # cot = get_Mul_Dec_CoT(num1, num2, question, answer)
    # print(cot)

    Division_n_m_neg()

if __name__ == "__main__":

    main()
    # unit_test()
