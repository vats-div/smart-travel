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
import pickle 

def ScoreDocument(X, word_count,total_words_eachtopic,topic_props,i):
    
    # score = (# words in doc) * \sum[ (# times word in T_i) / (# words) * P(T_i) ]    
    tmp = np.array(word_count[i,:].todense()).flatten()
    tmp = tmp / total_words_eachtopic 
    tmp = np.dot(topic_props, tmp)

    print np.shape(X[:,i])
    xx = np.array(X[:,i].todense()).flatten()

    mix = 0.5
    
    tmp = ((1-mix) * tmp + mix * xx)
    return tmp
    
def GetRanking(search_word, city_search_word):
    
    # is keyword is index_keyword then score is
    
    filehandler = open('topic_model_data.obj', 'r')
    D = pickle.load(filehandler)
   
    print len(D["title"])
    
    ListOfKeywords = [np.where(D["word_list"] == ww)[0] for ww in search_word]
    LifOfCityKeywords = [np.where(D["title"]==ww)[0] for ww in city_search_word]
    #score = np.zeros((num_docs,))
    
    score = []
    for index_keyword in ListOfKeywords:
    #    score = score + ScoreDocument(X, word_count,total_words_eachtopic,topic_props,index_keyword)
    #    score = score * ScoreDocument(X, word_count,total_words_eachtopic,topic_props,index_keyword)
        if len(index_keyword) > 0:
            score.append(D["num_words"] * \
            ScoreDocument(D["X"], D["word_count"], \
            D["total_words_eachtopic"],D["topic_props"],\
            index_keyword[0]))
    
    for ind in LifOfCityKeywords:
    
        if len(ind) > 0:
            tt = -np.sum(abs(D["topic_props"] - D["topic_props"][ind,:]),axis=1)
            tt[ind] = -10000.00
            score.append(tt)
        
    rl = 0
    num_rows = len(D["title"])
    
    for ss in score:
        tmp1 = np.argsort(-np.array(ss))
        tmp2 = np.zeros((num_rows,))
        tmp2[tmp1] = np.array(range(num_rows))
        rl = rl + tmp2

    tmp = np.argsort(rl)
    rr = np.zeros((num_rows,))
    rr[tmp] = np.array(range(num_rows))
    
    # return ranking
    return rr    
    #ranked_list = np.argsort(rl)
    #title_r = D["title"][ranked_list]

#search_word = ['pub','beer','museum']
#city_search_word = ['']
#
#ranking = GetRanking(search_word, city_search_word)
#
#word_num = np.array([len(text.split()) for text in main_data["all_data"]])
#topic1 = doc_tops[:,3]
#ranked_list = np.argsort(-np.array(topic1))
#title_r = title[ranked_list]
