import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn import linear_model, neighbors, ensemble, preprocessing
import os
import pickleizer
import text_processing
import nytimes_crawl_2 as nytc
import encoder
from scipy.stats import percentileofscore
import random

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

LDA, TF = pickleizer.load_topic_analyzer(pickleizer.SUBDIR)
MODEL, FEATURENAMES = pickleizer.load_model(pickleizer.SUBDIR)
DAYENCODER, AUTHORENCODER = pickleizer.load_encoders(pickleizer.SUBDIR)
DAYSOFWEEK = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

def predict_new_article_text(author,dayofweek,text,fac=100):
    weights = article_weights(text)
    return predict_new_article_text_sub(author,dayofweek,weights,fac)
    
def article_weights(text):
    tidiedtext = text_processing.tidy_text_and_join(text)
    return article_topic_weights(tidiedtext,LDA,TF)
    
def predict_new_article_text_sub(author,dayofweek,weights,fac=100):
    author = AUTHORENCODER.encode([author])
    day = DAYENCODER.encode([dayofweek])
    feature = np.append(day,author)
    feature = np.append(feature,weights)
    logres = MODEL.predict([feature])[0]
    return int(round(10**logres/fac)*fac)
    
def article_topic_weights(tidiedtext,lda,tf_vectorizer):
    document_term_matrix = tf_vectorizer.transform([tidiedtext])
    weights = lda.transform(document_term_matrix)
    return weights/np.sum(weights)

def get_recommendations(author,dayofweek,weights,df):
    topicnames = [fname for fname in FEATURENAMES if fname.startswith('topic')]
    weightsall = df[topicnames]
    weightscoeff = np.array(get_relevant_coeff('topic'))
    score = np.dot(weightsall,weightscoeff)
    scorecurr = np.dot(weights,weightscoeff)
    perctopic = percentileofscore(score,scorecurr)
    messagetopic = clever_message_topic(perctopic)
    percauthor, topauthors = encoder_rank(AUTHORENCODER,author,num=3)
    messageauthor = clever_message_author(AUTHORENCODER,percauthor,topauthors)
    percday, topdayidx = encoder_rank(DAYENCODER,dayofweek)
    topday = DAYSOFWEEK[topdayidx[0]]
    messageday = clever_message_day(DAYENCODER,percday,topday)
    return [messagetopic, messageauthor, messageday]    
    
def encoder_rank(encoder,token,num=1):
    name = encoder.name
    encodercoeffall = []
    idx = encoder.get_token_id(token)
    encodercoeffall = get_relevant_coeff(encoder.name)
    encodercoeff = encodercoeffall[idx]
    perc = percentileofscore(encodercoeffall,encodercoeff)
    topperformersidx = np.argsort(np.array(encodercoeffall))[::-1]
    topperformers = [encoder.idtotoken[idx] for idx in topperformersidx[:num]]
    return perc, topperformers

def get_relevant_coeff(name):
    return [coeff for coeff, fname in zip(MODEL.coef_,FEATURENAMES) if fname.startswith(name)]

def clever_message_day(encoder,perc,topperformer,cutoff=75):
    heading = '**Day**:'
    message1 = perc_message(perc)
    if perc < cutoff:
        message2 = 'May I suggest a different day of the week? Perhaps {0}.'.format(topperformer)
    else:
        message2 = random.choice(['Outstanding choice!','You chose well. Bravo!','Well played!'])
    return '{2} {0} ({1})'.format(message2,message1,heading)

def clever_message_author(encoder,perc,topperformers,cutoff=75):
    heading = '**Author**:'
    message1 =  perc_message(perc)
    if perc < cutoff:
        message2 = 'You could stand to be more interesting, like {0}.'.format(random.choice(topperformers))
    else:
        message2 = random.choice(['Outstanding choice!','You chose well. Bravo!','Well played!'])
    return '{2} {0} ({1})'.format(message2,message1,heading)

def clever_message_topic(perc,cutoff=75):
    heading = '**Topic**:'
    message1 = perc_message(perc)
    if perc < cutoff:
        message2 = 'May I suggest writing about something more interesting?'
    else:
        message2 = 'I see some potential here!'
    return '{2} {0} ({1})'.format(message2,message1,heading)

def perc_message(perc):
    return 'Percentile **{0:.0f}**'.format(perc)

        
    







