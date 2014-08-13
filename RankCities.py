# -*- coding: utf-8 -*-
"""
Created on Mon Aug  4 15:10:42 2014

@author: dvats
"""

"""
1) Write function to compute entropy from word frequencies
2) First attempt was to compute entropy of words individually
    and then look at the distributio of the words -> didn't work that well
3) To do -> now look at a more global approach that uses topic modeling
"""

import numpy as np
import pandas as pd
from collections import Counter
import re
import MySQLdb as db

# 1 -> Simple method based on local entropy
# 2 -> Elegant method based on 
RANK_STRATEGY = 2
  
# return entropy from text
def FindEntropy(text):
    if text == '':
	return 0.0
    word_freq = np.array([np.float(c) for c in Counter(text).values()])
    word_freq = word_freq[word_freq > 1]
    if len(word_freq) == 0:
        return 0.0
        
    word_freq = np.array(word_freq / np.sum(word_freq))
    temp = word_freq[word_freq != 0]
    return -np.sum(temp * np.log(temp))

# assumes that topic modeling has been run
# and then reads the outputs
def FindEntropyTopicModeling(num_docs):
    f = open("./output_csv/TopicsInDocs.csv", 'r')
    topic_dist = f.read().split()
    f.close()    
    topic_dist = topic_dist[8:]
    entropy_values = [0] * num_docs
    prob_values = [0] * num_docs
    for tmp in topic_dist:
        tmp = tmp.split(',')
        # name of th file
        tmp_name = int(tmp[1].split('/')[-1].split('.')[0])
        prob = [float(t) for t in tmp[3:len(tmp):2]]
        #prob = prob / sum(prob)
        prob.append(1.0-sum(prob))
        prob = np.array(prob)
        prob = prob[prob > 0]
        prob_values[tmp_name] = prob
        e = -np.sum(prob * np.log(prob))
        if np.isnan(e):
            print prob
        entropy_values[tmp_name] = e
    
    return entropy_values, prob_values

def GetTopWord(text):
    cc = Counter(text.split()).most_common(10)
    return ' '.join([cw[0] for cw in cc])

# read the ./data/TravelData.csv

main_data = pd.read_csv("./data/FilteredTravelData.csv")
guide_data = np.array(main_data["all_data"])
title = np.array(main_data["title"])

RANK_STRATEGY = 1

if RANK_STRATEGY == 1:
    entropy_values = np.array([FindEntropy(text) for text in guide_data])

if RANK_STRATEGY == 2:     
    entropy_values = FindEntropyTopicModeling(len(main_data))[0]

#all_titles = np.array(range(0,len(title)))
ranked_list = np.argsort(-np.array(entropy_values))
main_data["ranking"] = ranked_list

#Open connection to mysql database
con = db.connect('localhost','root','','initial_ranked_list')

# cursors
cr = con.cursor()
cr.execute("drop table if exists ranking;")

# create table columns
tmp = '''
create table ranking (
        rank int(7),
        title text,
        search_terms text,
        top_words blob,
        region text,
        primary key (rank)
);
'''
cr.execute(tmp)

# write columns the database
rank_c = range(0,len(ranked_list))
top_words_c = np.array(main_data["top_words"])[ranked_list]
title_c = title[ranked_list]
top_words_more = np.array(main_data["top_words_100"])[ranked_list]
region = np.array(main_data["Region"])[ranked_list]

for i in rank_c: 
    print i
    tmp_c = "INSERT INTO ranking (rank, title, top_words, search_terms, region) VALUES (%s, %s, %s, %s, %s)" 
    if type(region[i]) == type(1.0):
        region[i] = ' '
    tmp_v = [i+1, title_c[i], top_words_c[i], top_words_more[i], region[i].replace('_',' ')]
    cr.execute(tmp_c,tuple(tmp_v))

con.commit()
cr.close()
con.close()