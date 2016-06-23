import unicodedata
import sys
import nltk

PUNCTTBL = dict.fromkeys(i for i in xrange(sys.maxunicode)
                      if unicodedata.category(unichr(i)).startswith('P'))
stemmer = nltk.stem.snowball.EnglishStemmer()
lemmatizer = nltk.stem.WordNetLemmatizer()
stopwords = set(nltk.corpus.stopwords.words('english'))

def remove_punctuation(text):
    return text.translate(PUNCTTBL)

def tidy_text(text,wordoption='stem'):
    """ Does the following: 1. Removes punctuation 2. Tokenises words 3. Removes stop words 4. Puts words through the stemmer/lemmatizer"""

    text = remove_punctuation(text)
    stopwords.add('mr') # NYT!

    outwords = []
    for word in text.split():
        word = word.lower()
        if word not in stopwords:
            if len(word) > 0:
                if not word[0].isdigit():
                    if wordoption == 'stem':
                        newword = stemmer.stem(word)
                    elif wordoption == 'lemma':
                        newword = lemmatizer.lemmatize(word)
                    else:
                        newword = word
                    outwords.append(newword)
    return outwords

def tidy_text_and_join(text,option='all'):
    if option == 'all':
        tidytext = tidy_text(text)
    elif option == 'nounadj':
        tidytext = tidy_text_noun_adj(text)
    return ' '.join(tidytext)

def tidy_text_noun_adj(text,wordoption='lemma'):
    tokentext = nltk.word_tokenize(text)
    taggedwords = nltk.pos_tag(tokentext)
    outwords = []
    for taggedword in taggedwords:
        if taggedword[1].startswith('NN') or taggedword[1].startswith('JJ'):
            word = taggedword[0].lower()
            if word not in stopwords:
                if len(word) > 0:
                    if wordoption == 'stem':
                        newword = stemmer.stem(word)
                    elif wordoption == 'lemma':
                        newword = lemmatizer.lemmatize(word)
                    else:
                        newword = word
                    outwords.append(newword)
    return outwords

                
                
                
