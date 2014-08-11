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
import gzip

def ReadDocumentTopics(num_docs, num_topics):   
    # read document in ./mallet_output/per_document_output.gz
    
    # read file
    f = gzip.open('./mallet_output/per_document_output.gz', 'rb')
    
    doc_tops = np.empty([num_docs,num_topics])
    
    for chunk in iter(lambda: f.readline(), ''):
        
        # split document
        chunk = chunk.split()
        ind = chunk[1]
        ind = ind.split('.txt')[0]
        ind = int(ind.split('/')[1]) # get indx number
        top_num = int(chunk[-1]) # get topic number
        
        