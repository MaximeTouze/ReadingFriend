import math
import os
import re
import fse
import gensim
import gensim.downloader as api
import nltk
import numpy as np
import pandas as pd
from fse import SplitIndexedList
from fse.models import uSIF
from nltk.corpus import stopwords
from sklearn import metrics
from sklearn.metrics.pairwise import cosine_similarity
import logging
import re
import unicodedata
import matplotlib.pyplot as plt
import seaborn as sns
import torch
from nltk.tokenize import word_tokenize
from transformers import BertForQuestionAnswering, BertTokenizer

nltk.download('wordnet')
nltk.download('stopwords')

pd.set_option('display.max_colwidth', None)

# Reading in the dataset
df1 = pd.read_csv('./dataset/S08_question_answer_pairs.txt', sep='\t')
df2 = pd.read_csv('./dataset/S09_question_answer_pairs.txt', sep='\t')
df3 = pd.read_csv('./dataset/S10_question_answer_pairs.txt', sep='\t', encoding = 'ISO-8859-1')
frames = [df1, df2, df3]
df = pd.concat(frames)

def getArticleText(file):
    fpath = './dataset/text_data/'+file+'.txt.clean'
    try:
        f = open(fpath, 'r')
        text = f.read()
    except UnicodeDecodeError:
        f = open(fpath, 'r', encoding = 'ISO-8859-1')
        text = f.read()
    return text

df = df.dropna(subset=['ArticleFile'])
df = df.dropna(subset=['Answer'])
df['ArticleText'] = df['ArticleFile'].apply(lambda x: getArticleText(x))
df['ArticleText'] = df['ArticleText'].apply(lambda x: re.sub(r'(\n)+', '. ', x))
df = df.drop(['DifficultyFromQuestioner', 'DifficultyFromAnswerer', 'ArticleFile'], axis='columns')

# stop_words = set(stopwords.words('english'))
def cleanQuestion(text):
    text = str(text)
    # wnl = nltk.stem.WordNetLemmatizer()
    text = text.lower()
    words = re.sub(r'[^\w\s]', '', text).split()
    # words = [word for word in words if not word in stop_words]
    return " ".join([word for word in words])

def cleanAnswer(text):
    text = str(text)
    # wnl = nltk.stem.WordNetLemmatizer()
    text = text.lower()
    words = re.sub(r'[^\w\s]', '', text).split()
    # words = [word for word in words if not word in stop_words]
    return " ".join([word for word in words])

def cleanText(text):
    text = str(text)
    # wnl = nltk.stem.WordNetLemmatizer()
    text = text.lower()
    words = re.sub(r'[^\w\s\.\?]', '', text).split()
    # words = [word for word in words if not word in stop_words]
    return " ".join([word for word in words])

df['Question'] = df['Question'].apply(lambda x: cleanQuestion(x))
df['Answer'] = df['Answer'].apply(lambda x: cleanAnswer(x))
df['ArticleText'] = df['ArticleText'].apply(lambda x: cleanText(x))



# SIF



from fse.models import uSIF

glove = api.load("glove-wiki-gigaword-100")
model_sif = uSIF(glove, workers=2, lang_freq="en")

def getSim(q, x):
    x = (str(x).split(), 0)
    sim = metrics.pairwise.cosine_similarity(model_sif.infer([q]), model_sif.infer([x]))
    return sim

def getBestAnswer(question, potentials):
    q = (str(question).split(), 0)
    c = pd.DataFrame(potentials)
    c['sim'] = c[0].apply(lambda x: getSim(q, x))
    max = c.sort_values(by='sim', ascending=False).iloc[:3]
    return max[0]



# BERT with SIF



use_cuda = True

#if(not(os.path.isfile("./model/pytorch_model.bin"))):
tokenizer = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
model_bert = BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
    #tokenizer.save_pretrained('./model')
    #model_bert.save_pretrained('./model')
#else:
    #tokenizer = BertTokenizer.from_pretrained('./model')
    #model_bert = BertForQuestionAnswering.from_pretrained('./model')

model_sif.train(SplitIndexedList(list(df['ArticleText'])))

def get_split(text1):

    #Reference: https://medium.com/@armandj.olivares/using-bert-for-classifying-documents-with-long-texts-5c3e7b04573d

    l_total = []
    l_parcial = []
    if len(text1.split())//150 >0:
        n = len(text1.split())//150
    else:
        n = 1
    for w in range(n):
        if w == 0:
            l_parcial = text1.split()[:250]
            l_total.append(" ".join(l_parcial))
        else:
            l_parcial = text1.split()[w*150:w*150 + 250]
            l_total.append(" ".join(l_parcial))
    return l_total

def getAnswerBert(question, context):

    # print('Query Context has {} tokens.'.format(len(tokenizer.encode(context))))

    context_list = get_split(context)

    ans = []

    for c in context_list:

        encoding = tokenizer.encode_plus(text=question,text_pair=c)

        inputs = encoding['input_ids']  #Token embeddings
        token_type_id = encoding['token_type_ids']  #Segment embeddings
        tokens = tokenizer.convert_ids_to_tokens(inputs) #input tokens

        output = model_bert(input_ids=torch.tensor([inputs]), token_type_ids=torch.tensor([token_type_id]))
        start_index = torch.argmax(output.start_logits)
        end_index = torch.argmax(output.end_logits)

        answer = ' '.join(tokens[start_index:end_index+1])

        ans.append(answer)
    print('Question: ', question)

    potentials = []
    for i in ans:
        if ('SEP' not in i) and ('CLS' not in i):
            potentials.append(re.sub('(#)+', '', i))

    answer = getBestAnswer(question, potentials)

    # print('Potential Answers: \n')
    # print(answer.head())
    return answer
