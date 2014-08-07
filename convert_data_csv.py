# -*- coding: utf-8 -*-
"""
Created on Sun Aug  3 21:22:38 2014

@author: dvats
"""

# convert the data from wikivoyage to a csv file

import re
import pandas as pd
import numpy as np

def CleanData(text):
    # remove headers like See, Do, etc
    section_headings = ["See", "Do", "Learn", \
                        "Eat", "Drink", "Buy", \
                        "GuideClass", "LinkBefore", "Region"]
    for s in section_headings:
        text = text.replace("<h2>"+s+"</h2>", "")
    
    # remove brackets like [ and ]
    text = text.replace("[", "").replace("]", "")   
    
    return text

# return pattern from a string that contain pattern="id_num" url
def GetPattern(text, pattern):
    tmp = re.search(pattern, text)
    return text[tmp.end():].split('"', 1)[1].split('"', 1)[0]

# return a dictionary with headings given by <h>HEADING</h>
def GetMainData(text):
    temp_text = text.split('\n', 1)[1]
    temp_text = temp_text.replace("</doc>", "")

    # find all instances of <h>
    h_p = [m.start() for m in re.finditer('<h>', temp_text)]
    h_p.append(len(temp_text))
    text_divide = [temp_text[h_p[i]:h_p[i+1]] \
                    for i, h in enumerate(h_p) if h != h_p[-1]]
    
    MainData = {}
    for tt in text_divide:
        st = tt.split('\n', 1)[0] # get te <h>LABEL</h> line
        st = st.replace("<h>", "").replace("</h>","")
        MainData[st] = tt.split('\n', 1)[1].replace('\n', " ").replace('\r', " ").lstrip().rstrip()
        
    return MainData
    
ff = open("./data/wikivoyage_data")
all_data = ff.read()

# find all instances of <doc and </doc>
start_doc = [m.start() for m in re.finditer('<doc', all_data)]
end_doc = [m.end() for m in re.finditer('</doc>', all_data)]

# separate the data
sep_data = [all_data[sd:end_doc[i]] for i, sd in enumerate(start_doc)]
id_data = np.array([GetPattern(ss.split('\n', 1)[0], "id=") for ss in sep_data])
title_data = np.array([GetPattern(ss.split('\n', 1)[0], "title=") for ss in sep_data])
url_data = np.array([GetPattern(ss.split('\n', 1)[0], "url=") for ss in sep_data])
final_data = {}

final_data["title"] = title_data
final_data["url"] = url_data
final_data["id"] = id_data
num_rows = len(id_data)
section_headings = ["See", "Do", "Learn", \
                    "Eat", "Drink", "Buy", \
                    "GuideClass", "LinkBefore", "Region"]
for h in section_headings:
    final_data[h] = [''] * num_rows
                    
# iterate over all elements in sep_data
for i, ss in enumerate(sep_data):
    temp_data = GetMainData(ss) # return a dictionary
    for k in temp_data.keys():
        final_data[k][i] = temp_data[k]

# write the data to a csv file
final_data = pd.DataFrame(final_data)
#final_data.to_csv("./data/TravelData.csv")
