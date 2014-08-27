# -*- coding: utf-8 -*-
"""
Created on Tue Aug 19 16:16:01 2014

Get the country name of each city using database of countries
in countries_list.txt

Write the countries to a database

@author: dvats
"""

# find the country for each city

import pandas as pd
import numpy as np
import MySQLdb as db

main_data = pd.read_csv("./data/FilteredTravelData.csv", usecols=["Region","title"]).fillna(value='')

region = np.array(main_data["Region"])
list_countries = open('./data/countries_list.txt', 'r').readlines()[0].split('\r')
list_countries = np.array([ll.lstrip().rstrip().replace('&','and').lower() for ll in list_countries])
list_countries_new = np.array(['_'.join(ll.split()) for ll in list_countries])

countries = ['']*len(region)

for ind in range(len(region)):
    
    rr = region[ind].lower()
    val = np.zeros(len(list_countries))
    for i, c in enumerate(list_countries):
        val[i] = c in rr
        
    if sum(val) == 1.0:
        ind_c = np.where(val == True)[0][0]
        countries[ind] = list_countries[ind_c]
    
    if sum(val) == 0.0:
        val1 = np.zeros(len(list_countries_new))
        for i, c in enumerate(list_countries_new):
            val1[i] = c in rr
        
        if sum(val1) == 1.0:
            ind_c = np.where(val1==True)[0][0]
            countries[ind] = ' '.join(list_countries[ind_c].split('_'))
        
    if 'scotland' in rr:
        countries[ind] = 'united kingdom'
        
    if 'united states' in rr:
        countries[ind] = 'united states'

    if 'united kingdom' in rr:
        countries[ind] = 'united kingdom'

    if 'united_states' in rr:
        countries[ind] = 'united states'

    if 'united_kingdom' in rr:
        countries[ind] = 'united kingdom'                
        
    if 'saudi arabia' in rr:
        countries[ind] = 'saudi arabia'
        
    if 'new zealand' in rr:
        countries[ind] = 'new zealand'
                    
    if 'new_zealand' in rr:
        countries[ind] = 'new zealand'
        
    if 'south korea' in rr:
        countries[ind] = 'south korea'
        
    if 'south_korea' in rr:
        countries[ind] = 'south korea'
        
    if 'north_korea' in rr:
        countries[ind] = 'north korea'
        
    if 'north carolina' in rr:
        countries[ind] = 'united states'
        
    if 'florida' in rr:        
        countries[ind] = 'united states'
        
    if 'new york' in rr:
        countries[ind] = 'united states'
    
    if 'toronto' in rr:
        countries[ind] = 'canada'
        
    if 'lehigh' in rr:
        countries[ind] = 'united states'

    if 'Italy' in rr:
        countries[ind] = 'italy'
    
    if 'greek' in rr:
        countries[ind] = 'greece'

    if 'greece' in rr:
        countries[ind] = 'greece'

    if 'new south wales' in rr:
        countries[ind] = 'australia'                
            
    if 'detroit' in rr:
        countries[ind] = 'united states'                
        
    if 'north west england' in rr:
        countries[ind] = 'united kingdom'

    if 'ohio' in rr:
        countries[ind] = 'united states'

    if 'jammu' in rr:
        countries[ind] = 'india'
    
    if 'nigeria' in rr:
        countries[ind] = 'nigeria'
        
    if 'romania' in rr:
        countries[ind] = 'romania'
        
    if 'NorwayNorway' in rr:
        countries[ind] = 'norway'
        
    if 'Nova Scotia' in rr:
        countries[ind] = 'canada'
        
    if 'east england' in rr:
        countries[ind] = 'united kingdom'
    
    if 'east of england' in rr:
        countries[ind] = 'united kingdom'
        
    if 'ontario' in rr:
        countries[ind] = 'canada'    
        
    if 'auckland' in rr:
        countries[ind] = 'australia'    

con = db.connect('localhost','root','','guide_data')
cr = con.cursor()
cr.execute("drop table if exists CountryList;")

# create table columns
tmp = '''
create table CountryList (
        id int(7),
        country text,
        primary key (id)
);
'''
cr.execute(tmp)

for i in range(len(countries)): 
    tmp_c = "INSERT INTO CountryList (id, country) VALUES (%s, %s)" 
    tmp_v = [i+1, countries[i]]
    cr.execute(tmp_c,tuple(tmp_v))

con.commit()
cr.close()
con.close()
