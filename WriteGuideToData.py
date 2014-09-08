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

Aug 27: Finished the above three steps!!!

The code below now writes the relevant data to a database that is called
by the web app
"""

import numpy as np
import pandas as pd
import MySQLdb as db

# read the ./data/TravelData.csv

main_data = pd.read_csv("./data/FilteredTravelData.csv").fillna(value=' ')
num_words = np.array([len(gg.split()) for gg in main_data["all_data"]])
title = np.array(main_data["title"])
region = np.array(main_data["Region"])
top_words = np.array(main_data["top_words"])
url = np.array(main_data["url"])
num_rows = len(main_data)

#Open connection to mysql database
con = db.connect('localhost', 'root', '', 'guide_data')

# cursors
cr = con.cursor()
cr.execute("drop table if exists MainData;")

# create table columns
tmp = '''
create table MainData (
        id int(7),
        title text,
        top_words blob,
        region text,
        url text,
        num_words int(7),
        primary key (id)
);
'''
cr.execute(tmp)

for i in range(num_rows):
    tmp_c = "INSERT INTO MainData (id, title, top_words, region, num_words, url) VALUES (%s, %s, %s, %s, %s, %s)"
    if type(region[i]) == type(1.0):
        region[i] = ' '
    tmp_v = [i+1, title[i], top_words[i], region[i].replace('_', ' '), num_words[i], url[i]]
    cr.execute(tmp_c, tuple(tmp_v))

con.commit()
cr.close()
con.close()
