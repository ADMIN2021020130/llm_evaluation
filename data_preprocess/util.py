import os

def count_token(data_list, weishu=4):
    count = 0
    for data in data_list:
        count += len(data["data"][0]["prompt"]) + len(data["data"][0]["response"][0][0])
    count_bill = round(float(count) / 1000000000.0, weishu)
    return count, count_bill

def check_format(data):
    if not "id" in data.keys():
        return False
    if not "data" in data.keys():
        return False
    if type(data["data"]) != list or (len(data["data"]) == 0) or (not "prompt" in data["data"][0].keys()):
        return False
    if not "response" in data["data"][0].keys():
        return False
    if type(data["data"][0]["response"]) != list or type(data["data"][0]["response"][0]) != list \
        or type(data["data"][0]["response"][0][0]) != str:
        return False
    return True