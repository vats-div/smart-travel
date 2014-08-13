# -*- coding: utf-8 -*-
"""
Created on Mon Aug 11 12:03:01 2014

@author: dvats
"""

# main code to rank cities based on topic modeling
# first step:
#   - read the output from mallet
#       per_document_output.gz   
#       topic_keys.txt           
#       topic_props.txt          
#       topic_words_weights.txt  
#       word_topic_counts.txt

import numpy as np
import pandas as pd
import gzip
from scipy.sparse import lil_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

def GetID(text):
    text = text.split()
    ind = text[1]
    ind = ind.split('.txt')[0]
    ind = int(ind.split('guide_data/')[1]) # get index number
    return ind

def ReadDocumentTopics(num_docs, num_topics):   
    # read document in ./mallet_output/per_document_output.gz
    # and count the number of times a topic appears

    # read file
    f = gzip.open('./mallet_output/per_document_output.gz', 'rb')
    f.readline()
    alpha = f.readline()
    alpha = alpha.split(":")[1]
    alpha = np.array([float(a) for a in alpha.split()])
    f.readline()
    doc_tops = np.zeros([num_docs,num_topics])
    
    for chunk in iter(lambda: f.readline(), ''):
        
        ind = GetID(chunk) # id number
        top_num = int(chunk.split()[-1]) # get topic number
        if ind > num_docs-1:
            break
        doc_tops[ind, top_num] = doc_tops[ind, top_num] + 1.0
        
    return doc_tops
        
def ReadTopicProps(num_docs, num_topics):

    f = open("mallet_output/topic_props.txt")
    f.readline()
    topic_prop = np.zeros((num_docs, num_topics))
    
    for chunk in iter(lambda: f.readline(), ''):
        ind = GetID(chunk)
        chunk = chunk.split()[2:]
        for i in range(num_topics):
            c1 = int(chunk[2*i])
            c2 = float(chunk[2*i+1])
            topic_prop[ind,c1] = c2
    
    return topic_prop
    
def ReadWordCounts(num_topics):
    
    f = open("mallet_output/word_topic_counts.txt")

    num_words = 10000

    # create a sparse matrix of size num_words x num_topics
    
    word_count = lil_matrix((num_words,num_topics))
    word_list = []
    
    for chunk in iter(lambda: f.readline(), ''):
        chunk = chunk.split()
        ind = int(chunk[0])
        if ind == num_words-1:
            break
        word_list.append(chunk[1])
        chunk = chunk[2:]
        for ck in chunk:
            # ck has the form xx:yy
            ck = ck.split(':')
            word_count[ind,int(ck[0])] = int(ck[1])
                
    return word_count, np.array(word_list)
    
def ScoreDocument(X, word_count,total_words_eachtopic,topic_props,i):
    
    # score = (# words in doc) * \sum[ (# times word in T_i) / (# words) * P(T_i) ]    
    tmp = np.array(word_count[i,:].todense()).flatten()
    tmp = tmp / total_words_eachtopic 
    tmp = np.dot(topic_props, tmp)
    xx = np.array(X[:,i].todense()).flatten()

    mix = 0.5
    
    tmp = ((1-mix) * tmp + mix * xx)
    return tmp
    
# main code

main_data = pd.read_csv("./data/FilteredTravelData.csv")
guide_data = np.array(main_data["all_data"])

title = np.array(main_data["title"])
num_docs = len(main_data)

num_topics = 30

# doc_tops: num_docs x num_topics matrix
# topic_props: num_docs x num_topics matrix
# num_words: num_docs x 1 vector

doc_tops = ReadDocumentTopics(num_docs, num_topics)
num_words = np.sum(doc_tops,axis=1)
topic_props = ReadTopicProps(num_docs, num_topics)

# word_distr: num_words x num_topics matrix
word_count, word_list = ReadWordCounts(num_topics)
total_words_eachtopic = np.array(word_count.sum(axis=0))[0]

vectorizer = TfidfVectorizer(vocabulary=word_list)
X = vectorizer.fit_transform(guide_data)
X = normalize(X,axis=1,norm='l1')

# is keyword is index_keyword then score is
search_word = ['climbing','spa','wine']
city_search_word = ['']
ListOfKeywords = [np.where(word_list == ww)[0] for ww in search_word]
LifOfCityKeywords = [np.where(title==ww)[0] for ww in city_search_word]
#score = np.zeros((num_docs,))

score = []
for index_keyword in ListOfKeywords:
#    score = score + ScoreDocument(X, word_count,total_words_eachtopic,topic_props,index_keyword)
#    score = score * ScoreDocument(X, word_count,total_words_eachtopic,topic_props,index_keyword)
    if len(index_keyword) > 0:
        score.append(num_words * ScoreDocument(X, word_count,total_words_eachtopic,topic_props,index_keyword))

for ind in LifOfCityKeywords:
    if len(ind) > 0:
        tt = -np.sum(abs(topic_props - topic_props[ind,:]),axis=1)
        tt[ind] = -10000.00
        score.append(tt)
    
rl = 0
num_rows = len(main_data)
for ss in score:
    tmp1 = np.argsort(-np.array(ss))
    tmp2 = np.zeros((num_rows,))
    tmp2[tmp1] = np.array(range(num_rows))
    rl = rl + tmp2
    print rl

print len(rl)
ranked_list = np.argsort(rl)
print rl
print ranked_list
title_r = title[ranked_list]

print title_r[:50]

#word_num = np.array([len(text.split()) for text in main_data["all_data"]])
#topic1 = doc_tops[:,3]
#ranked_list = np.argsort(-np.array(topic1))
#title_r = title[ranked_list]