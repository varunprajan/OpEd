import urllib2
from bs4 import BeautifulSoup
import re
import nytimesarticle as nyta
import urllib2
import requests
import csv
import time
import pandas as pd
import numpy as np
from nytimesarticle import articleAPI

apikey = '56d7a05e3e8641c5baadd1b21b58ec05'
api = articleAPI(apikey)

def article_info(article):
    url = article['web_url']
    print(url)
    res = url_counts(url) # dependent variable ('hype')
    res['first_name'], res['last_name'] = article_columnists(article) 
    res['document_type'] = article['document_type']
    res['full_text'] = url_full_text(url)
    res['url'] = url
    return res

def article_keywords(article):
    def keywords():
        for keyword in article['keywords']:
            yield keyword['value'].lower()
    return list(keywords())
    
def article_columnists(article):
    try:
        person = article['byline']['person'][0]
        firstname = person.get('firstname',np.nan)
        lastname = person.get('lastname',np.nan)
    except IndexError:
        firstname, lastname = np.nan, np.nan
    def lower_except_nan(mystr):
        try:
            return mystr.lower()
        except AttributeError:
            return mystr
    return lower_except_nan(firstname), lower_except_nan(lastname)

def url_full_text(url):
    soup = soupify_url(url)
    return ' '.join(yield_par_from_soup(soup))
    
def yield_par_from_soup(soup,classtag='story-body-text story-content'):
    paragraphs = soup.findAll('p',{'class':classtag})
    for par in paragraphs:
        yield par.get_text()
        
def soupify_url(url):
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    response = opener.open(url)
    return BeautifulSoup(response.read(),'lxml')
    
def url_counts(url):
    apiurl = 'http://api.facebook.com/restserver.php?method=links.getStats&urls={0}'.format(url)
    r = requests.get(apiurl)
    soup = BeautifulSoup(r.text,'xml')
    def yield_count():
        for attr in ['share_count','like_count','comment_count']:
            taggedinfo = getattr(soup,attr)
            yield attr, taggedinfo.contents[0]
    return dict(yield_count())

class OpEdReader(object):
    def __init__(self,name,urls=None,columns=None):
	self.name = name
        if urls is None:
            self.urls = set()
        if columns is None:
            columns = ['first_name','last_name','comment_count','document_type',
                       'full_text','like_count','share_count','url']
        self.data = pd.DataFrame(columns=columns) # blank
        
    @classmethod
    def init_from_file(cls,name,csvfile):
        self = cls(name)
        self.data = pd.read_csv(csvfile,index_col=0)
        self.urls = set(self.data['url'])
        return self
    
    def save_oped_articles_all_pages(self,begindate,enddate=None,author=None,maxpages=101,pagestart=0):
        for page in range(pagestart,maxpages):
            if page%5 == 0 and page != 0:
                self.save_to_csv('{1}{0}.csv'.format(page,self.name))
            print(page)
            articles = self.current_articles_one_page(page,begindate,enddate=enddate,author=author)
            if articles:
                self.save_oped_articles(articles)
            else:
                return
            
    def save_oped_articles_one_page(self,page,begindate,enddate=None,author=None,sleeptime=2):
        articles = self.current_articles_one_page(page,begindate,enddate=enddate,author=author)
        self.save_oped_articles(articles,sleeptime)
        
    def save_oped_articles(self,articles,sleeptime=2,wordcutoff=30):
        for i, article in enumerate(articles):
            self.save_oped_article(article)
            time.sleep(sleeptime)
            
    def save_oped_article(self,article,wordcutoff=30):
        wordcount = int(article['word_count'])
        if wordcount > wordcutoff:
            articletype = article['type_of_material']
            try:
                articleinfo = article_info(article)
		if articleinfo['url'] not in self.urls:
                	newdf = pd.DataFrame([articleinfo])
                	self.data = self.data.append(newdf)
            except:
                print('Fail')
                print(article['web_url'])
            
    
    def current_articles_one_page(self,page,begindate,enddate=None,author=None):
        fq = {'news_desk.contains':['OpEd','Editorial'],'document_type':'article',
              'type_of_material.contains':['Op-Ed','OpEd','Editorial']}
        if author is not None:
            fq['byline'] = author
        if enddate is None:
            articles = api.search(fq=fq,begin_date=begindate,page=page)
        else:
            articles = api.search(fq=fq,begin_date=begindate,end_date=enddate,page=page)
        return articles['response']['docs']
    
    def save_to_csv(self,csvfile):
        self.data.to_csv(csvfile,encoding='utf-8')

