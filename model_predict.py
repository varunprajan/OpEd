import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn import linear_model, neighbors, ensemble, preprocessing
import os
import pickleizer
import math
import text_processing
import nytimes_crawl as nytc

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

LDA, TF = pickleizer.load_topic_analyzer(pickleizer.SUBDIR)
MODEL = pickleizer.load_model(pickleizer.SUBDIR)
AUTHORID = pickleizer.load_author(pickleizer.SUBDIR)

def feature_names():
    N_AUTHORS = len(AUTHORID)
    N_DAYS = 7
    N_TOPICS = LDA.components_.shape[0]
    topicnames = ['topic{0}'.format(i) for i in range(N_TOPICS)]
    authornames = ['author{0}'.format(i) for i in range(N_AUTHORS)]
    daynames = ['Day{0}'.format(i) for i in range(n_days)]
    return topicnames + authornames + daynames

def predict_new_article_url(firstname,lastname,dayofweek,url):
    fulltext = nytc.url_full_text(url)
    return predict_new_article_text(firstname,lastname,dayofweek,fulltext)

def predict_new_article_text(firstname,lastname,dayofweek,text,fac=100):
    tidiedtext = text_processing.tidy_text_and_join(text)
    weights = article_topic_weights(tidiedtext,LDA,TF)
    author = author_num(firstname,lastname,AUTHORID)
    days = day_of_week(dayofweek)
    feature = np.append(weights,author)
    feature = np.append(feature,days)
    logres = MODEL.predict([feature])[0]
    return int(round(10**logres/fac)*fac)
    
def article_topic_weights(tidiedtext,lda,tf_vectorizer):
    document_term_matrix = tf_vectorizer.transform([tidiedtext])
    weights = lda.transform(document_term_matrix)
    return weights/np.sum(weights)

def day_of_week(day,ndays=7):
    days = np.zeros((ndays,1))
    days[day] = 1
    return days

def author_num(firstname,lastname,authorid):
    if firstname is None:
        firstname = float('nan')
    if lastname is None:
        lastname = float('nan')
    nauthors = len(authorid) + 1
    idauth = authorid.get((firstname,lastname),0)
    auth = np.zeros((nauthors,1))
    auth[idauth] = 1
    return auth
