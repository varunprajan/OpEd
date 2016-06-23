import os
import pickle
import nltk
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn import linear_model, neighbors, ensemble, preprocessing
import encoder

LDANAME = 'lda'
TFNAME = 'tf'
MODELNAME = 'model'
FEATNAME = 'feat'
SUBDIR = ''
DAYENCNAME = 'dayenc'
AUTHORENCNAME = 'authorenc'

def save_encoders(dayencoder,authorencoder,subdir=SUBDIR):
    pickle_save(dayencoder,DAYENCNAME,subdir)
    pickle_save(authorencoder,AUTHORENCNAME,subdir)
    
def load_encoders(subdir=SUBDIR):
    dayencoder = pickle_load(DAYENCNAME,subdir)
    authorencoder = pickle_load(AUTHORENCNAME,subdir)
    return dayencoder, authorencoder

def save_topic_analyzer(lda,tf_vectorizer,subdir=SUBDIR):
    pickle_save(lda,LDANAME,subdir)
    pickle_save(tf_vectorizer,TFNAME,subdir)

def load_topic_analyzer(subdir=SUBDIR):
    lda = pickle_load(LDANAME,subdir)
    tf = pickle_load(TFNAME,subdir)
    return lda, tf
    
def save_model(model,featurenames,subdir=SUBDIR):
    pickle_save(model,MODELNAME,subdir)
    pickle_save(featurenames,FEATNAME,subdir)
    
def load_model(subdir=SUBDIR):
    model = pickle_load(MODELNAME,subdir)
    featurenames = pickle_load(FEATNAME,subdir)
    return model, featurenames

def pickle_save(obj,filepref,subdir=SUBDIR):
    filepath = pickle_path(filepref,subdir)
    pickle.dump(obj, open(filepath,'wb'))
    
def pickle_load(filepref,subdir=SUBDIR):
    filepath = pickle_path(filepref,subdir)
    return pickle.load(open(filepath,'rb'))

def pickle_path(filepref,subdir=SUBDIR,suffix='.p'):
    filename = filepref + suffix
    return os.path.join(subdir,filename)