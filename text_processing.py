import unicodedata
import sys
import nltk

PUNCTTBL = dict.fromkeys(i for i in xrange(sys.maxunicode)
                      if unicodedata.category(unichr(i)).startswith('P'))

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