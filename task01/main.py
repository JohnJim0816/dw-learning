#!/usr/bin/env python
# coding=utf-8
'''
Author: John
Email: johnjim0816@gmail.com
Date: 2021-01-11 10:56:31
LastEditor: John
LastEditTime: 2021-01-11 10:58:45
Discription: 
Environment: 
'''
import json
import pandas as pd
data_path = "arxiv-metadata-oai-2019.json"
data  = [] #初始化
#使用with语句优势：1.自动关闭文件句柄；2.自动显示（处理）文件读取数据异常
with open(data_path, 'r') as f: 
    for line in f: 
        data.append(json.loads(line))
        
data = pd.DataFrame(data) #将list变为dataframe格式，方便使用pandas进行分析
data.to_csv('arxiv-metadata-oai-2019.csv',index=None)
print(data.shape) #显示数据大小