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
from nltk.corpus import wordnet as wn
from nltk.corpus.reader import NOUN
from nltk.stem import wordnet
import nltk

import re

        
def get_wordnet_pos(treebank_tag):

    if treebank_tag.startswith('J'):
        return wordnet.wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.wordnet.ADV
    else:
        return ''
    
# convert word to singular
def ConvertToSingular(word):
    
    synsets = wn.synsets(word, NOUN)
    if len(synsets) > 0:
        # then noun
        lmtzr = wordnet.WordNetLemmatizer()
        return lmtzr.lemmatize(word)
    else:
        return word

def MyStemWord(word,inp):
    
    lmtzr = wordnet.WordNetLemmatizer()
    if inp == '':
        return lmtzr.lemmatize(word)
    else:
        return lmtzr.lemmatize(word, inp)
    
# input a string and output a clean string
def FilterData(text, sw, i):
    
    #print i
    
    if type(1.0) == type(text):
        text = ' '
        return text
        
    # remove punctuations
    text = re.sub(r'\[.*?\]|\(.*?\)|\W', ' ', text)
    ff = open("./word_files/remove_puncs.txt")
    list_words = ff.read().split()
    ff.close()
    for ll in list_words:
        text = text.replace(ll," ")
    
    # remove stopwords and additional words
    # stem words using wordnet
    text = text.lower().split()
    #pp_tag = nltk.pos_tag(text)    
    #text = np.array([MyStemWord(s[0], get_wordnet_pos(s[1])) \
    #            for s in pp_tag if s[0] not in sw])  
    
    text = np.array([s for s in text if s not in sw])
    
    # remove all two letter words
    text = np.array([s for s in text if len(s) > 2])
    #return text
    return " ".join(text)

# merge strings with the DataFrame df
# return numpy array
def MergeStringColumns(df,strs):

    if type(df[strs[0]]) == float(1.0):
            df[strs[0]] = ''

    if len(strs) == 1:
        return np.array(df[strs[0]])    
    
    if type(df[strs[1]]) == float(1.0):
            df[strs[1]] = ''
                        
    tmp = df[strs[0]] + ' ' + df[strs[1]]
    
    for i in range(len(strs)-1,len(strs)):
        if type(df[strs[i]]) == float(1.0):
            df[strs[i]] = ''

        tmp = tmp + ' ' + df[strs[i]]
    return np.array(tmp)
    
    
def GetTopWord(text,num_w):
    cc = Counter(text.split()).most_common(num_w)
    return ' '.join([cw[0] for cw in cc])
    
def RemoveWordsInKeys(text,kys):
    text = [s for s in text.split() if s not in kys]
    return " ".join(text)

def RemoveLowFrequencyWords(guide_data, num_w):
    txt_all = ' '.join(guide_data)
    cc = Counter(txt_all.split())
    kys = np.array(cc.keys())
    vls = np.array(cc.values())
    kys = kys[vls < num_w]
    print "Number of words to remove is " + str(len(kys))
    
    # save list of words in kys
    f = open('./word_files/extra_stopwords.txt', 'w')
    for wds in kys:
        f.write("%s\n" % wds)
    f.close()
    
    # remove words from guide_data that are in keys
    # I only run this in the java code when learning a statistical modl
    # for computational efficiency
    
    #guide_data = np.array([RemoveWordsInKeys(text,kys) for text in guide_data])
        
def RemoveCityReference(guide_data,title):
    
    for i, tt in enumerate(title):
        
        # clean the title first
        gg = guide_data[i]
        tt = tt.split('(')[0].lower()
        gg = gg.replace(tt,'')
        guide_data[i] = gg
        
    return guide_data
        
# read file
print "Reading File..."
main_data = pd.read_csv("./data/TravelData.csv").fillna(value = '')
print "Done Reading File..."

