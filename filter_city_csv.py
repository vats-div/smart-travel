# -*- coding: utf-8 -*-
"""
Created on Wed Aug  6 23:42:43 2014

@author: dvats
"""

# filter the city csv file
# remove stopwords
# merge guides together

import numpy as np
import pandas as pd
from collections import Counter
import re

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
        text = text.replace(ll," ")
    
    # remove stopwords
    ff = open("stopwords.txt")
    sw = ff.read()
    sw = sw.split()
    text = text.lower().split()
    text = np.array([s for s in text if s not in sw])

    # TO DO
    #   convert plurals to singulars
    
    return " ".join(text)


# merge strings with the DataFrame df
# return numpy array
def MergeStringColumns(df,strs):

    tmp = df[strs[0]] + ' ' + df[strs[1]]
    
    for i in range(len(strs)-1,len(strs)):
        tmp = tmp + ' ' + df[strs[i]]
    return np.array(tmp)
    
    
def GetTopWord(text,num_w):
    cc = Counter(text.split()).most_common(num_w)
    return ' '.join([cw[0] for cw in cc])
    
# read file
main_data = pd.read_csv("./data/TravelData.csv", na_values=[''])

main_data_copy = main_data.copy()

n_rows = np.max(main_data.count())

# list of things to accept
gg = ['usable_city', 'usable_district', \
        'star_district', 'star_city', \
        'guide_district', 'guide_city', \
        'outline_city', 'outline_district']
        
# filter data according to GuideClass
combine = ["See", "Do", "Learn", "Eat", "Drink"]

main_data = main_data[main_data["GuideClass"].isin(gg)].reset_index()
get_text = MergeStringColumns(main_data, combine)
guide_data = np.array([FilterData(text) for text in get_text])
main_data["all_data"] = guide_data

# remove strings where guide_data = ' '
ind = np.array(main_data["all_data"]) != ' '
main_data = main_data[ind]
main_data.index = range(len(main_data))

guide_data = np.array(main_data["all_data"])
title = np.array(main_data["title"])

# now merge different guides
# if the title of a guide is text1/text2, move contents to
# guide with title text1

ind = [True] * int(len(title))

for i, tt in enumerate(title):
    tt = tt.split('/')
    if len(tt) > 1:
        # get first element
        print ' '.join(tt)
        tt = tt[0].lstrip().rstrip()
        index_tt = np.where(title == tt)[0]
        
        # merge guides
        guide_data[index_tt] = guide_data[index_tt] + ' ' + guide_data[i]
        ind[i] = False
        
# reassign guide data
main_data["all_data"] = guide_data
main_data = main_data[ind]
main_data.index = range(len(main_data))
# try to populate region properly

region = np.array(main_data["Region"])
link_before = np.array(main_data["LinkBefore"])

region_copy = np.array(main_data_copy["Region"])
title = np.array(main_data_copy["title"])

for i, reg in enumerate(region):
    if type(reg) == type(1.0):
        # get link before
        lb = link_before[i]
        if type(lb) != type(1.0):
            lb = lb.lstrip().rstrip()
            lb = ' '.join(lb.split('_'))
            ind = np.where(title == lb)[0] # index for link before
            if len(ind) > 0:
                ind = ind[0]
                reg_new = region_copy[ind]
                if type(reg_new) != type(1.0):
                    print i
                    region[i] = reg_new
                    
# update region in main_data
main_data["Region"] = region

guide_data = np.array(main_data["all_data"])
title = np.array(main_data["title"])

main_data["top_words_100"] = np.array([GetTopWord(text,100) for text in guide_data])
main_data["top_words"] = np.array([GetTopWord(text,10) for text in guide_data])

# write the files 
# run a bash command to delete files in ./temp_dir/
for i, tt in enumerate(guide_data):
    f = open("./temp_dir/" + str(i) + ".txt", 'w')
    f.write(tt)
    f.close()
    
# write file to a new csv file
    
main_data.to_csv('./data/FilteredTravelData.csv')