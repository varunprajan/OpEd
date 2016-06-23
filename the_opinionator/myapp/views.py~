from flask import render_template, request, redirect
from the_opinionator import app
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import psycopg2
from model_predict import AUTHORID, predict_new_article_text, article_weights
from similar_articles import predict_similar_articles, return_df, same_other_df, percentiles
import copy
import numpy as np

user = 'varun' #add your username here (same as previous postgreSQL)                      
host = 'localhost'
dbname = 'birth_db'
db = create_engine('postgres://%s%s/%s'%(user,host,dbname))
con = None
con = psycopg2.connect(database = dbname, user = user)

app.var = {}

DAYSOFWEEK = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html",
       title = 'Home', user = { 'nickname': 'Miguel' },
       )

@app.route('/input', methods = ['GET', 'POST'])
def oped_input():
    if request.method == 'GET':
        authorid2 = copy.copy(AUTHORID)
        del authorid2[(None,None)]
        return render_template("input3.html", authorid = authorid2, daysofweek = DAYSOFWEEK)
    elif request.method == 'POST':
        # app.var['fulltext'] = request.args.get('full_text')
        # app.var['author'] = request.args.get('author')
        # app.var['day'] = int(request.args.get('day'))
        fulltext = request.form['full_text']
        firstname, lastname = author_to_names(request.form['author'])
        day = int(request.form['day']) - 1
        weights = article_weights(fulltext)
        df = return_df()
        sameauthor, otherauthor = same_other_df(df,firstname,lastname)
        expectedshares = predict_new_article_text(firstname,lastname,day,weights)
        percsame, percother = percentiles(sameauthor,otherauthor,expectedshares)
        app.var['percsame'], app.var['percother'] = int(percsame*100)/100, int(percother*100)/100
        app.var['expectedshares'] = expectedshares
        app.var['articlessame'], app.var['articlesother'] = predict_similar_articles(sameauthor,otherauthor,weights)
        if 'Predict' in request.form:
            return redirect('/output')
        elif 'Similar' in request.form:
            return redirect('/similar')
        else:
            raise ValueError('Bad request')

def author_to_names(author):
    firstname, lastname = author.split()
    if firstname == 'None' and lastname == 'None':
        firstname, lastname = None, None
    return firstname, lastname
    
@app.route('/output', methods = ['GET','POST'])
def oped_output():
    if request.method == 'GET':
        return render_template('output.html', expectedshares=app.var['expectedshares'], percsame = app.var['percsame'], percother = app.var['percother'])
    
@app.route('/similar', methods  = ['GET', 'POST'])
def similar_opeds():
    if request.method == 'GET':
        table_same = df_to_tabledict(app.var['articlessame'])
        table_other = df_to_tabledict(app.var['articlesother'])
        return render_template('similar.html', same=table_same, other=table_other)
    
def df_to_tabledict(df):
    res = []
    for i, row in enumerate(df.iterrows()):
        rowdata = row[1]
        firstname = rowdata['first_name']
        lastname = rowdata['last_name']
        if firstname is None:
            firstname = ''
        if lastname is None:
            lastname = 'The Editorial Board'            
        res.append({'index': i + 1,
                    'url': rowdata['url'],
                    'title': rowdata['Title'].decode('utf-8'),
                    'first_name': firstname,
                    'last_name': lastname,
                    'sharecount': rowdata['share_count']})
    return res

@app.route('/d32', methods = ['GET', 'POST'])
def d32():
    return render_template('sample10_d3.html')

@app.route('/input2')
def input2():
    return render_template('input2.html')

@app.route('/d3', methods = ['GET', 'POST'])
def d3():
    return render_template('sample11_d3.html')