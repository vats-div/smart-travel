# -*- coding: utf-8 -*-
"""
Created on Mon Aug  4 15:10:42 2014

@author: dvats
"""

"""
1) Write function to compute entropy from word frequencies
"""

import numpy as np
import pandas as pd

# input a string and output a clean string
def FilterData(text):
    if type(1.0) == type(text):
        text = ''
        return text
        
    # remove punctuations
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
    return " ".join(text)

# return entropy from word frequencies
def FindEntropy(word_freq):
   temp = word_freq[word_freq != 0]
   return np.sum(temp * np.log(temp))
   

# read the ./data/TravelData.csv

main_data = pd.read_csv("./data/TravelData.csv", \
            usecols=['title', 'See', 'url', 'GuideClass'])

# only keep cities and remove rows that have missing GuideClass

# list of things to accepts
gg = ['usablecity', 'usabledistrict', 'stardistrict', 'starcity']
temp_index = np.array([t in gg for t in main_data.GuideClass])

main_data = main_data[main_data["GuideClass"].isin(gg)]

text_see = np.array([FilterData(text) for text in main_data.See])
title = np.array(main_data.title)