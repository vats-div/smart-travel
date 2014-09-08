# -*- coding: utf-8 -*-
"""
Created on Tue Aug 19 11:50:45 2014

Code writes th dictionary ofwords, countries, and cities
to a file so that error checking can be done when a user
enters a word that is not in the database

@author: dvats
"""

# get a list of all words, regions, and cities and write to file

import pandas as pd
import numpy as np


ff = open('./mallet_output/word_topic_counts.txt', 'r')

words = ff.readlines()
words = [w.split()[1] for w in words]
words = ' '.join(words)
# write words to a text file

ff = open('./test_web/word.txt', 'w')
ff.write(words)
ff.close()

file_name = "./data/FilteredTravelData.csv"
usecols = ["Region", "title"]
main_data = pd.read_csv(file_name, usecols=usecols).fillna(value='')
title = np.array(main_data["title"])
title = [tt.lower() for tt in title]

ff = open('./test_web/title.txt', 'w')
ff.write(' '.join(title))
ff.close()

region = np.array(main_data["Region"])
region = [rr.lower() for rr in region]

ff = open('./test_web/country.txt', 'w')
ff.write(' '.join(region))
ff.close()
