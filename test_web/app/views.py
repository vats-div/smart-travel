from flask import render_template, request
from app import app
import pymysql as mdb
import numpy as np
from RankingUsingMallet import GetRanking
import cgi

db= mdb.connect(user="root", host="localhost", db="guide_data", charset='utf8')

@app.route('/')
@app.route('/index')

def index():
	return render_template("cities.html",
        title = 'Home',
        )

@app.route('/check')

def check_data():

	rt_data = []

        # keywords
        user_input = request.args.get('keywords', '')
        user_input = user_input.lstrip().rstrip().lower().encode('ascii')
        if len(user_input) > 0:
                user_input = user_input.split(',')

        # filter for regions
        country_input = request.args.get('country', '')
        country_input = country_input.lstrip().rstrip().lower().encode('ascii')

        # cities people like
        like_input = request.args.get('like', '')
        like_input = like_input.lstrip().rstrip().lower().encode('ascii')
        if len(like_input) > 0:
                like_input = like_input.split(',')

	for ky in user_input:
		if ky not in open('./word.txt', 'r').read():
			rt_data.append(ky)

	for ci in country_input:
		if ci not in open('./country.txt', 'r').read():
			rt_data.append(ci)

	for li in like_input:
		if li not in open('./title.txt', 'r').read():
			rt_data.append(li)

	if len(rt_data) > 1:
		rt_data = ','.join(rt_data)
		rt_data = "Sorry, the inputs " + rt_data + " are not in the database. Discovering cities without these inputs!"
	
	if len(rt_data) == 1:
		rt_data = rt_data[0]
		rt_data = "Sorry, the input " + rt_data + " is not in the database.  Discovering cities without this input!"

	if len(rt_data) == 0:
		rt_data = ''

	return rt_data

@app.route("/rank")

def cities_rank():
        print request.args.get('keywords', '')

	# keywords
        user_input = request.args.get('keywords', '')
	user_input = user_input.lstrip().rstrip().lower().encode('ascii')
	if len(user_input) > 0:
		user_input = user_input.split(',')

	# filter for regions
        country_input = request.args.get('country', '')
	country_input = country_input.lstrip().rstrip().lower().encode('ascii')

	# cities people like
	like_input = request.args.get('like', '')
	like_input = like_input.lstrip().rstrip().lower().encode('ascii')
	if len(like_input) > 0:
		like_input = like_input.split(',')
		print like_input
	
	# get ranking
	rnk = GetRanking(user_input,like_input)

	with db:
		cur = db.cursor()
		# cmnd = "SELECT id, title, top_words, url FROM MainData "
		cmnd = "select a.id, title, SUBSTRING_INDEX(top_words,' ',5) as top_words, url, country from MainData a join CountryList b on a.id=b.id "

		# SELECT title, top_words FROM ranking WHERE 
		# (search_terms LIKE "%pub%" AND search_terms LIKE "%bar%") AND
		# (region LIKE "% UNITED %" OR region LIKE "% Australia %");

		if country_input != '':
			cmnd = cmnd + 'WHERE ('
       	        	for st in country_input.split(','):
                      		cmnd = cmnd + " region LIKE '%"
                        	cmnd = cmnd + "%s" % st
                        	cmnd = cmnd + "%'"
                        	if country_input.split(',')[-1] != st:
                                	cmnd = cmnd + " OR "

			cmnd = cmnd + ");"

		print cmnd
		cur.execute(cmnd)
		query_results = cur.fetchall()

	cities = []
	for result in query_results:
		cities.append(dict(id=result[0], title=result[1], top_words=result[2], url=result[3],country=result[4]))

	# only rank things in id
	ListOfID = []
	for city in cities:
		ListOfID.append(city["id"]-1)	

	# get the corresponding ranking
	rnk = rnk[ListOfID]

	# sort then
	argrank = np.argsort(rnk)

	#print type(cities)
	#print type(cities[0])
	#rnk = rnk[cities["id"]-1]
	#print rnk

	#return "<h3>This is the server response!</h3>"
	tmp = '<table id = "ranklist" class="table table-striped">'
    	tmp = tmp + '<tr> <th>Name</th> <th>Country</th> <th>Top Keywords</th></tr>'

	cnt = 1;
	max_results = 200;
	for a in argrank:
		cnt = cnt + 1;
		city = cities[a]
    		tmp = tmp + '<tr> <td>' + '<a href=' + city["url"] + ' target="_blank">' + cgi.escape(city["title"]).encode('ascii','xmlcharrefreplace') + '</a>' + '</td> <td>' +city["country"].title() + '</td><td>' + city["top_words"] + '</td></tr>'
		if cnt > max_results:
			break;
	
	tmp = tmp + '</table>'

	return tmp
