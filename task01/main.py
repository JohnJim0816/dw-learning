#!/usr/bin/env python
# coding=utf-8
'''
Author: John
Email: johnjim0816@gmail.com
Date: 2021-01-11 10:56:31
LastEditor: John
LastEditTime: 2021-01-12 17:04:29
Discription: 
Environment: 
'''
import sys,os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))) # 添加当前文件所在的父目录到sys.path
curr_dir = os.path.abspath(os.path.dirname(__file__))

import seaborn as sns #用于画图
from bs4 import BeautifulSoup #用于爬取arxiv的数据
import re #用于正则表达式，匹配字符串的模式
import requests #用于网络连接，发送网络请求，使用域名获取对应信息
import json #读取数据，我们的数据为json格式的
import pandas as pd #数据处理，数据分析
import matplotlib.pyplot as plt #画图工


data2019_path = curr_dir+"/data/arxiv-metadata-oai-2019"
data_alll_path = curr_dir+"/data/arxiv-metadata-oai-snapshot"
def json2csv(data_path):
    data_json_path = data_path + ".json"
    data  = [] #初始化
    #使用with语句优势：1.自动关闭文件句柄；2.自动显示（处理）文件读取数据异常
    with open(data_json_path, 'r') as f: 
        for line in f:
            temp_dict = json.loads(line)
            key_words = ['Reinforcement Learning','reinforcement Learning','Reinforcement learning','reinforcement Learning']
            for key_word in key_words:
                if key_word in temp_dict['title'] or key_word in temp_dict['abstract']:
                    data.append(json.loads(line))
                    break
    df = pd.DataFrame(data) #将list变为dataframe格式，方便使用pandas进行分析

    ### 由于一些特征对后面的分析无关紧要，所以删除减小内存以便加快分析速度 ###
    del_cols = ['submitter','authors','comments','journal-ref','doi','report-no','license','versions','authors_parsed','title','abstract']
    df = df.drop(columns=del_cols) # 删除无关特征
    df["year"] = pd.to_datetime(df["update_date"]).dt.year #将update_date从例如2019-02-20的str变为datetime格式，并提取处year
    del df["update_date"] #删除 update_date特征，其使命已完成

    # print(df.shape) #显示数据大小   

    ### 存储为csv ###
    df.to_csv(data_path+'.csv',index=None)

def get_taxonomy():
    #爬取所有的类别
    website_url = requests.get('https://arxiv.org/category_taxonomy').text #获取网页的文本数据
    soup = BeautifulSoup(website_url,'lxml') #爬取数据，这里使用lxml的解析器，加速
    root = soup.find('div',{'id':'category_taxonomy_list'}) #找出 BeautifulSoup 对应的标签入口
    tags = root.find_all(["h2","h3","h4","p"], recursive=True) #读取 tags

    #初始化 str 和 list 变量
    level_1_name = ""
    level_1_names = []
    level_3_codes = []
    level_3_names = []
    #进行
    for t in tags:
        if t.name == "h2":
            level_1_name = t.text    
        elif t.name == "h3":
            pass
        elif t.name == "h4":
            raw = t.text
            level_3_code = re.sub(r"(.*) \((.*)\)",r"\1",raw)
            level_3_name = re.sub(r"(.*) \((.*)\)",r"\2",raw)
        elif t.name == "p":
            level_1_names.append(level_1_name)
            level_3_names.append(level_3_name)
            level_3_codes.append(level_3_code)
    #根据以上信息生成dataframe格式的数据
    df_taxonomy = pd.DataFrame({
    'group_name' : level_1_names,
    'category_name' : level_3_names,
    'categories' : level_3_codes,})
    #按照 "group_name" 进行分组，在组内使用 "archive_name" 进行排序
    df_taxonomy.groupby(["group_name","group_name"])
    return df_taxonomy

def plot_cato_dist(df,df_taxonomy):
    _df = df.merge(df_taxonomy, on="categories", how="left").drop_duplicates(["id","group_name"]).groupby("group_name").agg({"id":"count"}).sort_values(by="id",ascending=False).reset_index()
    fig = plt.figure(figsize=(15,12))
    
    plt.pie(_df["id"],  labels=_df["group_name"], autopct='%1.2f%%', startangle=160)
    plt.tight_layout()
    plt.show()

def plot_year_dist(df,df_taxonomy):
    group_name="Computer Science"
    cats = df.merge(df_taxonomy, on="categories").query("group_name == @group_name")
    cats = cats.groupby(["year","category_name"]).count().reset_index().pivot(index="category_name", columns="year",values="id")
    cats = cats.fillna(0)
    return cats

if __name__ == "__main__":
    PATH  = data_alll_path
    # json2csv(PATH)
    df_taxonomy = get_taxonomy()
    df = pd.read_csv(PATH+'.csv')

    ### 保留2016年后的数据 ###
    df = df[df["year"] >= 2017] #找出 year 中2016年以后的数据，并将其他数据删除
    # data.groupby(['categories','year']) #以 categories 进行排序，如果同一个categories 相同则使用 year 特征进行排序
    df.reset_index(drop=True, inplace=True) #重新编号

    cats = plot_year_dist(df,df_taxonomy)
    print(cats)

    