# load stop words
ff = open("./word_files/stopwords.txt")
sw = ff.read()
sw = sw.split()
ff.close()
ff = open("./word_files/extra_stopwords.txt")
sw_extra = set(ff.read().split())

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
print "Filtering Data.."
guide_data = np.array([FilterData(text, sw, i) for i, text in enumerate(get_text)])
main_data["all_data"] = guide_data
print "Done Filtering Data ..."

# drop the columns in combine
for cols in combine:
    main_data = main_data.drop(cols, 1)

# remove strings where guide_data = ' '
ind = np.array(main_data["all_data"]) != ''
main_data = main_data[ind]
main_data.index = range(len(main_data))

guide_data = np.array(main_data["all_data"])
title = np.array(main_data["title"])

# now merge different guides
# if the title of a guide is text1/text2, move contents to
# guide with title text1

print "Merging guides..."

ind = [True] * int(len(title))

for i, tt in enumerate(title):
    tt = tt.split('/')
    if len(tt) > 1:
        # get first element
        #print ' '.join(tt)
        tt = tt[0].lstrip().rstrip()
        index_tt = np.where(title == tt)[0]
        
        # merge guides
        guide_data[index_tt] = guide_data[index_tt] + ' ' + guide_data[i]
        ind[i] = False
        
# reassign guide data
main_data["all_data"] = guide_data
main_data = main_data[ind]
main_data.index = range(len(main_data))

print "Done merging guides..."

# try to populate region properly so that county/state can be accurately
# detected

print "Detecting Country/Region of every city"
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
                    # print i
                    region[i] = reg_new

# update region in main_data
main_data["Region"] = region

print "Done detecting Country/Region of every city"

# remove words that only occur once
# precomputed to avoid computations
#print "Now Removing Words that occur once"
#guide_data = np.array(main_data["all_data"])
print "Removing low frequency words"
RemoveLowFrequencyWords(guide_data, 20)
print "Done removing low frequency words"

guide_data = np.array(main_data["all_data"])
title = np.array(main_data["title"])

# if guide_data contains a reference to its city,
# remove it
print "Removing city reference from guide"
guide_data = RemoveCityReference(guide_data,title)
main_data["all_data"] = guide_data
print "Done removing city reference"

# write the files 
# run a bash command to delete files in ./temp_dir/
for i, tt in enumerate(guide_data):
    f = open("./guide_data/" + str(i) + ".txt", 'w')
    f.write(tt)
    f.close()
    
# write file to a new csv file
main_data["top_words"] = np.array([GetTopWord(text,10) for text in guide_data])
main_data.to_csv('./data/FilteredTravelData.csv')

# code not needed
#main_data["all_data"] = guide_data
## already saved in sw_extra from a previous iteration
#part_word = "sjhshksnsmbdkwnd" # some random word
#pw = " " + part_word + " "
#all_text = pw.join(guide_data)
#regex = re.compile(r'\b(' + r'|'.join(sw_extra) + r')\b\s*')
#out = regex.sub("", all_text)
#guide_data = np.array(out.split(part_word))
#main_data["all_data"] = guide_data

#main_data = pd.read_csv("./data/FilteredTravelData.csv").fillna('')
#ind = np.array(main_data["all_data"] == '')
#word_num = np.array([len(gg.split()) for gg in np.array(main_data["all_data"])])
#ind = ind + np.array(word_num < 50)
#ind = np.logical_not(ind)
#
#guide_data = np.array(main_data["all_data"])[ind]
#title = np.array(main_data["title"])[ind]
#top_words = np.array(main_data["top_words"])[ind]
#Region = np.array(main_data["Region"])[ind]
#url = np.array(main_data["url"])[ind]
#word_num = word_num[ind]
#RemoveLowFrequencyWords(guide_data, 20)
#
#for i, tt in enumerate(guide_data):
#    f = open("./guide_data/" + str(i) + ".txt", 'w')
#    f.write(tt)
#    f.close()
#
#guide_data = np.array(main_data["all_data])
#RemoveLowFrequencyWords(guide_data, 20)