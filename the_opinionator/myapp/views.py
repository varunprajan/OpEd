from flask import render_template, request, redirect, Markup
from myapp import app
import pandas as pd
from model_predict import predict_new_article_text_sub, article_weights, get_recommendations, AUTHORENCODER, DAYSOFWEEK
from similar_articles import predict_similar_articles, same_other_df, percentiles
import queries
import copy
import numpy as np
import markdown

app.var = {}

SAMPLETEXT = u'In general, you shouldn\u2019t pay much attention to polls at this point, especially with Republicans unifying around Donald Trump while Bernie Sanders hasn\u2019t conceded the inevitable. Still, I was struck by several recent polls showing Mr. Trump favored over Hillary Clinton on the question of who can best manage the economy.'

@app.route('/')
@app.route('/input', methods = ['GET', 'POST'])
def oped_input():
    if request.method == 'GET':
        if 'Stuck' in request.args.keys():
            poptext = SAMPLETEXT
            print('Yay')
        else:
            poptext = ''
        print(poptext)
        return render_template("input3.html", authorid = AUTHORENCODER.tokentoid, daysofweek = DAYSOFWEEK, poptext = poptext)
    elif request.method == 'POST':
        # app.var['fulltext'] = request.args.get('full_text')
        # app.var['author'] = request.args.get('author')
        # app.var['day'] = int(request.args.get('day'))
        fulltext = request.form['full_text']
        author = request.form['author']
        app.var['author'] = author
        day = int(request.form['day']) - 1
        weights = article_weights(fulltext)
        df = queries.return_df(queries.all_query())
        samedf, otherdf = same_other_df(df,author)
        expectedshares = predict_new_article_text_sub(author,day,weights)
        percsame, percother = percentiles(samedf,otherdf,expectedshares)
        recommendations = get_recommendations(author,day,weights,df)
        app.var['percsame'], app.var['percother'] = int(percsame*100)/100, int(percother*100)/100
        app.var['expectedshares'] = expectedshares
        app.var['articlessame'], app.var['articlesother'] = predict_similar_articles(samedf,otherdf,weights)
        app.var['recommendations'] = recommendations
        if 'Predict' in request.form:
            return redirect('/output')
        elif 'Similar' in request.form:
            return redirect('/similar')
        else:
            raise ValueError('Bad request')
    
@app.route('/output', methods = ['GET','POST'])
def oped_output():
    if request.method == 'GET':
        recommendations = [Markup(markdown.markdown(content)) for content in app.var['recommendations']]
        return render_template('output.html', expectedshares=app.var['expectedshares'], percsame = app.var['percsame'], percother = app.var['percother'], recommendations = recommendations, authorname=app.var['author'])
    
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
        title = rowdata['title']
        if type(title) == str:
            title = title.decode('utf-8')
        res.append({'index': i + 1,
                    'url': rowdata['url'],
                    'title': title,
                    'author': rowdata['author'],
                    'sharecount': rowdata['share_count']})
    return res

@app.route('/d33', methods = ['GET', 'POST'])
def d32():
    return render_template('sample10_d3.html')

@app.route('/d32', methods = ['GET', 'POST'])
def d33():
    return render_template('sample14_d3.html')

@app.route('/d3', methods = ['GET', 'POST'])
def d34():
    return render_template('sample17_d3.html')

@app.route('/d34', methods = ['GET', 'POST'])
def d3():
    return render_template('sample11_d3.html')
