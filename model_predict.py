import numpy as np
import pandas as pd
import nltk
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn import linear_model, neighbors, ensemble, preprocessing
import unicodedata
import sys
import os
import pickleizer
import nytimes_crawl_2 as nytc
import math

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

PUNCTTBL = dict.fromkeys(i for i in xrange(sys.maxunicode)
                      if unicodedata.category(unichr(i)).startswith('P'))

LDA, TF = pickleizer.load_topic_analyzer(pickleizer.SUBDIR)
MODEL = pickleizer.load_model(pickleizer.SUBDIR)
AUTHORID = pickleizer.load_author(pickleizer.SUBDIR)
N_AUTHORS = len(AUTHORID)
N_DAYS = 7
N_TOPICS = LDA.components_.shape[0]

def feature_names():
    topicnames = ['topic{0}'.format(i) for i in range(N_TOPICS)]
    authornames = ['author{0}'.format(i) for i in range(N_AUTHORS)]
    daynames = ['Day{0}'.format(i) for i in range(n_days)]
    return topicnames + authornames + daynames

def predict_new_article_url(firstname,lastname,dayofweek,url):
    fulltext = nytc.url_full_text(url)
    return predict_new_article_text(firstname,lastname,dayofweek,fulltext)

def predict_new_article_text(firstname,lastname,dayofweek,text,fac=100):
    tidiedtext = tidy_text_and_join(text)
    weights = article_topic_weights(tidiedtext,LDA,TF)
    author = author_num(firstname,lastname,AUTHORID)
    days = day_of_week(dayofweek)
    feature = np.append(weights,author)
    feature = np.append(feature,days)
    logres = MODEL.predict([feature])[0]
    return int(round(10**logres/fac)*fac)

def remove_punctuation(text):
    return text.translate(PUNCTTBL)

def tidy_text(text):
    """ Does the following: 1. Removes punctuation 2. Tokenises words 3. Removes stop words 4. Puts words through the snowball stemmer"""

    text = remove_punctuation(text)
    stemmer = nltk.stem.snowball.EnglishStemmer()
    stopwords = set(nltk.corpus.stopwords.words('english'))

    outwords = []
    for word in text.split():
        word = word.lower()
        if word not in stopwords:
            if len(word) > 0:
                if not word[0].isdigit():
                    outwords.append(stemmer.stem(word))
    return outwords

def tidy_text_and_join(text):
    tidytext = tidy_text(text)
    return ' '.join(tidytext)
    
def article_topic_weights(tidiedtext,lda,tf_vectorizer):
    document_term_matrix = tf_vectorizer.transform([tidiedtext])
    weights = lda.transform(document_term_matrix)
    weights /= np.sum(weights)
    return weights

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




