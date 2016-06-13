from flask import render_template, request, redirect
from the_opinionator import app
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from a_Model import ModelIt
import pandas as pd
import psycopg2
from model_predict import AUTHORID, predict_new_article_text

user = 'varun' #add your username here (same as previous postgreSQL)                      
host = 'localhost'
dbname = 'birth_db'
db = create_engine('postgres://%s%s/%s'%(user,host,dbname))
con = None
con = psycopg2.connect(database = dbname, user = user)

app.var = {}

AUTHORID = pickleizer.load_author(pickleizer.SUBDIR)
DAYSOFWEEK = [

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html",
       title = 'Home', user = { 'nickname': 'Miguel' },
       )

@app.route('/input', methods = ['GET', 'POST'])
def oped_input():
    if request.method == 'GET':
        return render_template("input.html", authorid = AUTHORID, daysofweek = DAYSOFWEEK)
    elif request.method == 'POST':
        # app.var['fulltext'] = request.args.get('full_text')
        # app.var['author'] = request.args.get('author')
        # app.var['day'] = int(request.args.get('day'))
        app.var['fulltext'] = request.form['full_text']
        app.var['author'] = request.form['author']
        app.var['day'] = request.form['day']
        return redirect('/output')

@app.route('/output', methods = ['GET','POST'])
def oped_output():
    if request.method == 'GET':
        fulltext = app.var['fulltext']
        firstname, lastname = app.var['author'].split()
        day = app.var['day']
        if firstname == 'None' and lastname == 'None':
            firstname, lastname = None, None
        expectedshares = predict_new_article_text(firstname,lastname,day,fulltext)
        return render_template('output.html', expectedshares=expectedshares)