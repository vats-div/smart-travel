from flask import render_template, request
from app import app
import pymysql as mdb
import numpy as np
from RankingUsingMallet import GetRanking

db= mdb.connect(user="root", host="localhost", db="guide_data", charset='utf8')

@app.route('/')
@app.route('/index')

def index():
	return render_template("index.html",
        title = 'Home',
        )

@app.route('/db')
def cities_page():
	with db: 
		cur = db.cursor()
		cur.execute("SELECT Name FROM city LIMIT 15;")
		query_results = cur.fetchall()
	cities = ""
	for result in query_results:
		cities += result[0]
		cities += "<br>"
	return cities

@app.route("/db_fancy")

def cities_page_fancy():

	return render_template('cities.html')

@app.route("/rank")

def cities_rank():
        print request.args.get('keywords', '')

	# keywords
        user_input = request.args.get('keywords', '')
	user_input = user_input.lstrip().rstrip()

	# filter for regions
        country_input = request.args.get('country', '')
	country_input = country_input.lstrip().rstrip()

	# cities people like
	like_input = request.args.get('like', '')
	like_input = like_input.lstrip().rstrip()

	with db:
		cur = db.cursor()
		cmnd = "SELECT id, title, top_words, url FROM MainData "

		# SELECT title, top_words FROM ranking WHERE 
		# (search_terms LIKE "%pub%" AND search_terms LIKE "%bar%") AND
		# (region LIKE "% UNITED %" OR region LIKE "% Australia %");

		if country_input != '':
			cmnd = cmnd + 'WHERE ('
       	        	for st in country_input.split(','):
                      		cmnd = cmnd + " region LIKE '% "
                        	cmnd = cmnd + "%s" % st
                        	cmnd = cmnd + " %'"
                        	if country_input.split(',')[-1] != st:
                                	cmnd = cmnd + " OR "

			cmnd = cmnd + ");"

		print cmnd
		cur.execute(cmnd)
		query_results = cur.fetchall()

	cities = []
	for result in query_results:
		cities.append(dict(id=result[0], title=result[1], top_words=result[2], url=result[3]))

	# only rank things in id
	ListOfID = [city["id"]-1 for city in cities]

	# get the corresponding ranking
	# get ranking
	print ListOfID
	rnk = GetRanking(user_input.split(','),like_input.split(','))

	# sort then
	argrank = np.argsort(rnk)

	#print type(cities)
	#print type(cities[0])
	#rnk = rnk[cities["id"]-1]
	print rnk

	#return "<h3>This is the server response!</h3>"
	tmp = '<table id = "ranklist" class="table table-hover">'
    	tmp = tmp + '<tr><th>Name</th><th>Top Keywords</th></tr>'

	for a in argrank:
		city = cities[a]
    		tmp = tmp + '<tr><td>' + '<a href=' + city["url"] + ' target="_blank">' + city["title"] + '</a>' + '</td><td>'+ city["top_words"] + '</td></tr>'

	tmp = tmp + '</table>'
	return tmp
