import os
import pickle
import nltk
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn import linear_model, neighbors, ensemble, preprocessing

LDANAME = 'lda'
TFNAME = 'tf'
MODELNAME = 'model'
AUTHORIDNAME = 'authorid'
SUBDIR = ''

def save_topic_analyzer(lda,tf_vectorizer,subdir=''):
    pickle_save(lda,LDANAME,subdir)
    pickle_save(tf_vectorizer,TFNAME,subdir)

def load_topic_analyzer(subdir=''):
    lda = pickle_load(LDANAME,subdir)
    tf = pickle_load(TFNAME,subdir)
    return lda, tf
    
def save_model(model,subdir=''):
    pickle_save(model,MODELNAME,subdir)
    
def load_model(subdir=''):
    return pickle_load(MODELNAME)
    
def save_author(authorid,subdir=''):
    pickle_save(authorid,AUTHORIDNAME,subdir)
    
def load_author(subdir=''):
    return pickle_load(AUTHORIDNAME,subdir)

def pickle_save(obj,filepref,subdir=''):
    filepath = pickle_path(filepref,subdir)
    pickle.dump(obj, open(filepath,'wb'))
    
def pickle_load(filepref,subdir=''):
    filepath = pickle_path(filepref,subdir)
    return pickle.load(open(filepath,'rb'))

def pickle_path(filepref,subdir='',suffix='.p'):
    filename = filepref + suffix
    return os.path.join(subdir,filename)