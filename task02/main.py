#!/usr/bin/env python
# coding=utf-8
'''
Author: John
Email: johnjim0816@gmail.com
Date: 2021-01-13 11:00:00
LastEditor: John
LastEditTime: 2021-01-15 15:53:45
Discription: 
Environment: 
'''
import sys,os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))) # 添加当前文件所在的父目录到sys.path
curr_dir = os.path.abspath(os.path.dirname(__file__))

import json
import pandas as pd
import ast 
import matplotlib.pyplot as plt #画图工

data_alll_path = curr_dir+"/data/arxiv-metadata-oai-snapshot"  # 包含所有年份的数据

def pre_process(data_path):
    data_json_path = data_path + ".json"
    data  = [] #初始化
    #使用with语句优势：1.自动关闭文件句柄；2.自动显示（处理）文件读取数据异常
    with open(data_json_path, 'r') as f: 
        for line in f:
            tmp_dict = json.loads(line)
            key_words = ['Reinforcement Learning','reinforcement Learning','Reinforcement learning','reinforcement Learning']
            for key_word in key_words:
                if key_word in tmp_dict['title'] or key_word in tmp_dict['abstract']:
                    ### 合并作者姓名 ###
                    tmp_dict = {'id':tmp_dict['id'],'categories': tmp_dict['categories'],'update_date':tmp_dict["update_date"], 'authors_parsed': tmp_dict['authors_parsed']}
                    data.append(tmp_dict)         
                    break
    df = pd.DataFrame(data) #将list变为dataframe格式，方便使用pandas进行分析
    df["year"] = pd.to_datetime(df["update_date"]).dt.year #将update_date从例如2019-02-20的str变为datetime格式，并提取处year
    del df["update_date"] #删除 update_date特征，其使命已完成

    # print(df.shape) #显示数据大小   

    ### 存储为csv ###
    df.to_csv(data_path+'.csv',index=None)

def plot_top10_authors(df):
    df['authors_parsed'] = df['authors_parsed'].apply(lambda x: ast.literal_eval(x)) # 读取的str转list
    
    all_authors = sum(df['authors_parsed'], [])
    # 拼接所有的作者
    authors_names = [' '.join(x) for x in all_authors]
    authors_names = pd.DataFrame(authors_names)

    # 根据作者频率绘制直方图
    plt.figure(figsize=(10, 6))
    authors_names[0].value_counts().head(10).plot(kind='barh')

    # 修改图配置
    names = authors_names[0].value_counts().index.values[:10]
    _ = plt.yticks(range(0, len(names)), names)
    plt.ylabel('Author')
    plt.xlabel('Count')
    plt.show()

if __name__ == "__main__":
    PATH  = data_alll_path
    # pre_process(PATH)  # 首次分析时这行需要取消注释
    df = pd.read_csv(PATH+'.csv')
    plot_top10_authors(df)
    