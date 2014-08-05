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

# input a string and output a clean string
def FilterData(text):
    if type(1.0) == type(text):
        text = ' '
        return text
        
    # remove punctuations
    text = re.sub(r'\[.*?\]|\(.*?\)|\W', ' ', text)
    ff = open("remove_puncs.txt")
    list_words = ff.read().split()
    ff.close()
    for ll in list_words:
        text = text.replace(ll,"")
    
    # remove stopwords
    ff = open("stopwords.txt")
    sw = ff.read()
    sw = sw.split()
    text = text.lower().split()
    text = np.array([s for s in text if s not in sw])

    # convert plurals to singulars
    # not implemented yet  
    
    # remove two letter words and return
    #return " ".join(word for word in text if len(word)>2)
    return " ".join(text)
  
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

def MergeStringColumns(df,strs):

    tmp = df[strs[0]] + ' ' + df[strs[1]]
    
    for i in range(len(strs)-1,len(strs)):
        tmp = tmp + ' ' + df[strs[i]]
    return tmp
    
def GetTopWord(text):
    cc = Counter(text.split()).most_common(10)
    return ' '.join([cw[0] for cw in cc])

# read the ./data/TravelData.csv

main_data = pd.read_csv("./data/TravelData.csv", \
            usecols=['title', 'See', 'Do', 'Learn', 'Eat', 'Drink', 'GuideClass'], na_values=[''])

n_rows = np.max(main_data.count())

# list of things to accept
gg = ['usablecity', 'usabledistrict', \
        'stardistrict', 'starcity','guidedistrict', 'guidecity']

# filter data according to GuideClass
combine = ["See", "Do", "Learn", "Eat", "Drink"]

main_data = main_data[main_data["GuideClass"].isin(gg)]
get_text = np.array(MergeStringColumns(main_data, combine))
guide_data = np.array([FilterData(text) for text in get_text])
title = np.array(main_data["title"])
entropy_values = np.array([FindEntropy(text) for text in guide_data])

#all_titles = np.array(range(0,len(title)))
ranked_list = np.argsort(-entropy_values)
main_data["ranking"] = ranked_list
main_data["top_words"] = np.array([GetTopWord(text) for text in guide_data])

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
        primary key (rank)
);
'''

cr.execute(tmp)

# write columns the database
rank_c = range(0,len(ranked_list))
top_words_c = np.array(main_data["top_words"])[ranked_list]
title_c = title[ranked_list]

for i, tt in enumerate(rank_c): 
    tmp_c = "INSERT INTO ranking (rank, title, search_terms) VALUES (%s, %s, %s)" 
    tmp_v = [tt+1, title_c[i], top_words_c[i]]
    cr.execute(tmp_c,tuple(tmp_v))

con.commit()
cr.close()
con.close()

# remove things have zero entropy -> nothing to do in these places
#title = title[entropy != 0]
#text_see = text_see[entropy != 0]
#entropy = entropy[entropy != 0]