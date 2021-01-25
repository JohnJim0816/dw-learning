#!/usr/bin/env python
# coding=utf-8
'''
Author: John
Email: johnjim0816@gmail.com
Date: 2021-01-25 13:45:51
LastEditor: John
LastEditTime: 2021-01-25 19:52:43
Discription: 
Environment: 
'''
import sys,os

from networkx.algorithms.traversal.depth_first_search import dfs_predecessors
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))) # 添加当前文件所在的父目录到sys.path
curr_dir = os.path.abspath(os.path.dirname(__file__))

import json
import pandas as pd
import ast 
import matplotlib.pyplot as plt
import networkx as nx

data_alll_path = curr_dir+"/data/arxiv-metadata-oai-snapshot"  # 包含所有年份的数据
def util_name_apply(authors):
    new_authors = []
    for author in authors:
        new_authors.append(author[:3]) # 由于可能出现如['Araya', 'Mauricio', '', 'LORIA/INRIA']中这种'LORIA/INRIA'类似于地区或者其他的无效字眼，所以需要筛除去前三项包含姓名的
    return new_authors

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
                    tmp_dict = {'authors_parsed': tmp_dict['authors_parsed']}
                    data.append(tmp_dict)         
                    break
    df = pd.DataFrame(data) #将list变为dataframe格式，方便使用pandas进行分析
    df['authors_parsed'] = df['authors_parsed'].apply(util_name_apply) 
    ### 存储为csv ###
    df.to_csv(data_path+'.csv',index=None)

def method1(df):
    df['authors_parsed'] = df['authors_parsed'].apply(lambda x: ast.literal_eval(x)[:3]) # 读取的str转list
    all_authors = sum(df['authors_parsed'], [])
    # 拼接所有的作者
    authors_names = [' '.join(x[:-1]) for x in all_authors]
    authors_names = pd.DataFrame(authors_names)
    top10_names= authors_names[0].value_counts().index.values[:10].tolist()
    print(top10_names)
    G = nx.Graph()
    n = 0
    for i in range(len(df)):
        authors = df.iloc[i]['authors_parsed']
        authors = [' '.join(x[:-1]) for x in authors]
        # print(authors)
        if list(set(authors)&set(top10_names)):
            n+=1
            for author in authors[1:]:
                G.add_edge(author[0],author)
    print(n)
    # 计算论文关系中有多少个联通子图
    print(len(nx.communicability(G)))
    nx.draw(G, with_labels=True)
    
    degree_sequence = sorted([d for n, d in G.degree()], reverse=True)
    dmax = max(degree_sequence)
    plt.loglog(degree_sequence, "b-", marker="o")
    plt.title("Degree rank plot")
    plt.ylabel("degree")
    plt.xlabel("rank")
    # draw graph in inset
    plt.axes([0.45, 0.45, 0.45, 0.45])
    Gcc = G.subgraph(sorted(nx.connected_components(G), key=len, reverse=True)[0])

    pos = nx.spring_layout(Gcc)
    plt.axis("off")
    nx.draw_networkx_nodes(Gcc, pos, node_size=20)
    nx.draw_networkx_edges(Gcc, pos, alpha=0.4)
    plt.show()
if __name__ == "__main__":
    PATH  = data_alll_path
    # pre_process(PATH)  # 首次分析时这行需要取消注释
    df = pd.read_csv(PATH+'.csv')
    method1(df)