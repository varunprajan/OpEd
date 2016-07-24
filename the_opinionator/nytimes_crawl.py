import urllib2
from bs4 import BeautifulSoup
import nytimesarticle as nyta
import requests
import time
import pandas as pd
import numpy as np
from nytimesarticle import articleAPI
from datetime import datetime
from dateutil.relativedelta import relativedelta
import yaml

with open('config.yml', 'r') as f:
    doc = yaml.load(f)
    apikey = doc['NYTIMESAPIKEY']
    api = articleAPI(apikey)

def read_all(names,enddate,begindate='19500101',datefmt='%Y%m%d'): # begindate is a really early date
    for name in names:
        reader = OpEdReader(name)
        reader.save_oped_articles_all_pages(begindate,enddate)
        enddate = reader.data['date'].iloc[-1]
    
def query_articles_one_page(page,begindate,enddate=None,author=None):
    """Returns one page of NYT opinions, from begindate to enddate. Optionally takes a specific author"""
    fq = {'news_desk.contains':['OpEd','Editorial'],'document_type':'article',
          'type_of_material.contains':['Op-Ed','OpEd','Editorial']}
    if author is not None:
        fq['byline'] = author
    kwargs = {} if enddate is None else {'end_date' : enddate}
    articles = api.search(fq=fq,begin_date=begindate,page=page,**kwargs)
    return articles['response']['docs']

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

def lower_not_none(mystr):
    return mystr.lower() if mystr is not None else mystr

def author_name(firstname,lastname,unsignedname='The Editorial Board',othername='Other'):
    if pd.isnull(firstname) and pd.isnull(lastname):
        return unsignedname
    else:
        try:
            return '{0} {1}'.format(firstname.title(),lastname.title())
        except:
            return othername

class NYTArticle(object):
    def __init__(self,article):
        self.article = article
        self.url = article['web_url']
        self.soup = soupify_url(self.url)
        self.title = self.get_title()
        self.document_type = article['document_type']
        self.date = self.date_from_url()
        self.first_name, self.last_name = self.author_names()
        self.full_text = self.url_full_text()
        counts = url_counts(self.url)
        self.share_count, self.like_count, self.comment_count = counts['share_count'], counts['like_count'], counts['comment_count']        
    
    def get_title(self,titlenum=21):
        return self.soup.find('title').contents[0][:-titlenum]
    
    def date_from_url(self,searchstr='.com/',strlen=10):
        """Determines the date the article was published by parsing the url (which contains the date)"""
        n = len(searchstr)
        idx = self.url.find(searchstr)
        finalstr = self.url[idx+n:idx+n+strlen]
        return datetime.strptime(finalstr,'%Y/%m/%d')
    
    def author_names(self):
        firstname, lastname = self.author_name_from_article()
        if (firstname is None and lastname is not None) or (firstname is not None and lastname is None): # bad name
            firstname, lastname = self.author_name_from_soup()
        return lower_not_none(firstname), lower_not_none(lastname)
        
    def author_name_from_soup(self):
        tag = self.soup.findAll('meta',{'name':'author'})[0]
        namewords = tag.get('content').split()
        firstname, lastname = namewords[0], namewords[-1]
        return firstname, lastname
    
    def author_name_from_article(self):
        byline = self.article['byline']
        noname = False
        if byline:
            try:
                person = byline['person'][0]
                firstname = person.get('firstname',None)
                lastname = person.get('lastname',None)
            except IndexError:
                firstname, lastname = None, None
        else:
            firstname, lastname = None, None
        return firstname, lastname
            
    def url_full_text(self,classtag='story-body-text story-content'):
        def yield_par_from_soup():
            paragraphs = self.soup.findAll('p',{'class':classtag})
            for par in paragraphs:
                yield par.get_text()
        return ' '.join(yield_par_from_soup())

class OpEdReader(object):
    def __init__(self,name,urls=None,columns=None):
	self.name = name
        if urls is None:
            self.urls = set()
        if columns is None:
            columns = ['first_name','last_name','comment_count','document_type',
                       'full_text','like_count','share_count','url','date','title']
        self.data = pd.DataFrame(columns=columns) # blank
        
    @classmethod
    def init_from_file(cls,name,csvfile):
        obj = cls(name)
        obj.data = pd.read_csv(csvfile,index_col=0)
        obj.urls = set(obj.data['url'])
        return obj
    
    def csv_file_page(self,page):
        return '{0}_{1}.csv'.format(self.name,page)
    
    def save_oped_articles_all_pages(self,begindate,enddate=None,author=None,maxpages=101,pagestart=0,verbose=True):
        for page in range(pagestart,maxpages):
            if page%5 == 0 and page != 0: # in case we crash in the middle
                self.save_to_csv(self.csv_file_page(page))
            if verbose:
                print(page)
            articles = query_articles_one_page(page,begindate,enddate=enddate,author=author)
            if articles:
                self.save_oped_articles(articles)
            else:
                self.save_to_csv(self.csv_file_page(page))
                return
        
    def save_oped_articles(self,articles,sleeptime=2,wordcutoff=75):
        for article in articles:
            self.append_article_with_checks(article,wordcutoff=wordcutoff)
            time.sleep(sleeptime) # don't get banned!
            
    def append_article_with_checks(self,article,wordcutoff=75):
        wordcount = int(article['word_count'])
        url = article['web_url']
        if wordcount > wordcutoff and '/universal/' not in url: # eliminates too short and foreign language articles
            try:
                article = NYTArticle(article)
                if article.url not in self.urls:
                    self.append_article(article)
                    self.urls.add(article.url)
            except:
            	print('Fail')
                print(article['web_url'])
                
    def append_article(self,article):
        newdf = pd.DataFrame(columns = self.data.columns)
        for col in newdf.columns:
            newdf[col] = [getattr(article,col)]
        self.data = self.data.append(newdf)
    
    def save_to_csv(self,csvfile):
        self.data.to_csv(csvfile,encoding='utf-8')

    def drop_rows(self,indices):
        newdf = self.data.reset_index(drop=True)
        newdf = newdf.drop(indices)
        self.data = newdf
        
