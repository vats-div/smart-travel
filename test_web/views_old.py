from flask import render_template, request
from app import app
import pymysql as mdb
from RankingUsingMallet import GetRanking

db= mdb.connect(user="root", host="localhost", db="initial_ranked_list", charset='utf8')

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
        user_input = request.args.get('keywords', '')
	user_input = user_input.lstrip().rstrip()

        country_input = request.args.get('country', '')
	country_input = country_input.lstrip().rstrip()
	
	rnk = GetRanking(user_input.split(','),country_input.split(','))

	print rnk

	with db:
		cur = db.cursor()
		cmnd = "SELECT title, top_words FROM ranking "

		if len(user_input.split()) > 0:
			cmnd = cmnd + "WHERE ("
			# SELECT title, top_words FROM ranking WHERE 
			# (search_terms LIKE "%pub%" AND search_terms LIKE "%bar%") AND
			# (region LIKE "% UNITED %" OR region LIKE "% Australia %");
			for st in user_input.split():
				cmnd = cmnd + " search_terms LIKE '%"
				cmnd = cmnd + "%s" % st
				cmnd = cmnd + "%'"
				if user_input.split()[-1] != st:
					cmnd = cmnd + " AND "
			cmnd = cmnd + ")"

		if country_input != '':
			if len(user_input.split()) > 0:
				cmnd = cmnd + ' AND '
			else:
				cmnd = cmnd + 'WHERE '
			cmnd = cmnd + '('
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
		cities.append(dict(title=result[0], search_terms=result[1]))

	#return "<h3>This is the server response!</h3>"
	tmp = '<table id = "ranklist" class="table table-hover">'
    	tmp = tmp + '<tr><th>Name</th><th>Key Words</th></tr>'

	for city in cities:
    		tmp = tmp + '<tr><td>' + city["title"] + '</td><td>'+ city["search_terms"] + '</td></tr>'
	
	tmp = tmp + '</table>'

	return tmp
