import sys,os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))) # 添加当前文件所在的父目录到sys.path
curr_dir = os.path.abspath(os.path.dirname(__file__))

import json
import pandas as pd
import matplotlib.pyplot as plt #画图工
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.metrics import classification_report
from keras.preprocessing.text import Tokenizer
from keras.preprocessing import sequence
# Keras Layers:
from keras.layers import Dense,Input,LSTM,Bidirectional,Activation,Conv1D,GRU
from keras.layers import Dropout,Embedding,GlobalMaxPooling1D, MaxPooling1D, Add, Flatten
from keras.layers import GlobalAveragePooling1D, GlobalMaxPooling1D, concatenate, SpatialDropout1D# Keras Callback Functions:
from keras.callbacks import Callback
from keras.callbacks import EarlyStopping,ModelCheckpoint
from keras import initializers, regularizers, constraints, optimizers, layers, callbacks
from keras.models import Model
from keras.optimizers import Adam

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
                    tmp_dict = {'title': tmp_dict['title'], 'categories': tmp_dict['categories'], 'abstract': tmp_dict['abstract']}
                    data.append(tmp_dict)         
                    break
    df = pd.DataFrame(data) #将list变为dataframe格式，方便使用pandas进行分析
    ### 为了方便数据的处理，将标题和摘要拼接一起完成分类 ###
    df['text'] = df['title']+df['abstract']
    df['text'] = df['text'].apply(lambda x: x.replace('\n',' '))
    df['text'] = df['text'].apply(lambda x: x.lower())
    df = df.drop(['abstract', 'title'], axis=1)

    ### 由于原始论文有可能有多个类别，所以选择一个主要类别 ###
    # 多个类别，包含子分类
    df['categories'] = df['categories'].apply(lambda x : x.split(' '))
    # 单个类别，不包含子分类
    df['categories_big'] = df['categories'].apply(lambda x : [xx.split('.')[0] for xx in x])
    # 去重并排序
    df['categories_big'] = df['categories_big'].apply(lambda x : sorted({}.fromkeys(x).keys()))        
    ### 存储为csv ###
    df.to_csv(data_path+'.csv',index=None)

def method1(data):
    '''直接使用TF-IDF对文本提取特征，使用分类器进行分类，分类器的选择上可以使用SVM、LR、XGboost等
    '''
    mlb = MultiLabelBinarizer()
    data_label = mlb.fit_transform(data['categories_big'].iloc[:])
    vectorizer = TfidfVectorizer(max_features=4000)
    data_tfidf = vectorizer.fit_transform(data['text'].iloc[:])
    # 划分训练集和验证集
    x_train, x_test, y_train, y_test = train_test_split(data_tfidf, data_label,
                                                 test_size = 0.2,random_state = 1)
    # 构建多标签分类模型
    clf = MultiOutputClassifier(MultinomialNB())
    clf = clf.fit(x_train, y_train)
    print(classification_report(y_test, clf.predict(x_test)))
    
def method2(data):
    '''FastText是入门款的词向量，利用Facebook提供的FastText工具，可以快速构建分类器
    '''
    mlb = MultiLabelBinarizer()
    data_label = mlb.fit_transform(data['categories_big'].iloc[:])
    print(data['categories_big'].iloc[:])
    x_train, x_test, y_train, y_test = train_test_split(data['text'].iloc[:], data_label,
                                                 test_size = 0.2,random_state = 1)
    # parameter
    max_features= 500
    max_len= 150
    embed_size=100
    batch_size = 128
    epochs = 5
    tokens = Tokenizer(num_words = max_features)
    tokens.fit_on_texts(list(x_train)+list(x_test))

    x_sub_train = tokens.texts_to_sequences(x_train)
    x_sub_test = tokens.texts_to_sequences(x_test)

    x_sub_train=sequence.pad_sequences(x_sub_train, maxlen=max_len)
    x_sub_test=sequence.pad_sequences(x_sub_test, maxlen=max_len)
    # LSTM model
    sequence_input = Input(shape=(max_len, ))
    x = Embedding(max_features, embed_size,trainable = False)(sequence_input)
    x = SpatialDropout1D(0.2)(x)
    x = Bidirectional(GRU(128, return_sequences=True,dropout=0.1,recurrent_dropout=0.1))(x)
    x = Conv1D(64, kernel_size = 3, padding = "valid", kernel_initializer = "glorot_uniform")(x)
    avg_pool = GlobalAveragePooling1D()(x)
    max_pool = GlobalMaxPooling1D()(x)
    x = concatenate([avg_pool, max_pool]) 
    preds = Dense(25, activation="sigmoid")(x) # 根据标签数更改

    model = Model(sequence_input, preds)
    model.compile(loss='binary_crossentropy',optimizer=Adam(lr=1e-3),metrics=['accuracy'])
    model.fit(x_sub_train, y_train, batch_size=batch_size, epochs=epochs)

if __name__ == "__main__":
    PATH  = data_alll_path
    # pre_process(PATH)  # 首次分析时这行需要取消注释
    data = pd.read_csv(PATH+'.csv')
    method1(data)
    # method2(data)
    

