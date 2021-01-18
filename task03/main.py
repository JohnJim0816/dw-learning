#!/usr/bin/env python
# coding=utf-8
'''
Author: John
Email: johnjim0816@gmail.com
Date: 2021-01-18 13:02:04
LastEditor: John
LastEditTime: 2021-01-18 15:24:04
Discription: 
Environment: 
'''
import sys,os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))) # 添加当前文件所在的父目录到sys.path
curr_dir = os.path.abspath(os.path.dirname(__file__))
import re
import json
import pandas as pd
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
                    tmp_dict = {'abstract':tmp_dict['abstract'],'categories': tmp_dict['categories'],'comments':tmp_dict['comments'],'update_date':tmp_dict["update_date"]}
                    data.append(tmp_dict)         
                    break
    df = pd.DataFrame(data) #将list变为dataframe格式，方便使用pandas进行分析
    # print(df.shape) #显示数据大小   
    df["year"] = pd.to_datetime(df["update_date"]).dt.year #将update_date从例如2019-02-20的str变为datetime格式，并提取处year
    del df["update_date"] #删除 update_date特征，其使命已完成
    ### 存储为csv ###
    df.to_csv(data_path+'.csv',index=None)

def count_pages(df):
    # 使用正则表达式匹配，XX pages
    df['pages'] = df['comments'].apply(lambda x: re.findall('[1-9][0-9]* pages', str(x)))

    # 筛选出有pages的论文
    df = df[df['pages'].apply(len) > 0]

    # 由于匹配得到的是一个list，如['19 pages']，需要进行转换
    df['pages'] = df['pages'].apply(lambda x: float(x[0].replace(' pages', '')))
    print(df['pages'].describe().astype(int))
    # 选择主要类别
    df['categories'] = df['categories'].apply(lambda x: x.split(' ')[0])
    df['categories'] = df['categories'].apply(lambda x: x.split('.')[0])

    # 每类论文的平均页数
    plt.figure(num=1,figsize=(12, 6))
    df.groupby(['categories'])['pages'].mean().plot(kind='bar')
    plt.show()
    
def count_figures(df):
    
    df['figures'] = df['comments'].apply(lambda x: re.findall('[1-9][0-9]* figures', str(x)))
    df = df[df['figures'].apply(len) > 0]
    df['figures'] = df['figures'].apply(lambda x: float(x[0].replace(' figures', '')))
    print(df['figures'])
    # 选择主要类别
    df['categories'] = df['categories'].apply(lambda x: x.split(' ')[0])
    df['categories'] = df['categories'].apply(lambda x: x.split('.')[0])
    plt.figure(num=2,figsize=(12, 6))
    df.groupby(['categories'])['figures'].mean().plot(kind='bar')
    plt.show()
    
def count_data_with_code(df):
    # 筛选包含github的论文
    data_with_code = df[
        (df.comments.str.contains('github')==True)|
                        (df.abstract.str.contains('github')==True)
    ]
    data_with_code['text'] = data_with_code['abstract'].fillna('') + data_with_code['comments'].fillna('')

    # 使用正则表达式匹配论文
    pattern = '[a-zA-z]+://github[^\s]*'
    data_with_code['code_flag'] = data_with_code['text'].str.findall(pattern).apply(len)
    data_with_code = data_with_code[data_with_code['code_flag'] == 1]
    # 选择主要类别
    data_with_code['categories'] = data_with_code['categories'].apply(lambda x: x.split(' ')[0])
    data_with_code['categories'] = data_with_code['categories'].apply(lambda x: x.split('.')[0])
    plt.figure(num=3,figsize=(12, 6))
    data_with_code.groupby(['categories'])['code_flag'].count().plot(kind='bar')
    plt.show()
if __name__ == "__main__":
    PATH  = data_alll_path
    pre_process(PATH)  # 首次分析时这行需要取消注释
    df = pd.read_csv(PATH+'.csv')
    # count_pages(df)
    # count_figures(df)
    # count_data_with_code(df)