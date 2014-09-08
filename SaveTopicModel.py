# -*- coding: utf-8 -*-
"""
Created on Wed Aug 13 11:21:37 2014

Scripts to read the output of the topic model (run using mallet)
into python

@author: dvats
"""

# save the topic model as pickle onjects

import numpy as np
import pandas as pd
import gzip
from scipy.sparse import lil_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
import pickle


def GetID(text):
    """
    Get document id from the the text of the form
    guide_data/id.txt
    """
    text = text.split()
    ind = text[1]
    ind = ind.split('.txt')[0]
    ind = int(ind.split('guide_data/')[1])  # get index number
    return ind


def ReadDocumentTopics(num_docs, num_topics):
    """
    read document in ./mallet_output/per_document_output.gz
    and count the number of times a topic appears
    """
    # read file
    f = gzip.open('./mallet_output/per_document_output.gz', 'rb')
    f.readline()
    alpha = f.readline()
    alpha = alpha.split(":")[1]
    alpha = np.array([float(a) for a in alpha.split()])
    f.readline()
    doc_tops = np.zeros([num_docs, num_topics])
    for chunk in iter(lambda: f.readline(), ''):
        ind = GetID(chunk)  # id number
        top_num = int(chunk.split()[-1])  # get topic number
        if ind > num_docs-1:
            break
        doc_tops[ind, top_num] = doc_tops[ind, top_num] + 1.0
    return doc_tops


def ReadTopicProps(num_docs, num_topics):
    """
    Find the topic proportions for each document (guide_book)
    """

    f = open("mallet_output/topic_props.txt")
    f.readline()
    topic_prop = np.zeros((num_docs, num_topics))
    for chunk in iter(lambda: f.readline(), ''):
        ind = GetID(chunk)
        chunk = chunk.split()[2:]
        for i in range(num_topics):
            c1 = int(chunk[2*i])
            c2 = float(chunk[2*i+1])
            topic_prop[ind, c1] = c2
    return topic_prop


def ReadWordCounts(num_topics):
    """
    Read the number of times a word is mapped to a topic
    """

    f = open("mallet_output/word_topic_counts.txt")
    num_words = 10000

    # create a sparse matrix of size num_words x num_topics
    word_count = lil_matrix((num_words, num_topics))
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
            word_count[ind, int(ck[0])] = int(ck[1])
    return word_count, np.array(word_list)


def ScoreDocument(X, word_count, total_words_eachtopic, topic_props, i):
    """
    Main algorithm to score documents based on a keyword
    See test_web/app/RankingUsingMallet.py for more details
    """

    # score = (# words in doc) *
    #	\sum[ (# times word in T_i) / (# words) * P(T_i) ]
    tmp = np.array(word_count[i, :].todense()).flatten()
    tmp = tmp / total_words_eachtopic
    tmp = np.dot(topic_props, tmp)
    xx = np.array(X[:, i].todense()).flatten()
    mix = 0.5  # mixing of counting and lda model
    tmp = ((1-mix) * tmp + mix * xx)
    return tmp

# main code

print "Reading Data"
main_data = pd.read_csv("./data/FilteredTravelData.csv").fillna('')
guide_data = np.array(main_data["all_data"])

title = np.array(main_data["title"])
num_docs = len(main_data)

# read number of topics
num_topics = sum(1 for line in open('./mallet_output/topic_keys.txt'))

# doc_tops: num_docs x num_topics matrix
# topic_props: num_docs x num_topics matrix
# num_words: num_docs x 1 vector

doc_tops = ReadDocumentTopics(num_docs, num_topics)
num_words = np.sum(doc_tops, axis=1)
topic_props = ReadTopicProps(num_docs, num_topics)

# word_distr: num_words x num_topics matrix
word_count, word_list = ReadWordCounts(num_topics)
total_words_eachtopic = np.array(word_count.sum(axis=0))[0]

vectorizer = TfidfVectorizer(vocabulary=word_list)
X = vectorizer.fit_transform(guide_data)
X = normalize(X, axis=1, norm='l1')

# define a dictioary and then save the data

print"Saving data to pickle object"

DictData = {}

DictData["doc_tops"] = doc_tops
DictData["num_words"] = num_words
DictData["topic_props"] = topic_props
DictData["word_count"] = word_count
DictData["word_list"] = word_list
DictData["total_words_eachtopic"] = total_words_eachtopic
DictData["X"] = X
DictData["title"] = title

filehandler = open('test_web/topic_model_data.obj', 'w')
pickle.dump(DictData, filehandler)
filehandler.close()
